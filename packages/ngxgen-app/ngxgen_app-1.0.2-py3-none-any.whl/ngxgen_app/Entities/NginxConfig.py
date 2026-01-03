#!/usr/bin/env python


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Some files in this repo may be shared as they are licensed under the
# MPL-2.0 license.  Those files bear the appropriate copyright notice
# within them, most likely in some of files' top lines.
#
# Copyright (c) 2024-2025, Maciej Barć <xgqt@xgqt.org>


ind = " " * 4


class NginxLimits:

    def __init__(self, config: dict, server_name: str):
        self.server_name: str = server_name

        self.client_rate: None | str = config.get("client_rate")
        self.total_rate: None | str = config.get("total_rate")
        self.conns: None | int = config.get("conns")

        self.client_rate_zone_name: str = f"{server_name}-client-rate"
        self.total_rate_zone_name: str = f"{server_name}-total-rate"
        self.conns_rate_zone_name: str = f"{server_name}-conns"


class NginxConfig:

    def __init__(self) -> None:
        self._location_block_data: dict = {}

    def _make_directive(self, ind_step: int, key: str, val: None | str = None) -> str:
        val_suffix: str = ""

        if val:
            val_suffix = f" {val}"

        return f"{ind * ind_step}{key}{val_suffix};\n"

    def _make_tld_limits_block(self, nginx_limits: NginxLimits) -> str:
        size: str = "16m"
        out: str = ""

        if nginx_limits.client_rate:
            out += self._make_directive(
                ind_step=0,
                key="limit_req_zone $binary_remote_addr",
                val=f"zone={nginx_limits.client_rate_zone_name}:{size} rate={nginx_limits.client_rate}",
            )

        if nginx_limits.total_rate:
            out += self._make_directive(
                ind_step=0,
                key='limit_req_zone ""',
                val=f"zone={nginx_limits.total_rate_zone_name}:{size} rate={nginx_limits.total_rate}",
            )

        if nginx_limits.conns:
            out += self._make_directive(
                ind_step=0,
                key="limit_conn_zone $server_name",
                val=f"zone={nginx_limits.conns_rate_zone_name}:{size}",
            )

        return out

    def _make_server_limits_block(self, nginx_limits: NginxLimits) -> str:
        out: str = ""

        if nginx_limits.client_rate:
            out += self._make_directive(
                ind_step=1,
                key="limit_req",
                val=f"zone={nginx_limits.client_rate_zone_name} burst=5 nodelay",
            )

        if nginx_limits.total_rate:
            out += self._make_directive(
                ind_step=1,
                key="limit_req",
                val=f"zone={nginx_limits.total_rate_zone_name} burst=50 nodelay",
            )

        if nginx_limits.client_rate or nginx_limits.total_rate:
            out += self._make_directive(
                ind_step=1,
                key="limit_conn",
                val=f"{nginx_limits.conns_rate_zone_name} {nginx_limits.conns}",
            )

        return out

    def _make_upstream_server(self, upstream_server: dict) -> str:
        host: str = upstream_server.get("host", "127.0.0.1").strip()
        port: None | int = upstream_server.get("port", None)

        port_prefix: str = ""

        if port:
            port_prefix = f":{port}"

        server_opts: list[str] = [
            f"{host}{port_prefix}",
            "max_fails=3",
            "fail_timeout=10s",
        ]

        out: str = ""

        out += self._make_directive(ind_step=1, key="server", val=" ".join(server_opts))

        return out

    def _make_upstream_block(self, config: dict) -> str:
        upstream_name: str = config.get("name", "unnamed_upstream").strip()
        upstream_servers: list = config.get("servers", [])

        if len(upstream_servers) == 0:
            raise RuntimeError(f"Upstream {upstream_name} has no servers configured")

        out: str = ""

        out += f"upstream {upstream_name}\n"
        out += "{\n"
        out += "\n"
        out += self._make_directive(ind_step=1, key="keepalive", val="32")
        out += self._make_directive(ind_step=1, key="least_conn")
        out += "\n"

        for upstream_server in upstream_servers:
            out += self._make_upstream_server(upstream_server)

        out += "\n"
        out += "}\n"
        out += "\n"

        return out

    def _update_location_settings(self, settings: dict) -> None:
        # Update "location_block_data" while also keeping the key order
        # defined in the "settings" dictionary above.
        #
        for key, value in settings.items():
            if key in self._location_block_data:
                old_val = self._location_block_data[key]

                del self._location_block_data[key]

                self._location_block_data[key] = old_val
            else:
                self._location_block_data[key] = value

    def _add_access_settings(self, access_settings: list) -> None:
        settings: dict = {}

        for access_setting in access_settings:

            # Guard if we receive a empty hash.
            if not access_setting:
                continue

            # Extract the 1st key-value pair and unpack it into values.
            key, val = next(iter(access_setting.items()))

            # Dirty hack.
            settings[f"{key} {val}"] = ""

        self._update_location_settings(settings)

    def _add_gzip(self) -> None:
        gzip_types: list[str] = [
            "application/javascript",
            "application/json",
            "application/wasm",
            "application/xml",
            "application/xml+rss",
            "image/svg+xml",
            "text/css",
            "text/javascript",
            "text/plain",
            "text/xml",
        ]

        settings: dict[str, str] = {
            "gzip": "on",
            "gzip_types": " ".join(gzip_types),
            "gzip_comp_level": "5",
            "gzip_min_length": "1000",
            "gzip_vary": "on",
        }

        self._update_location_settings(settings)

    def _add_relocation(self, relocation_target: str) -> None:
        settings: dict[str, str] = {
            "return": f"301 {relocation_target}",
        }

        self._update_location_settings(settings)

    def _add_file_index_settings(self, index_format: str) -> None:
        settings: dict[str, str] = {
            "index": "off",
            "expires": "off",
            "add_header Cache-Control": '"no-store, no-cache, must-revalidate, proxy-revalidate"',
            "autoindex": "on",
        }

        match index_format:
            case "html":
                settings.update(
                    {
                        "autoindex_format": "html",
                        "autoindex_exact_size": "off",
                        "autoindex_localtime": "on",
                    }
                )
            case "json":
                settings.update(
                    {
                        "autoindex_format": "json",
                        "autoindex_exact_size": "on",
                        "autoindex_localtime": "off",
                        "default_type": "application/json",
                    }
                )
            case _:
                pass

        self._update_location_settings(settings)

    def _add_proxy_settings(self) -> None:
        timeout: int = 90

        settings: dict[str, str] = {
            "proxy_redirect": "default",
            "proxy_buffering": "off",
            "proxy_request_buffering": "off",
            "sendfile": "off",
            #
            "proxy_set_header Host": "$host",
            "proxy_set_header Connection": "$http_connection",
            "proxy_set_header Upgrade": "$http_upgrade",
            "proxy_set_header X-Real-IP": "$remote_addr",
            "proxy_set_header X-Forwarded-Server": "$host",
            "proxy_set_header X-Forwarded-For": "$proxy_add_x_forwarded_for",
            "proxy_set_header X-Forwarded-Port": "$server_port",
            "proxy_set_header X-Forwarded-Proto": "$scheme",
            #
            "proxy_max_temp_file_size": "0",
            "client_max_body_size": "32m",
            "client_body_buffer_size": "128k",
            #
            "proxy_connect_timeout": f"{timeout}",
            "proxy_send_timeout": f"{timeout}",
            "proxy_read_timeout": f"{timeout}",
        }

        self._update_location_settings(settings)

    def _make_location_block(self, config: dict) -> str:
        location_name: str = config.get("name", "/").strip()

        access_settings: list = config.get("access", [])

        is_gzip: bool = config.get("gzip", False)
        relocation_target: None | str = config.get("relocate", None)

        is_file_index: bool = config.get("file_index", False)
        index_format: str = config.get("index_format", "http").strip()

        is_proxy: bool = config.get("proxy", False)
        proxy_proto: str = config.get("proxy_proto", "http").strip()
        proxy_host: str = config.get("proxy_host", "").strip()
        proxy_port: None | int = config.get("proxy_port", None)
        proxy_path: str = config.get("proxy_path", "/").strip()

        self._location_block_data = config.get("block", {})

        if access_settings:
            self._add_access_settings(access_settings)

        if is_gzip:
            self._add_gzip()

        if relocation_target:
            self._add_relocation(relocation_target)

        if is_proxy:
            proxy_port_prefix: str = ""

            if proxy_port:
                proxy_port_prefix = f":{proxy_port}"

            proxy_pass_to: str = f"{proxy_proto}://{proxy_host}{proxy_port_prefix}{proxy_path}"
            self._location_block_data["proxy_pass"] = proxy_pass_to

            self._add_proxy_settings()

        if is_file_index:
            self._add_file_index_settings(index_format)

        out: str = ""

        out += f"{ind}location {location_name}\n"
        out += f"{ind}{{\n"

        for block_key, block_value in self._location_block_data.items():
            out += self._make_directive(ind_step=2, key=block_key, val=block_value)

        out += f"{ind}}}\n"
        out += "\n"

        return out

    def make_nginx_config(self, config_data) -> str:
        config_name: str = config_data["name"]

        config_listen: str = config_data.get("listen", "80").strip()
        config_logdir: str = config_data.get("logdir", "/var/log/nginx").strip()

        config_limits: dict = config_data.get("limits", {})
        config_upstreams: list = config_data.get("upstreams", [])
        config_includes: list = config_data.get("include", [])
        config_locations: list = config_data.get("locations", [])

        base_log_file_path: str = f"{config_logdir}/{config_name}.{config_listen}"

        out: str = ""
        nginx_limits: None | NginxLimits = None

        if config_limits:
            nginx_limits = NginxLimits(
                config=config_limits,
                server_name=config_name,
            )

            out += self._make_tld_limits_block(nginx_limits=nginx_limits)
            out += "\n"

        for config_upstream in config_upstreams:
            out += self._make_upstream_block(config=config_upstream)

        out += "server\n"
        out += "{\n"
        out += "\n"

        out += self._make_directive(1, "server_name", config_name)
        out += self._make_directive(1, "listen", config_listen)
        out += self._make_directive(1, "listen", f"[::]:{config_listen}")
        out += "\n"

        out += self._make_directive(1, "access_log", f"{base_log_file_path}.access.log main")
        out += self._make_directive(1, "error_log", f"{base_log_file_path}.error.log info")
        out += "\n"

        if config_limits and nginx_limits:
            out += self._make_server_limits_block(nginx_limits=nginx_limits)
            out += "\n"

        for config_include in config_includes:
            out += self._make_directive(1, "include", f"/etc/nginx/{config_include}")

        if len(config_includes) > 0:
            out += "\n"

        for config_location in config_locations:
            out += self._make_location_block(config=config_location)

        out += "}"

        return out

#!/usr/bin/env python


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2024-2025, Maciej Barć <xgqt@xgqt.org>


"""
App runner.
"""


import yaml

from ..Builder.CliBuilder import CliBuilder
from ..Entities.NginxConfig import NginxConfig


def read_config(yaml_file: str):
    with open(file=yaml_file, encoding="utf-8") as f:
        return yaml.safe_load(stream=f)


class AppRunner:

    def __init__(self) -> None:
        self.args = CliBuilder().add_arguments().parse().get_args()

    def run(self) -> None:
        data = read_config(self.args.input_config_yaml)

        nginx_config = NginxConfig()
        config_str = nginx_config.make_nginx_config(data)

        print(config_str)

#!/usr/bin/env python


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2024-2025, Maciej Barć <xgqt@xgqt.org>


import argparse

from typing import Self

from .. import __app__
from .. import __description__
from .. import __version__


class CliBuilder:
    """
    CLI builder.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._parser: argparse.ArgumentParser = argparse.ArgumentParser(
            prog=__app__,
            description=f"{__app__}, version {__version__}. {__description__}.",
        )
        self.__args: argparse.Namespace | None = None

        self._parser.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"{__version__}",
        )

    def add_arguments(self) -> Self:
        self._parser.add_argument(
            "input_config_yaml",
            help="input config.yaml file to use",
            type=str,
        )

        return self

    def parse(self) -> Self:
        self.__args = self._parser.parse_args()

        return self

    def get_args(self) -> argparse.Namespace:
        if not self.__args:
            raise RuntimeError("Arguments are not yet parsed")

        return self.__args

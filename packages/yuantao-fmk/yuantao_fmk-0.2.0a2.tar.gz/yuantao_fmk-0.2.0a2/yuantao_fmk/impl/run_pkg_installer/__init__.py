# Copyright (C) 2025 Tao Yuan
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

"""PkgBase基类包"""

import json
import os
import stat
from abc import abstractmethod
from typing import Dict, List, Optional

from hdfs import InsecureClient

from yuantao_fmk import Config, logger
from yuantao_fmk.downloader import (
    Downloader,
    HdfsDownloader,
    RequestsDownloader,
)
from yuantao_fmk.resource_installer import InstallerBase

class RunPkgInstaller(InstallerBase):
    def __init__(
        self,
        version: str,
        pkg_types_necessary: List[str],
        os_: str = Config.OS,
        arch: str = Config.ARCH,
    ):
        super().__init__(version, "run_package", pkg_types_necessary)
        self.os = os_
        self.arch = arch

    def pre_install(self, resource_tag, target_path):
        package_path = self.get_resource_local_url(resource_tag)
        if not os.access(package_path, os.X_OK) and package_path.endswith(".run"):
            current_stat = os.stat(package_path)
            os.chmod(package_path, current_stat.st_mode | stat.S_IEXEC)

    @abstractmethod
    def get_activation_commands(self, target_path: str) -> List[str]:
        pass

    def post_install_all(self, target_path):
        assert target_path is not None
        activation_commands = self.get_activation_commands(target_path)
        with open(
            os.path.join(target_path, "set_env.sh"), mode="w+", encoding="utf-8"
        ) as activation_file:
            activation_file.write("\n".join(activation_commands))
        logger.info(
            f"Install success! Run `source {target_path}/set_env.sh` to activate run package."
        )

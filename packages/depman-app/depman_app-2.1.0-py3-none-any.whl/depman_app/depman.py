#!/usr/bin/env python


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2024-2025, Maciej Barć <xgqt@xgqt.org>


"""
DepMan - micro, single-file general-purpose version manager.
"""


import argparse
import json
import os
import shutil
import subprocess

from dataclasses import dataclass
from hashlib import md5, sha1, sha256, sha512
from typing import Callable, List, Optional, Union
from xml.etree import ElementTree


TString = Optional[str]

TCallableCommand = Callable[[], None]

TListCommand = List[List[str]]

TCommand = Union[TCallableCommand, TListCommand, None]


@dataclass
class StaticDefs:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def __new__(cls, *args, **kwargs):
        pass

    app_name = "DepMan"

    app_version = "2.1.0"

    hash_methods = {
        "md5": md5,
        "sha1": sha1,
        "sha256": sha256,
        "sha512": sha512,
    }


class GenericUtils:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def __new__(cls, *args, **kwargs):
        pass

    @staticmethod
    def segmentize(a_string, separator) -> List[str]:
        return a_string.strip(separator).split(separator)


class ChecksumUtils:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def __new__(cls, *args, **kwargs):
        pass

    @staticmethod
    def getFileSum(sum_type, file_path) -> str:
        hash_method = StaticDefs.hash_methods[sum_type]
        a_hash = hash_method()

        with open(file_path, "rb") as a_file:
            for byte_block in iter(lambda: a_file.read(4096), b""):
                a_hash.update(byte_block)

        return a_hash.hexdigest()

    @staticmethod
    def checkFileSum(sum_type, expected_hash, file_path) -> None:
        hash_sum = ChecksumUtils.getFileSum(sum_type, file_path)

        if hash_sum == expected_hash:
            print(f" File {file_path} passed verification")
        else:
            raise RuntimeError(
                f"Checksum of a file {file_path} did not match, "
                + f"wanted: {expected_hash} but got: {hash_sum}"
            )


class Checksum:
    def __init__(self, *args, **kwargs) -> None:
        self.sum_type: TString = None
        self.sum_value: TString = None

    def setSumType(self, sum_type: str):
        if sum_type not in StaticDefs.hash_methods:
            raise RuntimeError(f"Checksum not supported, given: {sum_type}")

        self.sum_type = sum_type

        return self

    def setSumValue(self, sum_value: str):
        self.sum_value = sum_value

        return self

    def build(self):
        if not self.sum_type:
            raise RuntimeError("No checksum type given")

        if not self.sum_value:
            raise RuntimeError("No checksum value given")

        return self


class Src:
    def __init__(self, *args, **kwargs) -> None:
        self.src_uri: TString = None
        self.checksum: Optional[Checksum] = None

        self._out_file: TString = None

    def setSrcUri(self, src_uri: str):
        self.src_uri = src_uri

        return self

    def setChecksum(self, checksum: Checksum):
        self.checksum = checksum

        return self

    def build(self):  # abstract base
        if not self.src_uri:
            raise RuntimeError("No src uri given")

        self._out_file = GenericUtils.segmentize(self.src_uri, "/")[-1]

        return self

    def getOutFile(self) -> str:
        if not self._out_file:
            raise TypeError("_out_file is not set")

        return self._out_file

    def getDownloadCommand(self) -> TCommand:  # abstract
        pass

    def getVerifyCommand(self) -> TCommand:  # abstract
        pass

    def getExtractionCommand(self) -> TCommand:  # abstract
        pass


class FileSrc(Src):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def getDownloadCommand(self) -> TListCommand:
        if not self.src_uri:
            raise TypeError("src_uri is not set")

        if not self._out_file:
            raise TypeError("_out_file is not set")

        return [["curl", "-L", "-f", self.src_uri, "-o", self._out_file]]

    def getVerifyCommand(self) -> TCommand:
        if (checksum := self.checksum) is not None:
            if checksum.sum_value and checksum.sum_type:
                sum_type = checksum.sum_type
                sum_value = checksum.sum_value

                return lambda: ChecksumUtils.checkFileSum(sum_type, sum_value, self.getOutFile())

        return None


class TarSrc(FileSrc):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def getExtractionCommand(self) -> TListCommand:
        if not self._out_file:
            raise TypeError("_out_file is not set")

        return [
            ["bsdtar", "xf", self._out_file],
            ["rm", self._out_file],
        ]


class GitSrc(Src):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.git_branch: TString = None
        self.git_commit: TString = "LATEST"

    def setGitBranch(self, git_branch):
        self.git_branch = git_branch

        return self

    def build(self):
        if self.checksum:
            print(f"Checksum is set but this is a git repo, {self.src_uri}")
            print(f"Checksum {self.checksum} will be ignored")

        return super().build()

    def getDownloadCommand(self) -> TListCommand:
        if not self.src_uri:
            raise TypeError("src_uri is not set")

        if not self._out_file:
            raise TypeError("_out_file is not set")

        cmd = [
            "git",
            "clone",
            "--recursive",
            "--shallow-submodules",
            "--depth",
            "1",
        ]

        if self.git_branch:
            cmd += ["--branch", self.git_branch]

        cmd += [self.src_uri, self._out_file]

        return [cmd]


class Dependency:
    def __init__(self, *args, **kwargs) -> None:
        self.src: Optional[Src] = None
        self.local_path: TString = None
        self.local_name: TString = None

    def setSrc(self, src: Src):
        self.src = src

        return self

    def setLocalPath(self, local_path: str):
        self.local_path = local_path

        return self

    def setLocalName(self, local_name: str):
        self.local_name = local_name

        return self

    def build(self):
        if not self.src:
            raise RuntimeError("No src given")

        if not self.local_path:
            raise RuntimeError(f"No local path given for src {self.src}")

        if not self.local_name:
            self.local_name = self.src.getOutFile()

        return self

    def getOutName(self) -> str:
        """
        Return file name that user wants to have at the end.

        Checks local_name, if unspecified uses src's _out_file.
        """

        if self.local_name:
            return self.local_name

        if not self.src:
            raise TypeError("src is not set")

        return self.src.getOutFile()

    def makeLocalPath(self) -> None:
        if not self.local_path:
            return

        os.makedirs(self.local_path, exist_ok=True)


class DepmanConfiguration:
    def __init__(self, *args, **kwargs) -> None:
        self.dependencies: List[Dependency] = []

    def setDependencies(self, dependencies: List[Dependency]):
        self.dependencies = dependencies

        return self


class XmlUtils:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def __new__(cls, *args, **kwargs):
        pass

    @staticmethod
    def getDependenciesXml(xml):
        return xml.findall("dependency")

    @staticmethod
    def getSrc(xml) -> Src:
        src: Optional[Src] = None

        if (found_src := xml.find("gitSrc")) is not None:
            git_branch = found_src.find("gitBranch").get("value")
            # git_commit = found_src.find("gitCommit").get("value")

            src = GitSrc().setGitBranch(git_branch)

        elif (found_src := xml.find("fileSrc")) is not None:
            src = FileSrc()

        elif (found_src := xml.find("tarSrc")) is not None:
            src = TarSrc()

        if not src:
            raise RuntimeError("Src could not be parsed")

        src_uri = found_src.find("srcUri").get("value")

        checksum: Optional[Checksum] = None

        if (found_checksum := found_src.find("checksum")) is not None:
            sum_type = found_checksum.get("type")
            sum_value = found_checksum.get("value")

            checksum = Checksum().setSumType(sum_type).setSumValue(sum_value)

        return src.setSrcUri(src_uri).setChecksum(checksum).build()

    @staticmethod
    def getDependency(xml) -> Dependency:
        local_name_element = xml.find("localName")

        local_name: TString = None

        if local_name_element is None:
            pass
        else:
            local_name = local_name_element.get("value")

        local_path_element = xml.find("localPath")

        if local_path_element is None:
            raise RuntimeError("No local path declaration found in XML")

        local_path = local_path_element.get("value")

        src = XmlUtils.getSrc(xml)

        return Dependency().setSrc(src).setLocalPath(local_path).setLocalName(local_name).build()

    @staticmethod
    def getDependencies(element_tree):
        deps_xml = XmlUtils.getDependenciesXml(element_tree)

        return [XmlUtils.getDependency(dep_xml) for dep_xml in deps_xml]


class CommandExecutor:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def build(self):
        return self

    def run(self, command: Optional[List[str]]):
        if command:
            subprocess.run(command, check=True)


class DependencyManager:
    def __init__(self, *args, **kwargs) -> None:
        self.command_executor: Optional[CommandExecutor] = None
        self.dependencies: List[Dependency] = []

        self.start_cwd: str = "."
        self.dry_run: bool = False

    def setDependencies(self, dependencies: List[Dependency]):
        self.dependencies = dependencies

        return self

    def setCommandExecutor(self, command_executor: CommandExecutor):
        self.command_executor = command_executor

        return self

    def setStartCwd(self, start_cwd: str):
        self.start_cwd = start_cwd

        return self

    def setDryRun(self, a_bool):
        self.dry_run = a_bool

        return self

    def build(self):
        if not self.start_cwd:
            raise RuntimeError("No start_cwd given")

        if not self.command_executor:
            raise RuntimeError("No command_executor given")

        return self

    def toJson(self):
        top_level_object = {"current_working_directory": self.start_cwd}

        deps_arr = []

        for dependency in self.dependencies:
            d = {}

            d["uri"] = dependency.src.src_uri
            d["path"] = dependency.local_path
            d["name"] = dependency.local_name

            deps_arr.append(d)

        top_level_object["dependencies"] = deps_arr

        return json.dumps(top_level_object)

    def showConfiguration(self) -> None:
        index = 1

        for dependency in self.dependencies:
            if not dependency:
                raise TypeError("dependency is not set")

            if not dependency.src:
                raise TypeError("src is not set")

            if not dependency.src.src_uri:
                raise TypeError("src_uri is not set")

            print(f" Index  = {index}")
            print(f" Uri    = {dependency.src.src_uri}")
            print(f" Path   = {dependency.local_path}")
            print(f" Name   = {dependency.local_name}")

            index += 1

    def runCommand(self, a_command) -> None:
        """
        Run a given command (list or lambda).
        A Command is either a list of list of strings or a lambda function.

        In case of a list - each sub-list will be passed to a command executor.
        In case of a lambda - it will be called.
        """

        if not a_command:
            return

        elif isinstance(a_command, list):
            for a_subcommand in a_command:
                command_string = " ".join(a_subcommand)

                print(f" Running: {command_string}")

                if self.command_executor and not self.dry_run:
                    self.command_executor.run(a_subcommand)

        # Guard against lambda execution
        # (we can not tell the user what will be executed).
        elif self.dry_run:
            return

        # A lambda.
        else:
            a_command()

    def downloadDependencies(self) -> None:
        if not self.start_cwd:
            raise TypeError("start_cwd is not set")

        for dependency in self.dependencies:
            if not dependency.src:
                raise TypeError("src is not set")

            if not dependency.local_path:
                raise TypeError("local_path is not set")

            if not self.dry_run:
                dependency.makeLocalPath()
                os.chdir(self.start_cwd + "/" + dependency.local_path)

            out_name: str = dependency.getOutName()
            out_file: str = dependency.src.getOutFile()

            if os.path.exists(out_name):
                print(f" Already exists: {dependency.local_name}")
            else:
                print(f" Downloading: {dependency.local_name}")

                self.runCommand(dependency.src.getDownloadCommand())
                self.runCommand(dependency.src.getVerifyCommand())
                self.runCommand(dependency.src.getExtractionCommand())

                # HACK: Currently unsupported.
                if isinstance(dependency.src, TarSrc):
                    continue

                if dependency.local_name:
                    shutil.move(out_file, dependency.local_name)

            os.chdir(self.start_cwd)


class CliArgumentParser:
    def __init__(self, *args, **kwargs) -> None:
        argument_parser = argparse.ArgumentParser(
            prog=StaticDefs.app_name,
            description="minimal project-local dependency manager",
            epilog="",
        )

        argument_parser.add_argument(
            "--directory",
            "-C",
            help="Directory to use as a base of commands execution",
            type=str,
            default=START_CWD,
        )
        argument_parser.add_argument(
            "--config",
            "-c",
            help=f"{StaticDefs.app_name} config file path",
            type=str,
            default=os.path.join(START_CWD, "DEPMAN.xml"),
        )
        argument_parser.add_argument(
            "--dry_run",
            "-D",
            help="Dry run, do not download anything",
            action="store_true",
            default=False,
        )
        argument_parser.add_argument(
            "--json",
            "-j",
            help=f"Show {StaticDefs.app_name} config converted to JSON",
            action="store_true",
            default=False,
        )

        self.argument_parser = argument_parser
        self.parsed_args = None

    def build(self):
        self.parsed_args = self.argument_parser.parse_args()

        return self

    def getArgs(self):
        return self.parsed_args


class Program:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def __new__(cls, *args, **kwargs):
        pass

    @staticmethod
    def main() -> None:
        args = CliArgumentParser().build().getArgs()

        if not os.path.exists(args.config):
            raise FileNotFoundError(f"File not found, given: {args.config}")

        file_contents: str = ""

        with open(args.config, mode="r", encoding="UTF-8") as opened_file:
            file_contents = str(opened_file.read())

        # Parse XML and get the dependencies.
        element_tree = ElementTree.fromstring(file_contents)
        dependencies = XmlUtils.getDependencies(element_tree)

        command_executor = CommandExecutor().build()
        dependency_manager = (
            DependencyManager()
            .setDependencies(dependencies)
            .setCommandExecutor(command_executor)
            .setStartCwd(os.path.abspath(args.directory))
            .setDryRun(args.dry_run)
            .build()
        )

        if args.json:
            print(dependency_manager.toJson())

            return

        print(f"{StaticDefs.app_name} {StaticDefs.app_version}")

        dependency_manager.showConfiguration()
        dependency_manager.downloadDependencies()


START_CWD = os.getcwd()


if __name__ == "__main__":
    Program.main()

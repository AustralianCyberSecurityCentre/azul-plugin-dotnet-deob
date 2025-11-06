"""Deobfuscators used to deobfuscate dotnet binaries and executables."""

import os
import subprocess  # noqa # nosec: B404
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class DeobFailTypes(Enum):
    """Enum's for different kinds of failures."""

    NotValidDotnetFile = 1
    DotnetFileContentLengthMismatch = 2


@dataclass
class ExceptionMapping:
    """A mapping of a regex to a deobfuscator failure type."""

    regex_pattern: str
    fail_type: DeobFailTypes


class Deobfuscator:
    """Base Deobfuscators used to deobfuscate dotnet binaries, all other deobfuscators are based on this one."""

    key: str  # Identifying string for the deobfuscator.
    display_name: str  # Pretty name for the deobfuscator to appear on the UI.
    rel_path_to_exe: str  # Relative path to the Deobfuscators executable.
    regex_exception_mappings: list[ExceptionMapping]  # list of tuples with a regex and a corresponding exception type

    def _get_path_to_cmd(self):
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "bin",
            self.rel_path_to_exe,
        )

    def deobfuscate(self, in_file_path: str) -> tuple[str | None, str | None]:
        """Deobfuscate the supplied file and return the filepath of a deobfuscated file or an error.

        Returns Tuple[str | None, str | None]: first string is file path to the deobfuscated content second string is
        an error if one occurred.
        """
        raise NotImplementedError()

    def _deobfuscate(
        self, commandList: list[str], expected_out_file_loc: str, stdin: str = None
    ) -> tuple[str | None, str]:
        try:
            res: subprocess.CompletedProcess = subprocess.run(  # nosec: B603
                args=commandList,
                input=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                encoding="utf8",
            )

            if res.returncode != 0:
                return (
                    None,
                    f"An unexpected error occurred when deobfuscating. stderr {res.stderr} stdout: {res.stdout}.",
                )

            if os.path.exists(expected_out_file_loc):
                return expected_out_file_loc, None

            # Failed to produce expected output file without error.
            err_msg = f"Failed to produce the expected output file {expected_out_file_loc} contents of the out"
            +f" directory are {os.listdir(os.path.basename(expected_out_file_loc))}."
            return None, err_msg

        except OSError:
            return None, "OSError occured while deobfuscating."
        except subprocess.TimeoutExpired:
            return None, "Timed out while deobfuscating."


class De4dotCexDeobfuscator(Deobfuscator):
    """Deobfuscator that uses the de4dot-cex project.

    https://github.com/ViRb3/de4dot-cex
    """

    key: ClassVar[str] = "de4dotcex"
    display_name: str = "de4dot-cex"
    rel_path_to_exe: str = "mono/de4dot-cex/de4dot-x64.exe"
    regex_exception_mappings: list[ExceptionMapping] = [
        ExceptionMapping(
            regex_pattern=r"Format of the executable \(\.exe\) or library \(\.dll\) is invalid\.",
            fail_type=DeobFailTypes.NotValidDotnetFile,
        )
    ]

    def deobfuscate(self, in_file_path: str) -> tuple[str | None, str | None]:
        """Deobfuscate using de4dot-cex."""
        expected_out_file_loc = in_file_path + "deob-cex"
        commands = ["mono", self._get_path_to_cmd(), "-f", in_file_path, "-o", expected_out_file_loc]
        return self._deobfuscate(commands, expected_out_file_loc=expected_out_file_loc)


class ConfuserExStaticStringDecryptorDeobfuscator(Deobfuscator):
    """Deobfuscator that uses the ConfuserEx-Static-String-Decryptor project.

    https://github.com/Loksie/ConfuserEx-Static-String-Decryptor
    """

    key: ClassVar[str] = "ConfuserExSSD"
    display_name: str = "ConfuserEx-Static-String-Decryptor"
    rel_path_to_exe: str = "mono/ConfuserEx_Static_String_decryptor/ConfuserEx String Decryptor.exe"
    regex_exception_mappings: list[ExceptionMapping] = [
        ExceptionMapping(
            regex_pattern=r"Format of the executable \(\.exe\) or library \(\.dll\) is invalid\.",
            fail_type=DeobFailTypes.NotValidDotnetFile,
        ),
        ExceptionMapping(
            regex_pattern=r"There's not enough bytes left to read",
            fail_type=DeobFailTypes.DotnetFileContentLengthMismatch,
        ),
    ]

    def deobfuscate(self, in_file_path: str) -> tuple[str | None, str | None]:
        """Deobfuscate using ConfuserEx-Static-String-Decryptor."""
        expected_out_file_loc = in_file_path + "Cleaned.exe"
        commands = ["mono", self._get_path_to_cmd()]
        return self._deobfuscate(commands, expected_out_file_loc=expected_out_file_loc, stdin=in_file_path)


class UnscramblerDeobfuscator(Deobfuscator):
    """Deobfuscator that uses the Unscrambler project.

    NOTE: Unscrambler nearly always fails to modify the file.
    https://github.com/dr4k0nia/Unscrambler
    """

    key: ClassVar[str] = "unscrambler"
    display_name: str = "unscrambler"
    rel_path_to_exe: str = "dotnet/Unscrambler/Unscrambler.dll"
    regex_exception_mappings: list[ExceptionMapping] = [
        ExceptionMapping(
            regex_pattern=r"PE image does not contain a \.NET metadata directory",
            fail_type=DeobFailTypes.NotValidDotnetFile,
        ),
        ExceptionMapping(
            regex_pattern=r"Specified argument was out of the range of valid values\. \(Parameter \'fileOffset\'\)",
            fail_type=DeobFailTypes.DotnetFileContentLengthMismatch,
        ),
    ]

    def deobfuscate(self, in_file_path: str) -> tuple[str | None, str | None]:
        """Deobfuscate using Unscrambler."""
        prefix, postfix = os.path.splitext(in_file_path)
        expected_out_file_loc = prefix + "_unscrambled" + postfix
        commands = ["dotnet", self._get_path_to_cmd(), in_file_path]
        return self._deobfuscate(commands, expected_out_file_loc=expected_out_file_loc, stdin="\n")


AVAILABLE_DEOBFUSCATORS: list[Deobfuscator] = [
    UnscramblerDeobfuscator(),
    ConfuserExStaticStringDecryptorDeobfuscator(),
    De4dotCexDeobfuscator(),
]

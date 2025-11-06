"""Configurable plugin for using multiple dotnet Deobfuscators on a single file."""

import os
import re
import shutil
import tempfile
import traceback

import pefile
from azul_runner import BinaryPlugin, Job, State, add_settings, cmdline_run

from azul_plugin_dotnet_deob.deob import deobfuscators as deobs


class AzulPluginDotnetDeob(BinaryPlugin):
    """Configurable plugin for using multiple dotnet Deobfuscators on a single file."""

    VERSION = "2025.03.18"
    SETTINGS = add_settings(
        filter_data_types={
            "content": [
                # Windows exe
                "executable/windows/pe",
                "executable/windows/pe32",
                "executable/windows/pe64",
                "executable/windows/dll",
                "executable/windows/dll32",
                "executable/windows/dll64",
                # Potentially non windows exe
                "executable/dll32",
                "executable/pe32",
            ]
        },
        # File size to process
        filter_max_content_size=10 * 1024 * 1024,
        # Ignore self
        filter_self=True,
        # Keys of Deobfuscators in order they should be used.
        deobfuscators=(
            list[str],
            [
                deobs.UnscramblerDeobfuscator.key,
                deobs.ConfuserExStaticStringDecryptorDeobfuscator.key,
                deobs.De4dotCexDeobfuscator.key,
            ],
        ),
    )
    FEATURES = []

    def execute(self, job: Job):
        """Run the plugin."""
        data = job.get_data()
        in_file_path = data.get_filepath()
        try:
            with pefile.PE(in_file_path, fast_load=True) as pe:
                if (
                    len(pe.OPTIONAL_HEADER.DATA_DIRECTORY) < 15
                    or pe.OPTIONAL_HEADER.DATA_DIRECTORY[14].VirtualAddress == 0
                ):
                    return State(State.Label.OPT_OUT, "Not a .NET assembly")
        except pefile.PEFormatError:
            return State(
                State.Label.ERROR_EXCEPTION, failure_name="Error while parsing PE", message=traceback.format_exc()
            )

        successful_deobs = []
        failed_deobs: list[tuple[deobs.Deobfuscator, str]] = []

        with tempfile.TemporaryDirectory() as cur_dir:
            src_file_path = os.path.join(cur_dir, os.path.basename(in_file_path))
            shutil.copy(in_file_path, src_file_path)

            newest_file_path = src_file_path
            for deob in deobs.AVAILABLE_DEOBFUSCATORS:
                if deob.key not in self.cfg.deobfuscators:
                    continue

                result_file_path, error = deob.deobfuscate(newest_file_path)
                if result_file_path is None:
                    failed_deobs.append((deob, f"Deobfuscator {deob.display_name} failed with error: " + error))
                    self.logger.warning(failed_deobs[-1][1])
                else:
                    newest_file_path = result_file_path
                    successful_deobs.append(deob.display_name)

            if len(successful_deobs) > 0:
                with open(newest_file_path, "r+b") as f:
                    self.add_child_with_data_file(
                        {"action": "deobfuscated", "deobfuscated_by": ",".join(successful_deobs)},
                        data_file=f,
                    )
            else:
                # Process the deobfuscators and see if there is a useful message type.
                error_type = None
                for deob, msg in failed_deobs:
                    for mapping in deob.regex_exception_mappings:
                        regex = re.compile(mapping.regex_pattern)
                        matches = regex.search(msg)
                        if matches is not None:
                            error_type = mapping.fail_type
                            break

                if error_type == deobs.DeobFailTypes.NotValidDotnetFile:
                    return State(State.Label.OPT_OUT, message="Deobfuscators detect file as not a valid dotnet file.")
                elif error_type == deobs.DeobFailTypes.DotnetFileContentLengthMismatch:
                    # Error that occurs when the dotnet file has been improperly truncated.
                    self.is_malformed("Dotnetfile is shorter than the header specifies.")
                    return

                return State(
                    State.Label.COMPLETED_EMPTY,
                    failure_name="no-deobfuscation-processed",
                    message="Could not run any of the deobfuscators.",
                )


def main():
    """Plugin command-line entrypoint."""
    cmdline_run(plugin=AzulPluginDotnetDeob)


if __name__ == "__main__":
    main()

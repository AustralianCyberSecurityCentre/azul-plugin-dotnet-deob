"""Test cases for plugin output."""

from azul_runner import (
    FV,
    Event,
    EventData,
    EventParent,
    JobResult,
    State,
    test_template,
)

from azul_plugin_dotnet_deob.deob import deobfuscators as deobs
from azul_plugin_dotnet_deob.main import AzulPluginDotnetDeob


class TestExecute(test_template.TestPlugin):
    PLUGIN_TO_TEST = AzulPluginDotnetDeob

    def DEFAULT_CONFIG(self):
        """Get the default config."""
        return {
            "deobfuscators": [
                deobs.UnscramblerDeobfuscator.key,
                deobs.ConfuserExStaticStringDecryptorDeobfuscator.key,
                deobs.De4dotCexDeobfuscator.key,
            ]
        }

    def test_add_child(self):
        """Test a successful normal run that adds a child."""
        data = self.load_test_file_bytes(
            "d30feab410f4b260f6ec56d39969ac8673a585fae4c1308d51136bcd8af0100d",
            "Malicious .NET Windows 32EXE, obfuscated with ConfuserEx.",
        )
        result = self.do_execution(data_in=[("content", data)], config=self.DEFAULT_CONFIG())
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED),
                events=[
                    Event(
                        parent=EventParent(
                            entity_type="binary",
                            entity_id="d30feab410f4b260f6ec56d39969ac8673a585fae4c1308d51136bcd8af0100d",
                        ),
                        entity_type="binary",
                        entity_id="f457e1bf7090e0db87d6facf28fe74262c003c3b383157b5fe5c9d80c7a5f6db",
                        relationship={"action": "deobfuscated", "deobfuscated_by": "de4dot-cex"},
                        data=[
                            EventData(
                                hash="f457e1bf7090e0db87d6facf28fe74262c003c3b383157b5fe5c9d80c7a5f6db",
                                label="content",
                            )
                        ],
                    )
                ],
                data={"f457e1bf7090e0db87d6facf28fe74262c003c3b383157b5fe5c9d80c7a5f6db": b""},
            ),
        )

    def test_add_child_s(self):
        """Test a successful normal run that adds a child."""
        data = self.load_test_file_bytes(
            "61637f9940e5e336571cbf945be0f36d6d6050e06288df0f0232d93b26f0bde7",
            "Benign .NET Windows 32DLL, common library called Mono.Cecil.Mdb.dll.",
        )
        result = self.do_execution(data_in=[("content", data)], config=self.DEFAULT_CONFIG())
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED),
                events=[
                    Event(
                        parent=EventParent(
                            entity_type="binary",
                            entity_id="61637f9940e5e336571cbf945be0f36d6d6050e06288df0f0232d93b26f0bde7",
                        ),
                        entity_type="binary",
                        entity_id="41b72f11583563733b693f6b9d94ca2964054834645bc74a2b2ba445620460fb",
                        relationship={
                            "action": "deobfuscated",
                            "deobfuscated_by": "ConfuserEx-Static-String-Decryptor,de4dot-cex",
                        },
                        data=[
                            EventData(
                                hash="41b72f11583563733b693f6b9d94ca2964054834645bc74a2b2ba445620460fb",
                                label="content",
                            )
                        ],
                    )
                ],
                data={"41b72f11583563733b693f6b9d94ca2964054834645bc74a2b2ba445620460fb": b""},
            ),
        )

    def test_no_deobs_run(self):
        """Test a run where no deobfuscators successfully run."""
        data = self.load_test_file_bytes(
            "cd8764f579d38406fe77ab8ebcc4cec82e3ceef1d769ea2e9b84a866b6d0a119",
            "Malicious Windows 32EXE key logger and credential stealer.",
        )
        result = self.do_execution(data_in=[("content", data)], config=self.DEFAULT_CONFIG())
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.OPT_OUT, message="Deobfuscators detect file as not a valid dotnet file.")
            ),
        )

    def test_not_dotnet_file(self):
        """Test a run where the file is a mono dotnet file but has content after the declared end of file."""
        data = self.load_test_file_bytes(
            "b13049711027802304b0f50291d5557e76113b46c0a2258b919e65d519ace2f2", "Malicious .NET MONO Windows 32EXE."
        )
        result = self.do_execution(data_in=[("content", data)], config=self.DEFAULT_CONFIG())
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED),
                events=[
                    Event(
                        entity_type="binary",
                        entity_id="b13049711027802304b0f50291d5557e76113b46c0a2258b919e65d519ace2f2",
                        features={"malformed": [FV("Dotnetfile is shorter than the header specifies.")]},
                    )
                ],
            ),
        )

    def test_not_dotnet_file(self):
        """Test a run where the file is a mono dotnet file but has content after the declared end of file."""
        data = self.load_test_file_bytes(
            "6ade497b4a45a2c4688ac69fe2ae146c721db3cf8d82df9b5ca40b4614ad62b7",
            "Malicious .NET Windows 32EXE, keylogger with threat name AGENTTESLA",
        )
        result = self.do_execution(data_in=[("content", data)], config=self.DEFAULT_CONFIG())
        self.assertJobResult(
            result,
            JobResult(
                state=State(
                    State.Label.COMPLETED_EMPTY,
                    failure_name="no-deobfuscation-processed",
                    message="Could not run any of the deobfuscators.",
                )
            ),
        )

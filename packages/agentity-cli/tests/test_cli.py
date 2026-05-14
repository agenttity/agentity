import pytest
import json
import subprocess
import sys
from pathlib import Path

CLI_SCRIPT = str(Path(__file__).resolve().parents[2] / "agentity_cli" / "main.py")
if not Path(CLI_SCRIPT).exists():
    import agentity_cli
    CLI_SCRIPT = agentity_cli.__file__.replace("__init__.py", "main.py")


def run_cli(*args):
    return subprocess.run(
        [sys.executable, CLI_SCRIPT] + list(args),
        capture_output=True, text=True,
    )


def test_cli_create():
    result = run_cli("create", "--owner", "did:agentity:human:alice", "--scope", "test:read")
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["did"].startswith("did:agentity:agent:")
    assert "secretKey" in data
    assert "aid" in data


def test_cli_manifest():
    result = run_cli("manifest", "--name", "Test API", "--scopes", "test:read,test:write")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["name"] == "Test API"
    assert len(data["scopes"]) == 2


def test_cli_verify_from_stdout():
    create = run_cli("create", "--owner", "did:agentity:human:alice")
    assert create.returncode == 0
    tmp = Path("/tmp/agentity-test-id.json")
    tmp.write_text(create.stdout)
    result = run_cli("verify", str(tmp))
    assert result.returncode == 0
    assert "VERIFIED" in result.stdout
    tmp.unlink(missing_ok=True)


def test_cli_inspect_from_stdout():
    create = run_cli("create", "--owner", "did:agentity:human:alice")
    assert create.returncode == 0
    tmp = Path("/tmp/agentity-test-inspect.json")
    tmp.write_text(create.stdout)
    result = run_cli("inspect", str(tmp))
    assert result.returncode == 0
    assert "DID:" in result.stdout
    tmp.unlink(missing_ok=True)

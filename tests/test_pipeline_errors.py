
import subprocess
import sys

import pytest


def test_subprocess_raises_error_when_script_fails():
    """Un script qui retourne 1 doit provoquer une erreur si check=True."""
    with pytest.raises(subprocess.CalledProcessError) as error:
        subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.exit(1)",
            ],
            check=True,
        )

    assert error.value.returncode == 1


def test_subprocess_succeeds_when_script_returns_zero():
    """Un script qui retourne 0 doit terminer normalement."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.exit(0)",
        ],
        check=True,
    )

    assert result.returncode == 0

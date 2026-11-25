import sys

import pytest

from eval import live, run_full


def test_argparse_help_is_independent_of_module_docstring(monkeypatch, capsys):
    monkeypatch.setattr(run_full, "__doc__", None)
    monkeypatch.setattr(sys, "argv", ["run_full.py", "--help"])

    with pytest.raises(SystemExit) as result:
        run_full.main()

    output = capsys.readouterr()
    assert result.value.code == 0
    assert "--suite" in output.out and "--artifact-dir" in output.out
    assert output.err == ""


def test_live_usage_is_independent_of_module_docstring(monkeypatch):
    monkeypatch.setattr(live, "__doc__", None)
    monkeypatch.setattr(sys, "argv", ["live.py"])

    with pytest.raises(SystemExit) as result:
        live.main()

    assert "python3 -m eval.live catalog" in result.value.code
    assert "python3 -m eval.live run <folder>" in result.value.code

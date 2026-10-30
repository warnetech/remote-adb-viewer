from rav import cli, config


def test_add_list_remove(capsys):
    assert cli.main(["add", "pixel", "--tailscale", "100.64.0.5:5555"]) == 0
    assert cli.main(["add", "lab", "--ssh", "me@pi.local", "--serial", "ABC"]) == 0
    devices = config.load()
    assert devices["pixel"].transport == "tcp"
    assert devices["lab"].serial == "ABC"

    assert cli.main(["remove", "pixel"]) == 0
    assert set(config.load()) == {"lab"}
    assert cli.main(["remove", "pixel"]) == 1


def test_bad_name_is_an_error(capsys):
    assert cli.main(["add", "my phone", "--usb", "X"]) == 1
    assert "invalid device name" in capsys.readouterr().err


def test_unknown_device(capsys):
    assert cli.main(["doctor", "nope"]) == 1
    assert "no device named 'nope'" in capsys.readouterr().err


def test_view_missing_binary(capsys):
    cli.main(["add", "pixel", "--tcp", "100.64.0.5:5555"])
    assert cli.main(["view", "pixel", "--binary", "/nonexistent/tainuitech"]) == 1
    assert "'/nonexistent/tainuitech' not found" in capsys.readouterr().err


def test_view_options_are_parsed_and_extra_passed(monkeypatch):
    seen = {}

    def fake_view(args):
        seen.update(vars(args))
        return 0

    monkeypatch.setattr(cli, "cmd_view", fake_view)
    cli.main(["view", "pixel", "--profile", "wan", "--headless", "--binary", "x",
              "--", "--no-audio", "--max-fps=60"])
    assert seen["profile"] == "wan"
    assert seen["headless"] is True
    assert seen["binary"] == "x"
    assert seen["extra"] == ["--no-audio", "--max-fps=60"]

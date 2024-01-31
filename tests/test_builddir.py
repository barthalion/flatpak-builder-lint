from flatpak_builder_lint import checks, cli


def run_checks(filename: str) -> dict:
    checks.Check.errors = set()
    checks.Check.warnings = set()
    return cli.run_checks("builddir", filename)


def test_builddir_appid() -> None:
    errors = {"appid-ends-with-lowercase-desktop", "appid-uses-code-hosting-domain"}
    ret = run_checks("tests/builddir/appid")
    found_errors = set(ret["errors"])
    assert errors.issubset(found_errors)


def test_builddir_finish_args() -> None:
    errors = {
        "finish-args-arbitrary-autostart-access",
        "finish-args-arbitrary-dbus-access",
        "finish-args-arbitrary-xdg-data-access",
        "finish-args-flatpak-spawn-access",
        "finish-args-incorrect-dbus-gvfs",
        "finish-args-redundant-home-and-host",
        "finish-args-unnecessary-appid-own-name",
        "finish-args-unnecessary-xdg-data-access",
        "finish-args-wildcard-freedesktop-talk-name",
        "finish-args-wildcard-gnome-own-name",
        "finish-args-wildcard-kde-own-name",
        "finish-args-portal-talk-name",
    }

    warnings = {
        "finish-args-deprecated-shm",
        "finish-args-x11-without-ipc",
        "finish-args-redundant-device-all",
    }

    ret = run_checks("tests/builddir/finish_args")
    found_errors = set(ret["errors"])
    found_warnings = set(ret["warnings"])

    assert errors.issubset(found_errors)
    assert warnings.issubset(found_warnings)


def test_builddir_finish_args_missing() -> None:
    ret = run_checks("tests/builddir/finish_args_missing")
    found_errors = set(ret["errors"])
    assert "finish-args-not-defined" in found_errors


def test_builddir_flathub_json() -> None:
    errors = {
        "flathub-json-skip-appstream-check",
        "flathub-json-modified-publish-delay",
    }

    warnings = {"flathub-json-deprecated-i386-arch-included"}

    ret = run_checks("tests/builddir/flathub_json")
    found_errors = set(ret["errors"])
    found_warnings = set(ret["warnings"])

    assert errors.issubset(found_errors)
    assert warnings.issubset(found_warnings)


def test_builddir_baseapp() -> None:
    ret = run_checks("tests/builddir/baseapp")


def test_builddir_extension() -> None:
    ret = run_checks("tests/builddir/extension")


def test_builddir_console() -> None:
    errors = {"finish-args-not-defined"}

    ret = run_checks("tests/builddir/console")
    found_errors = set(ret["errors"])

    assert errors == found_errors


def test_builddir_metadata_spaces() -> None:
    ret = run_checks("tests/builddir/metadata-spaces")


def test_builddir_desktop_file() -> None:
    ret = run_checks("tests/builddir/desktop-file")
    errors = {
        "desktop-file-icon-key-wrong-value",
        "desktop-file-is-hidden",
        "desktop-file-exec-has-flatpak-run",
    }
    found_errors = set(ret["errors"])
    found_warnings = set(ret["warnings"])

    assert "desktop-file-low-quality-category" in found_warnings
    for err in errors:
        assert err in found_errors


def test_builddir_quality_guidelines() -> None:
    ret = run_checks("tests/builddir/appdata-quality")
    errors = {
        "appstream-missing-developer-name",
        "appstream-missing-project-license",
        "no-exportable-icon-installed",
    }
    warnings = {
        "appstream-name-too-long",
        "appstream-screenshot-missing-caption",
        "appstream-summary-too-long",
    }
    found_warnings = set(ret["warnings"])
    found_errors = set(ret["errors"])
    for w in warnings:
        assert w in found_warnings
    for e in errors:
        assert e in found_errors

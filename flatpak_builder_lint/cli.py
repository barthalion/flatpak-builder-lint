import argparse
import importlib
import importlib.resources
import json
import os
import pkgutil
import sys
from typing import Dict, List, Optional, Union

import sentry_sdk

from . import (
    __version__,
    appstream,
    builddir,
    checks,
    domainutils,
    manifest,
    ostree,
    staticfiles,
)

if sentry_dsn := os.getenv("SENTRY_DSN"):
    sentry_sdk.init(sentry_dsn)

for plugin_info in pkgutil.iter_modules(checks.__path__):
    importlib.import_module(f".{plugin_info.name}", package=checks.__name__)


def _filter(info: set, excepts: set) -> list:
    final = set()
    for i in info:
        count = False
        for j in excepts:
            if i is not None and i.startswith(j):
                count = True
                break
        if not count:
            final.add(i)
    return list(final)


def get_local_exceptions(appid: str) -> set[str]:
    with importlib.resources.open_text(staticfiles, "exceptions.json") as f:
        exceptions = json.load(f)
        ret = exceptions.get(appid)

    if ret:
        return set(ret)

    return set()


def run_checks(
    kind: str, path: str, enable_exceptions: bool = False, appid: Optional[str] = None
) -> Dict[str, Union[str, List[Optional[str]]]]:
    match kind:
        case "manifest":
            check_method_name = "check_manifest"
            infer_appid_func = manifest.infer_appid
            check_method_arg: Union[str, dict] = manifest.show_manifest(path)
        case "builddir":
            check_method_name = "check_build"
            infer_appid_func = builddir.infer_appid
            check_method_arg = path
        case "repo":
            check_method_name = "check_repo"
            infer_appid_func = ostree.infer_appid
            check_method_arg = path
        case _:
            raise ValueError(f"Unknown kind: {kind}")

    for checkclass in checks.ALL:
        check = checkclass()

        if (check_method := getattr(check, check_method_name, None)) and callable(check_method):
            check_method(check_method_arg)

    results: Dict[str, Union[str, List[Optional[str]]]] = {}
    if errors := checks.Check.errors:
        results["errors"] = list(errors)
    if warnings := checks.Check.warnings:
        results["warnings"] = list(warnings)
    if jsonschema := checks.Check.jsonschema:
        results["jsonschema"] = list(jsonschema)
    if appstream := checks.Check.appstream:
        results["appstream"] = list(appstream)
    if desktopfile := checks.Check.desktopfile:
        results["desktopfile"] = list(desktopfile)
    if info := checks.Check.info:
        results["info"] = list(info)

    if enable_exceptions:
        exceptions = None

        appid = appid[0] if appid else infer_appid_func(path)

        if appid:
            exceptions = domainutils.get_remote_exceptions(appid)
            if not exceptions:
                exceptions = get_local_exceptions(appid)

        if exceptions:
            if "*" in exceptions:
                return {}

            results["errors"] = list(errors - set(exceptions))
            if not results["errors"]:
                results.pop("errors")

            results["warnings"] = list(warnings - set(exceptions))
            if not results["warnings"]:
                results.pop("warnings")

            if "appstream-failed-validation" in set(exceptions):
                results.pop("appstream", None)

            if "desktop-file-failed-validation" in set(exceptions):
                results.pop("desktopfile", None)

            results["info"] = _filter(set(info), set(exceptions))
            if not results["info"]:
                results.pop("info")

    help = (
        "Please consult the documentation at "
        "https://docs.flathub.org/docs/for-app-authors/linter"
    )

    if any(x in results for x in ("errors", "warnings", "info")):
        results["message"] = help

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="A linter for Flatpak builds and flatpak-builder manifests",
        epilog="If you consider the detected issues incorrect, please report it here: https://github.com/flathub/flatpak-builder-lint",  # noqa: E501
    )
    parser.add_argument(
        "--version", action="version", version=f"flatpak-builder-lint {__version__}"
    )
    parser.add_argument("--exceptions", help="skip allowed warnings or errors", action="store_true")
    parser.add_argument("--appid", help="override app ID", type=str, nargs=1)
    parser.add_argument(
        "--cwd",
        help="override the path parameter with current working directory",
        action="store_true",
    )
    parser.add_argument(
        "--ref",
        help="override the primary ref detection",
        type=str,
        nargs=1,
        default=None,
    )

    parser.add_argument(
        "type",
        help="type of artifact to lint",
        choices=["builddir", "repo", "manifest", "appstream"],
    )
    parser.add_argument(
        "path",
        help="path to artifact",
        type=str,
        nargs=1,
    )

    args = parser.parse_args()
    exit_code = 0

    path = os.getcwd() if args.cwd else args.path[0]

    if args.ref:
        checks.Check.repo_primary_ref = args.ref[0]

    if args.type != "appstream":
        if results := run_checks(args.type, path, args.exceptions, args.appid):
            if "errors" in results:
                exit_code = 1

            output = json.dumps(results, indent=4)
            print(output)  # noqa: T201
    else:
        appstream_results = appstream.validate(path, "--explain")
        print(appstream_results["stdout"])  # noqa: T201
        print(appstream_results["stderr"])  # noqa: T201
        exit_code = appstream_results["returncode"]

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

import os
import subprocess
from typing import Optional

from lxml import etree

# for mypy
Element = etree._Element
ElementTree = etree._ElementTree


def validate(path: str, *args: str) -> dict:
    if not os.path.isfile(path):
        raise FileNotFoundError("AppStream file not found")

    overrides = {
        "all-categories-ignored": "error",
        "category-invalid": "error",
        "cid-desktopapp-is-not-rdns": "error",
        "cid-has-number-prefix": "error",
        "cid-missing-affiliation-gnome": "error",
        "cid-rdns-contains-hyphen": "error",
        "component-name-too-long": "info",
        "content-rating-missing": "error",
        "description-has-plaintext-url": "info",
        "desktop-app-launchable-omitted": "error",
        "desktop-file-not-found": "error",
        "developer-id-invalid": "info",
        "developer-id-missing": "error",
        "invalid-child-tag-name": "error",
        "metainfo-filename-cid-mismatch": "error",
        "metainfo-legacy-path": "error",
        "metainfo-multiple-components": "error",
        "name-has-dot-suffix": "error",
        "releases-info-missing": "error",
        "summary-too-long": "info",
        "unknown-tag": "error",
    }

    overrides_value = ",".join([f"{k}={v}" for k, v in overrides.items()])

    cmd = subprocess.run(
        ["appstreamcli", "validate", f"--override={overrides_value}", *args, path],
        capture_output=True,
    )

    ret = {
        "stdout": cmd.stdout.decode("utf-8"),
        "stderr": cmd.stderr.decode("utf-8"),
        "returncode": cmd.returncode,
    }

    return ret


def parse_xml(path: str) -> ElementTree:
    return etree.parse(path)


def components(path: str) -> list:
    components = parse_xml(path).xpath("/components/component")
    return list(components)


def is_developer_name_present(path: str) -> bool:
    developer_name = components(path)[0].xpath("developer/name")
    legacy_developer_name = components(path)[0].xpath("developer_name")
    return bool(developer_name or legacy_developer_name)


def is_project_license_present(path: str) -> bool:
    plicense = components(path)[0].xpath("project_license")
    return bool(plicense)


def component_type(path: str) -> str:
    return str(components(path)[0].attrib.get("type"))


def is_valid_component_type(path: str) -> bool:
    if component_type(path) in (
        "addon",
        "console-application",
        "desktop",
        "desktop-application",
        "runtime",
    ):
        return True
    return False


def name(path: str) -> Optional[str]:
    for name in parse_xml(path).findall("component/name"):
        if not name.attrib.get(r"{http://www.w3.org/XML/1998/namespace}lang"):
            return str(name.text)
    return None


def summary(path: str) -> Optional[str]:
    for summary in parse_xml(path).findall("component/summary"):
        if not summary.attrib.get(r"{http://www.w3.org/XML/1998/namespace}lang"):
            return str(summary.text)
    return None


def check_caption(path: str) -> bool:
    exp = "//screenshot[not(caption/text()) or not(caption)]"
    return not any(e is not None for e in parse_xml(path).xpath(exp))


def has_manifest_key(path: str) -> bool:
    custom = parse_xml(path).xpath("//custom/value[@key='flathub::manifest']/text()")
    metadata = parse_xml(path).xpath(
        "//metadata/value[@key='flathub::manifest']/text()"
    )
    return bool(custom or metadata)


def has_icon_key(path: str) -> bool:
    return bool(components(path)[0].xpath("icon"))


def icon_no_type(path: str) -> bool:
    for icon in parse_xml(path).findall("component/icon"):
        if icon.attrib.get("type") is None:
            return True
    return False


def is_remote_icon_mirrored(path: str) -> bool:
    remote_icons = parse_xml(path).xpath("//icon[@type='remote']/text()")
    return all(
        icon.startswith("https://dl.flathub.org/media/") for icon in remote_icons
    )


def get_icon_filename(path: str) -> Optional[str]:
    if icons := parse_xml(path).xpath("/components/component[1]/icon[@type='cached']"):
        return str(icons[0].text)
    return None

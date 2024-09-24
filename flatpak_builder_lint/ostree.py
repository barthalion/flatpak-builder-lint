import json
import os

import gi

gi.require_version("OSTree", "1.0")
from gi.repository import Gio, GLib, OSTree  # noqa: E402


def open_ostree_repo(repo_path: str) -> OSTree.Repo:
    repo = OSTree.Repo.new(Gio.File.new_for_path(repo_path))

    if not repo.open(None):
        raise Exception("Failed to open the OSTree repository")

    return repo


def get_refs(repo_path: str, ref_prefix: str | None) -> set[str]:
    repo = open_ostree_repo(repo_path)
    _, refs = repo.list_refs(ref_prefix, None)

    return set(refs.keys())


def get_primary_ref(repo_path: str) -> str | None:
    refs = get_refs(repo_path, None)

    ref: str

    for ref in refs:
        if ref.startswith("app/"):
            return ref

    return None


def infer_appid(path: str) -> str | None:
    ref = get_primary_ref(path)
    if ref:
        return ref.split("/")[1]

    return None


def extract_subpath(
    repo_path: str,
    ref: str,
    subpath: str,
    dest: str,
    should_pass: bool = False,
) -> None:
    repo = open_ostree_repo(repo_path)
    opts = OSTree.RepoCheckoutAtOptions()
    # https://gitlab.gnome.org/GNOME/pygobject/-/issues/639
    opts.mode = int(OSTree.RepoCheckoutMode.USER)  # type: ignore
    opts.overwrite_mode = int(OSTree.RepoCheckoutOverwriteMode.ADD_FILES)  # type: ignore
    opts.subpath = subpath

    _, rev = repo.resolve_rev(ref, True)

    # https://sourceware.org/git/?p=glibc.git;a=blob;f=io/fcntl.h;h=f157991782681caabe9bd7edb46ec205731965af;hb=HEAD#l149
    AT_FDCWD = -100
    if rev:
        if should_pass:
            try:
                repo.checkout_at(opts, AT_FDCWD, dest, rev, None)
            except GLib.Error as err:
                if err.matches(Gio.io_error_quark(), Gio.IOErrorEnum.NOT_FOUND):
                    pass
                else:
                    raise
        else:
            repo.checkout_at(opts, AT_FDCWD, dest, rev, None)


def get_flathub_json(repo_path: str, ref: str, dest: str) -> dict[str, str | bool | list[str]]:
    extract_subpath(repo_path, ref, "/files/flathub.json", dest, True)

    flathub_json_path = os.path.join(dest, "flathub.json")
    flathub_json: dict = {}

    if os.path.exists(flathub_json_path):
        with open(flathub_json_path) as fp:
            flathub_json = json.load(fp)

    return flathub_json

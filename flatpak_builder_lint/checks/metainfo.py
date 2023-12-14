import os
import tempfile
from typing import Optional

from .. import appstream, builddir, ostree
from . import Check


class MetainfoCheck(Check):
    def _validate(self, path: str, appid: str, flathub_json: Optional[dict]) -> None:
        if not flathub_json:
            flathub_json = {}
        skip_appstream_check = flathub_json.get("skip-appstream-check")
        skip_icons_check = flathub_json.get("skip-icons-check")

        appstream_path = f"{path}/files/share/app-info/xmls/{appid}.xml.gz"
        icon_path = f"{path}/files/share/app-info/icons/flatpak/128x128/{appid}.png"
        metainfo_dirs = [
            f"{path}/files/share/metainfo",
            f"{path}/files/share/appdata",
        ]
        metainfo_exts = [".appdata.xml", ".metainfo.xml"]
        metainfo_path = None

        is_baseapp = appid.endswith(".BaseApp")

        for metainfo_dir in metainfo_dirs:
            for ext in metainfo_exts:
                metainfo_dirext = f"{metainfo_dir}/{appid}{ext}"
                if os.path.exists(metainfo_dirext):
                    metainfo_path = metainfo_dirext

        if not skip_appstream_check:
            if not os.path.exists(appstream_path):
                self.errors.add("appstream-missing-appinfo-file")

            if not metainfo_path:
                self.errors.add("appstream-metainfo-missing")

            if metainfo_path is not None:
                if not appstream.is_developer_name_present(appstream_path):
                    self.warnings.add("appstream-missing-developer-name")

                if not is_baseapp:
                    appinfo_validation = appstream.validate(metainfo_path)
                    if appinfo_validation["returncode"] != 0:
                        self.errors.add("appstream-failed-validation")

        if not (skip_icons_check or skip_appstream_check):
            if not os.path.exists(icon_path):
                if not is_baseapp:
                    self.errors.add("appstream-missing-icon-file")

    def check_build(self, path: str) -> None:
        appid = builddir.infer_appid(path)
        if not appid:
            return

        metadata = builddir.get_metadata(path)
        if not metadata:
            return
        is_extension = metadata.get("extension")

        flathub_json = builddir.get_flathub_json(path)
        self._validate(f"{path}", appid, flathub_json)

        if is_extension:
            self.errors.discard("appstream-failed-validation")
            self.errors.discard("appstream-missing-icon-file")

        appstream_path = f"{path}/files/share/app-info/xmls/{appid}.xml.gz"
        if os.path.exists(appstream_path) and appstream.is_console(appstream_path):
            self.errors.discard("appstream-missing-icon-file")

    def check_repo(self, path: str) -> None:
        self._populate_ref(path)
        ref = self.repo_primary_ref
        if not ref:
            return
        appid = ref.split("/")[1]

        flathub_json = ostree.get_flathub_json(path, ref)

        with tempfile.TemporaryDirectory() as tmpdir:
            ret = ostree.extract_subpath(path, ref, "/", tmpdir)
            if ret["returncode"] != 0:
                raise RuntimeError("Failed to extract ostree repo")
            appstream_path = f"{tmpdir}/files/share/app-info/xmls/{appid}.xml.gz"
            self._validate(tmpdir, appid, flathub_json)
            if os.path.exists(appstream_path) and appstream.is_console(appstream_path):
                self.errors.discard("appstream-missing-icon-file")

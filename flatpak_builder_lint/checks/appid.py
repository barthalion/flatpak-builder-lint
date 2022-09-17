import os

from . import Check


class AppIDCheck(Check):
    type = "manifest"

    def check(self, manifest: dict) -> None:
        appid = manifest.get("id")
        if not appid:
            self.errors.append("appid-not-defined")
            return

        if filename := manifest.get("x-manifest-filename"):
            (manifest_basename, _) = os.path.splitext(filename)
            manifest_basename = os.path.basename(manifest_basename)

            if appid != manifest_basename:
                self.errors.append("appid-filename-mismatch")

        split = appid.split(".")
        if split[-1] == "desktop":
            self.errors.append("appid-ends-with-lowercase-desktop")

        domain = split[1].lower()
        tld = split[0].lower()
        if domain in ("github", "gitlab", "codeberg"):
            if tld != "io" and domain in ("github", "gitlab"):
                self.warnings.append("appid-uses-code-hosting-domain")
            # Codeberg: https://codeberg.page/
            if tld != "page" and domain == "codeberg":
                self.warnings.append("appid-uses-code-hosting-domain")
            if len(split) < 4:
                self.errors.append("appid-code-hosting-too-few-components")

import errno
import json
import os
import subprocess


# json-glib supports non-standard syntax like // comments. Bail out and
# delegate parsing to flatpak-builder.
def show_manifest(filename: str) -> dict:
    if not os.path.exists(filename):
        raise OSError(errno.ENOENT)

    ret = subprocess.run(
        ["flatpak-builder", "--show-manifest", filename], capture_output=True
    )

    if ret.returncode != 0:
        raise Exception(ret.stderr.decode("utf-8"))

    manifest = ret.stdout.decode("utf-8")
    manifest_json = json.loads(manifest)
    manifest_json["x-manifest-filename"] = filename

    # mypy does not support circular types
    # https://github.com/python/typing/issues/182
    return manifest_json  # type: ignore

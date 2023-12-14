#!/usr/bin/python3

import json

with open("org.flatpak.Builder/org.flatpak.Builder.json", "r") as f:
    manifest = json.load(f)

for module in manifest["modules"]:
    if isinstance(module, dict):
        if module.get("name") == "flatpak-builder-lint":
            module["sources"] = [{"type": "dir", "path": "../.."}]
            break

with open("org.flatpak.Builder/org.flatpak.Builder.json", "w") as f:
    json.dump(manifest, f)

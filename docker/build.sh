#!/bin/bash
set -e

sudo apt-get update
sudo apt-get install -y --no-install-recommends flatpak dbus-daemon \
    git python3

git config --global protocol.file.allow always

flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user -y flathub org.flatpak.Builder
rm -rf org.flatpak.Builder
git clone --depth=1 --branch master --recursive --single-branch https://github.com/flathub/org.flatpak.Builder.git

cp -vf docker/flatpak-builder-lint-deps.json org.flatpak.Builder/
python3 rewrite-manifest.py

case $1 in
    amd64)
        arch=x86_64
        ;;
    arm64)
        arch=aarch64
        ;;
esac

cd org.flatpak.Builder
dbus-run-session flatpak run org.flatpak.Builder --state-dir="$GITHUB_WORKSPACE/.flatpak-builder" \
    --arch="$arch" --verbose --user --force-clean --ccache \
    --install-deps-from=flathub builddir org.flatpak.Builder.json
rm -rf "builddir/files/lib/debug"

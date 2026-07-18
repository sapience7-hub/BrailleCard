#!/bin/sh
set -eu

# Downloads only the pinned official GitHub release used for offline slicing.
# It contains no printer address and performs no printer discovery or control.
repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
tool_dir="$repository_root/.tools/orca"
appimage="$tool_dir/OrcaSlicer.AppImage"
expected_sha="e1a07275a25f176626c55a5df39e91bc4476d8c28ee4a3192ff758e29dd5c3ba"
url="https://github.com/OrcaSlicer/OrcaSlicer/releases/download/v2.4.2/OrcaSlicer_Linux_AppImage_Ubuntu2404_aarch64_V2.4.2.AppImage"

mkdir -p "$tool_dir"
if [ ! -f "$appimage" ]; then
    curl --fail --location --show-error "$url" --output "$appimage"
fi
actual_sha=$(sha256sum "$appimage" | cut -d ' ' -f 1)
if [ "$actual_sha" != "$expected_sha" ]; then
    echo "OrcaSlicer AppImage checksum mismatch" >&2
    exit 1
fi
chmod +x "$appimage"
if [ ! -d "$tool_dir/squashfs-root" ]; then
    extract_dir=$(mktemp -d)
    (cd "$extract_dir" && "$appimage" --appimage-extract >/dev/null)
    mv "$extract_dir/squashfs-root" "$tool_dir/squashfs-root"
    rmdir "$extract_dir"
fi
echo "$tool_dir/squashfs-root"

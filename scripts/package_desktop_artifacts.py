"""Collect distributable installers with hashes and exact source provenance."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--platform", required=True)
args = parser.parse_args()
bundle = ROOT / "desktop/src-tauri/target/release/bundle"
output = ROOT / "build/desktop-artifacts" / args.platform
output.mkdir(parents=True, exist_ok=True)
version = json.loads((ROOT / "frontend/studio/package.json").read_text())["version"]
files = []
for source in sorted(bundle.rglob("*")):
    if not source.is_file() or source.suffix.lower() not in {".exe", ".msi", ".dmg", ".deb", ".appimage", ".rpm"}:
        continue
    relative = source.relative_to(bundle)
    target = output / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    files.append({"file": relative.as_posix(), "bytes": target.stat().st_size, "sha256": digest})
if not files:
    raise SystemExit("No installers found; refusing to publish an empty artifact.")
manifest = {"studio_version": version, "platform": args.platform,
            "source_commit": os.environ.get("GITHUB_SHA", "local-uncommitted-build"),
            "run_url": (os.environ.get("GITHUB_SERVER_URL", "") + "/" +
                        os.environ.get("GITHUB_REPOSITORY", "") + "/actions/runs/" +
                        os.environ.get("GITHUB_RUN_ID", "")) if os.environ.get("GITHUB_RUN_ID") else None,
            "native_installation_check": "pending", "files": files}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(output / "SHA256SUMS.txt").write_text("".join(item["sha256"] + "  " + item["file"] + "\n" for item in files), encoding="utf-8")
print(f"Collected {len(files)} installers in {output}")

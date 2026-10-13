#!/usr/bin/env python3
"""Reconstruct official r1 -> 2026-10-12 (7940 assets) -> 2026-10-13 (8032 assets).

Python 3.9+; standard library only. Obtain this script and chain_manifest.json
from the published repository. By default all update ZIPs are read beside it.
Only --updates-url permits missing update files from this repository's official
raw.githubusercontent.com URL. --download-base
fetches eight public r1 ZIPs; --base instead uses an already extracted r1 tree.
No login, token, Blender, game launch, or asset-script execution is needed.
Use a private, new --work directory with ample free space. Both output trees and downloads are retained; package-owned temporary staging
is removed. Failed runs are not resumable; use a different fresh work directory.
Keep the base, update files, and work directory unchanged while running.
"""
import argparse
import hashlib
import http.client
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request
import zipfile

CHAIN_MANIFEST_SHA256 = "f218e8186d09095c970caf26688460b10add5813e4c50303ac7508f25832cb50"
CHUNK = 4 * 1024 * 1024
EXPECTED_LAYER_IDS = ("layer1_20261012", "layer2_20261013")
EXPECTED_COUNTS = (7940, 8032)
DOWNLOAD_HOSTS = {"github.com", "raw.githubusercontent.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"}
SECOND_BASELINE = "Campus_Cloud_Offline_Candidate_20261012_7940_files"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
RESERVED = {"con", "prn", "aux", "nul"} | {
    prefix + str(n) for prefix in ("com", "lpt") for n in range(1, 10)
}


def fail(message):
    raise ValueError(message)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def require_sha(value):
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        fail("Invalid or unpinned SHA-256")
    return value


def relative_name(value):
    """Reject nonportable paths before pathlib or the OS can normalize them."""
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        fail("Invalid relative path: " + repr(value))
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        fail("Control character in path")
    parts = value.split("/")
    if any(p in ("", ".", "..") or p.endswith((" ", ".")) for p in parts):
        fail("Noncanonical relative path: " + repr(value))
    if any(p.split(".")[0].casefold() in RESERVED for p in parts):
        fail("Reserved device name in path: " + repr(value))
    if PurePosixPath(value).is_absolute():
        fail("Absolute path is forbidden")
    return value


def collision_key(value):
    return unicodedata.normalize("NFC", value).casefold()


def check_no_links(path):
    """Reject symlinks and Windows junctions/reparse points, including ancestors."""
    path = Path(os.path.abspath(str(path)))
    for current in reversed((path,) + tuple(path.parents)):
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            fail("Symlink or reparse path is forbidden: " + str(current))
    return path


def under(root, rel):
    relative_name(rel)
    root = check_no_links(root)
    path = check_no_links(root.joinpath(*rel.split("/")))
    if root not in path.parents:
        fail("Path does not lie strictly under root: " + rel)
    return path


def check_file(path, row):
    check_no_links(path)
    if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        fail("Missing regular file: " + str(path))
    if type(row["bytes"]) is not int or row["bytes"] < 0:
        fail("Invalid expected file size")
    require_sha(row["sha256"])
    if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
        fail("Size/SHA-256 mismatch: " + str(path))


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("Duplicate JSON key: " + key)
        result[key] = value
    return result


def json_bytes(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicate_keys)


def read_pinned_json(path, expected_sha):
    check_no_links(path)
    require_sha(expected_sha)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        fail("Pinned manifest SHA-256 mismatch: " + str(path))
    return json_bytes(raw)


class Inventory:
    """Portable namespace: detects duplicate files, case aliases and prefix conflicts."""
    def __init__(self):
        self.nodes = {}
        self.explicit = set()

    def add(self, rel, is_dir=False, allow_repeated=False):
        relative_name(rel)
        parts = rel.split("/")
        for i in range(1, len(parts) + 1):
            name = "/".join(parts[:i])
            key = collision_key(name)
            kind = "directory" if i < len(parts) or is_dir else "file"
            if key in self.nodes and self.nodes[key] != (name, kind):
                fail("Case, Unicode, or file/directory collision: " + rel)
            self.nodes[key] = (name, kind)
        key = collision_key(rel)
        if key in self.explicit and not allow_repeated:
            fail("Duplicate archive/manifest entry: " + rel)
        self.explicit.add(key)


def asset_rows(rows, count=None):
    if not isinstance(rows, list) or (count is not None and len(rows) != count):
        fail("Incorrect asset manifest count")
    index, namespace = {}, Inventory()
    for row in rows:
        rel = relative_name(row["path"])
        if not rel.startswith("assets/"):
            fail("Only assets/ entries are permitted: " + rel)
        namespace.add(rel)
        if type(row["bytes"]) is not int or row["bytes"] < 0:
            fail("Invalid asset size")
        require_sha(row["sha256"])
        index[rel] = (row["bytes"], row["sha256"])
    return index


def zip_members(archive):
    namespace, result = Inventory(), []
    for member in archive.infolist():
        name = member.filename
        if member.orig_filename != name:
            fail("NUL or truncated ZIP name")
        directory = member.is_dir()
        rel = relative_name(name[:-1] if directory else name)
        mode = member.external_attr >> 16
        file_type = stat.S_IFMT(mode)
        if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
            fail("ZIP links or special files are forbidden: " + rel)
        if bool(file_type == stat.S_IFDIR) != directory and file_type:
            fail("Inconsistent ZIP entry type: " + rel)
        if member.external_attr & 0x400:
            fail("ZIP reparse entries are forbidden: " + rel)
        if member.flag_bits & 1:
            fail("Encrypted ZIP entries are forbidden")
        namespace.add(rel, directory)
        result.append((member, rel, directory))
    return result


def safe_extract(archives, destination, root_name, allow_identical_metadata=False):
    """Extract only regular files; read every entry to EOF for actual CRC checks.

    Public r1 repeats root metadata across eight ZIPs. Only identical bytes at
    the identical non-assets path may repeat; no file is overwritten.
    """
    relative_name(root_name)
    if "/" in root_name:
        fail("Archive root must be one directory")
    destination = check_no_links(destination)
    if destination.exists():
        fail("Extraction directory already exists: " + str(destination))
    destination.mkdir(mode=0o700, parents=False)
    namespace, written = Inventory(), {}
    for path in archives:
        with zipfile.ZipFile(path) as archive:
            for member, rel, directory in zip_members(archive):
                if rel != root_name and not rel.startswith(root_name + "/"):
                    fail("Unexpected archive root: " + rel)
                metadata = rel.startswith(root_name + "/") and not rel.startswith(root_name + "/assets/") and rel != root_name + "/assets"
                repeated = rel in written
                namespace.add(rel, directory, allow_repeated=directory or (metadata and allow_identical_metadata))
                target = under(destination, rel)
                if directory:
                    target.mkdir(parents=True, exist_ok=True)
                    with archive.open(member) as stream:
                        if stream.read(1):
                            fail("Nonempty directory entry")
                    continue
                target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                h, size = hashlib.sha256(), 0
                if repeated:
                    if not (metadata and allow_identical_metadata):
                        fail("Repeated file is forbidden: " + rel)
                    with archive.open(member) as stream:
                        for block in iter(lambda: stream.read(CHUNK), b""):
                            h.update(block)
                            size += len(block)
                    if (size, h.hexdigest()) != written[rel]:
                        fail("Conflicting repeated metadata: " + rel)
                else:
                    with archive.open(member) as stream, target.open("xb") as out:
                        for block in iter(lambda: stream.read(CHUNK), b""):
                            out.write(block)
                            h.update(block)
                            size += len(block)
                    if size != member.file_size:
                        fail("Truncated ZIP member: " + rel)
                    written[rel] = (size, h.hexdigest())
    return under(destination, root_name)


def verify_assets(root, rows, count, label):
    expected = asset_rows(rows, count)
    assets = under(root, "assets")
    if not assets.is_dir():
        fail("Base/output must contain assets/: " + str(root))
    observed = set()
    for directory, dirs, files in os.walk(assets, followlinks=False):
        for name in dirs + files:
            path = check_no_links(Path(directory) / name)
            if not path.is_dir() and not path.is_file():
                fail("Special file in asset tree: " + str(path))
        for name in files:
            observed.add((Path(directory) / name).relative_to(root).as_posix())
    if observed != set(expected):
        fail(label + " inventory mismatch; missing=" + str(sorted(set(expected) - observed)[:5]) + "; extra=" + str(sorted(observed - set(expected))[:5]))
    print("Checking " + label + ": " + str(count) + " assets...", flush=True)
    for i, row in enumerate(rows, 1):
        check_file(under(root, row["path"]), row)
        if i % 1000 == 0:
            print("  verified", i, "/", count, flush=True)
    print(label + ": exact asset inventory and SHA-256 PASS", flush=True)


def public_https(url, resolve=False):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment or parsed.port not in (None, 443):
        fail("Only credential-free public HTTPS URLs are permitted")
    host = parsed.hostname.lower()
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
        fail("Local/private download destination is forbidden")
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        addresses = []
    if resolve:
        addresses += [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)]
    if any(not address.is_global for address in addresses):
        fail("Local/private download destination is forbidden")
    return url


def official_download_url(url, resolve=False):
    public_https(url, resolve=resolve)
    if urllib.parse.urlsplit(url).hostname not in DOWNLOAD_HOSTS:
        fail("Only official GitHub public download hosts are permitted")
    return url


def official_updates_url(url):
    parsed = urllib.parse.urlsplit(official_download_url(url))
    if parsed.hostname != "raw.githubusercontent.com" or parsed.query or not re.fullmatch(r"/YansongG-HKU/UChicago-Campus-CS2-Assets/[A-Za-z0-9._-]+/updates/20261013/?", parsed.path):
        fail("--updates-url must point to raw.githubusercontent.com/YansongG-HKU/UChicago-Campus-CS2-Assets/<ref>/updates/20261013")
    return url


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        official_download_url(newurl, resolve=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)



class PublicHTTPSConnection(http.client.HTTPSConnection):
    def connect(self):
        if self._tunnel_host:
            fail("Proxy tunnels are not supported for public downloads")
        addresses = socket.getaddrinfo(self.host, self.port, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
            fail("Local/private connection destination is forbidden")
        last_error = None
        for family, socktype, proto, _canonical, sockaddr in addresses:
            connection = socket.socket(family, socktype, proto)
            try:
                connection.settimeout(self.timeout)
                if self.source_address:
                    connection.bind(self.source_address)
                # Use exactly the validated address, with no second DNS lookup.
                connection.connect(sockaddr)
                self.sock = self._context.wrap_socket(connection, server_hostname=self.host)
                return
            except OSError as exc:
                connection.close()
                last_error = exc
        raise last_error


class PublicHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(PublicHTTPSConnection, req, context=self._context)


def download(url, target, row):
    official_download_url(url, resolve=True)
    target = check_no_links(target)
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if target.exists():
        fail("Download target already exists: " + str(target))
    print("Downloading", target.name, flush=True)
    # Disable proxy discovery, cookies, netrc and authentication: public files only.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), PublicRedirect(), PublicHTTPSHandler())
    request = urllib.request.Request(url, headers={"User-Agent": "Campus-public-reconstruction/1"})
    with opener.open(request, timeout=120) as response, target.open("xb") as out:
        official_download_url(response.geturl())
        total = 0
        for block in iter(lambda: response.read(CHUNK), b""):
            total += len(block)
            if total > row["bytes"]:
                fail("Download exceeded its pinned size: " + target.name)
            out.write(block)
    check_file(target, row)


def prepare_layer(layer, files, workspace):
    paths = [layer["start_zip"]] + layer["part_zips"]
    root = safe_extract([files[path] for path in paths], workspace / layer["id"], layer["root"])
    parts = read_pinned_json(under(root, "parts.json"), layer["parts_sha256"])
    output_rows = read_pinned_json(under(root, "asset_manifest.json"), layer["manifest_sha256"])
    asset_rows(output_rows, layer["final_count"])
    installer = under(root, layer["installer"])
    require_sha(layer["installer_sha256"])
    if not installer.is_file() or sha256(installer) != layer["installer_sha256"]:
        fail("Installer hash mismatch")
    if parts.get("format") != "campus-delta-parts-1" or parts.get("part_count") != len(parts["parts"]) or len(parts["parts"]) != len(layer["part_zips"]):
        fail("Invalid parts format/count")
    if layer["id"] == EXPECTED_LAYER_IDS[1] and parts.get("baseline") != SECOND_BASELINE:
        fail("Incorrect second-layer baseline")
    namespace = Inventory()
    delta = workspace / (layer["id"] + ".delta.zip")
    with delta.open("xb") as out:
        for row, zip_path in zip(parts["parts"], layer["part_zips"]):
            namespace.add(row["path"])
            if PurePosixPath(zip_path).name != row["zip_file"] or sha256(files[zip_path]) != require_sha(row["zip_sha256"]):
                fail("Part ZIP order/hash mismatch")
            part = under(root, row["path"])
            check_file(part, row)
            with part.open("rb") as stream:
                shutil.copyfileobj(stream, out, CHUNK)
    check_file(delta, {"bytes": parts["delta_bytes"], "sha256": parts["delta_sha256"]})
    with zipfile.ZipFile(delta) as archive:
        members = zip_members(archive)
        names = {rel: member for member, rel, is_dir in members if not is_dir}
        if "delta_manifest.json" not in names:
            fail("Delta manifest is missing")
        for member, rel, is_dir in members:
            if is_dir or (rel != "delta_manifest.json" and not re.fullmatch(r"literals/[0-9a-f]{64}", rel)):
                fail("Unexpected delta ZIP member: " + rel)
            h = hashlib.sha256()
            with archive.open(member) as stream:
                for block in iter(lambda: stream.read(CHUNK), b""):
                    h.update(block)
            if rel.startswith("literals/") and h.hexdigest() != rel.split("/")[1]:
                fail("Delta literal hash mismatch")
        manifest = json_bytes(archive.read("delta_manifest.json"))
        if manifest.get("format") != "campus-content-delta-1":
            fail("Invalid content-delta format")
        if layer["id"] == EXPECTED_LAYER_IDS[1] and manifest.get("baseline") != SECOND_BASELINE:
            fail("Wrong second-layer delta baseline")
        original = asset_rows(manifest["original_manifest"], layer["base_count"])
        final = asset_rows(manifest["output_manifest"], layer["final_count"])
        if final != asset_rows(output_rows):
            fail("Delta output differs from pinned asset manifest")
        patched = asset_rows(manifest["patched_files"])
        if set(original) - set(final) or {**original, **patched} != final:
            fail("Delta inventory cannot produce expected output")
        for row in manifest["patched_files"]:
            length = 0
            for op in row["ops"]:
                if not isinstance(op, list) or not op:
                    fail("Invalid delta operation")
                if op[0] == "C" and len(op) == 4:
                    relative_name(op[1])
                    if op[1] not in original or any(type(n) is not int or n < 0 for n in op[2:]) or op[2] + op[3] > original[op[1]][0]:
                        fail("Invalid copy operation")
                    length += op[3]
                elif op[0] == "L" and len(op) == 2:
                    require_sha(op[1])
                    member = names.get("literals/" + op[1])
                    if member is None:
                        fail("Missing delta literal")
                    length += member.file_size
                else:
                    fail("Unknown delta operation")
            if length != row["bytes"]:
                fail("Delta operations have incorrect total size")
    # These are only freshly extracted package parts inside our new workspace.
    # The assembled delta is now independently pinned, so release duplicate data.
    for row in parts["parts"]:
        under(root, row["path"]).unlink()
    current = sum(size for size, digest in original.values())
    peak = current
    for row in manifest["patched_files"]:
        peak = max(peak, current + row["bytes"])
        current += row["bytes"] - original.get(row["path"], (0, ""))[0]
    return {"installer": installer, "delta": delta, "original": manifest["original_manifest"], "final": output_rows, "peak_asset_bytes": peak, "delta_bytes": parts["delta_bytes"]}


def load_chain(path):
    chain = read_pinned_json(path, CHAIN_MANIFEST_SHA256)
    layers = chain["layers"]
    if len(layers) != 2 or tuple(row["id"] for row in layers) != EXPECTED_LAYER_IDS:
        fail("Unexpected update-chain layers/order")
    if tuple(row["final_count"] for row in layers) != EXPECTED_COUNTS or layers[1]["base_count"] != EXPECTED_COUNTS[0]:
        fail("Incorrect update-chain asset counts")
    if layers[1]["manifest_sha256"] != require_sha(chain["final_manifest_sha256"]):
        fail("Final manifest pin differs from second layer")
    namespace, records = Inventory(), {}
    for row in chain["files"]:
        namespace.add(row["path"])
        require_sha(row["sha256"])
        if type(row["bytes"]) is not int or row["bytes"] < 0:
            fail("Invalid update-file size")
        records[row["path"]] = row
    selected = []
    for layer, part_count in zip(layers, (12, 21)):
        if len(layer["part_zips"]) != part_count:
            fail("Unexpected layer ZIP count")
        for path in [layer["start_zip"]] + layer["part_zips"]:
            if path not in records or not path.endswith(".zip"):
                fail("Required ZIP missing from pinned file manifest")
            selected.append(path)
    if len(set(selected)) != len(selected):
        fail("A ZIP appears in more than one layer/position")
    base = chain["public_base_archives"]
    if base["required_archive_count"] != 8 or len(base["archives"]) != 8:
        fail("Exactly eight public r1 archives are required")
    base_names = Inventory()
    for row in base["archives"]:
        base_names.add(row["filename"])
        if "/" in row["filename"]:
            fail("Base archive name must be a filename")
        require_sha(row["sha256"])
        if type(row["bytes"]) is not int or row["bytes"] < 0:
            fail("Invalid base archive size")
        public_https(row["url"])
    return chain, records


def run_installer(stage, base, output, workspace):
    check_no_links(base)
    check_no_links(output)
    if output.exists():
        fail("Output already exists; never overwriting: " + str(output))
    temp = workspace / "installer_temp"
    temp.mkdir(mode=0o700, exist_ok=True)
    env = dict(os.environ, TMPDIR=str(temp), TEMP=str(temp), TMP=str(temp))
    # -I isolates Python imports from cwd, user-site and PYTHON* variables.
    subprocess.run([sys.executable, "-I", "-B", str(stage["installer"]), "--original", str(base), "--output", str(output), "--delta", str(stage["delta"])], check=True, cwd=workspace, env=env)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--base", type=Path, help="Existing official r1 root containing assets/; read-only")
    source.add_argument("--download-base", action="store_true", help="Download and extract all eight pinned public r1 ZIPs")
    parser.add_argument("--work", required=True, type=Path, help="New, nonexistent directory; both asset outputs/downloads retained")
    parser.add_argument("--updates-dir", type=Path, default=Path(__file__).absolute().parent, help="Directory containing chain_manifest.json and update ZIP paths; default: beside this script")
    parser.add_argument("--updates-url", help="Official raw.githubusercontent.com repo/<ref>/updates/20261013 URL for missing update files only")
    args = parser.parse_args(argv)
    updates = check_no_links(args.updates_dir)
    chain, records = load_chain(under(updates, "chain_manifest.json"))
    work = check_no_links(args.work)
    base = check_no_links(args.base) if args.base else None
    if work.exists() or not work.parent.is_dir():
        fail("--work must be nonexistent with an existing parent directory")
    for source_root in (updates, base):
        if source_root and (source_root == work or source_root in work.parents or work in source_root.parents):
            fail("--work must be separate from update/base trees")
    if base and not under(base, "assets").is_dir():
        fail("--base must be the extracted r1 root containing assets/")
    if args.updates_url:
        official_updates_url(args.updates_url)
    print("Space warning: budget 16 GB+ free with --download-base, or 8 GB+ with an external --base. Exact free-space checks follow package validation. Both asset trees/downloads are retained; only package-owned temporary staging is removed.", flush=True)
    work.mkdir(mode=0o700)
    files = {}
    for rel, row in records.items():
        local = under(updates, rel)
        if local.exists():
            check_file(local, row)  # Never replace a mismatched local file by downloading.
            files[rel] = local
        else:
            if not args.updates_url:
                fail("Missing update file: " + rel + "; download it or explicitly provide --updates-url")
            target = under(work, "downloaded_updates/" + rel)
            url = args.updates_url.rstrip("/") + "/" + urllib.parse.quote(rel, safe="/")
            download(url, target, row)
            files[rel] = target
    print("All update files match pinned size/SHA-256; validating both layers before any installer runs.", flush=True)
    with tempfile.TemporaryDirectory(prefix="verified_package_", dir=str(work)) as staging_name:
        staging = Path(staging_name)
        stages = [prepare_layer(layer, files, staging) for layer in chain["layers"]]
        if asset_rows(stages[0]["final"]) != asset_rows(stages[1]["original"]):
            fail("First output is not exactly the second layer's baseline")
        output_peak = max(stages[0]["peak_asset_bytes"], sum(row["bytes"] for row in stages[0]["final"]) + stages[1]["peak_asset_bytes"] - stages[0]["delta_bytes"])
        required_space = output_peak + 100_000_000
        if args.download_base:
            required_space += sum(row["bytes"] for row in chain["public_base_archives"]["archives"]) + sum(row["bytes"] for row in stages[0]["original"])
        print("Additional free space required after staging:", required_space, "bytes (includes 100 MB margin)", flush=True)
        if shutil.disk_usage(work).free < required_space:
            fail("Insufficient free space for this exact reconstruction; need " + str(required_space) + " additional bytes")
        if args.download_base:
            archives = []
            for row in chain["public_base_archives"]["archives"]:
                path = under(work, "base_archives/" + row["filename"])
                download(row["url"], path, row)
                archives.append(path)
            base = safe_extract(archives, work / "extracted_base", chain["public_base_archives"]["extracted_root"], allow_identical_metadata=True)
        first = work / "Campus_Cloud_Offline_Candidate_20261012"
        final = work / "Campus_Strict_20261013"
        verify_assets(base, stages[0]["original"], chain["layers"][0]["base_count"], "Official r1 baseline")
        run_installer(stages[0], base, first, work)
        verify_assets(first, stages[0]["final"], 7940, "First output / second baseline")
        read_pinned_json(first / "asset_manifest.json", chain["layers"][0]["manifest_sha256"])
        # First output has passed all hashes; this private assembly is no longer needed.
        stages[0]["delta"].unlink()
        run_installer(stages[1], first, final, work)
        verify_assets(final, stages[1]["final"], 8032, "Latest final output")
        # Exact bytes of the installer's manifest are also pinned, beyond row hashes.
        read_pinned_json(final / "asset_manifest.json", chain["final_manifest_sha256"])
        print("SUCCESS: 8032 assets match the latest pinned inventory and SHA-256. Output: " + str(final), flush=True)
        print("Intermediate, downloads and original base retained; package-only temporary staging removed at exit. Offline integrity is verified; game acceptance is not implied.", flush=True)



if __name__ == "__main__":
    try:
        if sys.version_info < (3, 9):
            fail("Python 3.9 or newer is required")
        main()
    except (Exception, KeyboardInterrupt) as exc:
        print("STOPPED: " + str(exc) + ". Existing input files were not modified. Partial work is retained; use a new --work directory.", file=sys.stderr)
        sys.exit(1)

"""Recompress only PNG IDAT, retaining decoded scanlines and all other chunks."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

from PIL import Image

ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2])
REPORT.mkdir(exist_ok=False)
SIGNATURE = b'\x89PNG\r\n\x1a\n'


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def chunks(data):
    assert data.startswith(SIGNATURE)
    stop = 8
    while stop < len(data):
        length = struct.unpack_from('>I', data, stop)[0]
        tag = data[stop + 4:stop + 8]
        raw = data[stop + 8:stop + 8 + length]
        end = stop + 12 + length
        assert zlib.crc32(tag + raw) == struct.unpack_from('>I', data, end - 4)[0]
        yield tag, raw, data[stop:end]
        stop = end
    assert stop == len(data)


def scanlines(parts):
    return zlib.decompress(b''.join(raw for tag, raw, _ in parts if tag == b'IDAT'))


def optimize(path):
    data = path.read_bytes()
    parts = list(chunks(data))
    if any(tag in {b'acTL', b'fdAT'} for tag, _, _ in parts):
        raise ValueError(f'Unexpected animated texture: {path}')
    with Image.open(path) as image:
        image.load()
        width, height = image.size
        mode = image.mode
    new = data
    scanline_sha = None
    relative = path.relative_to(ROOT).as_posix()
    if path in selected:
        original = scanlines(parts)
        scanline_sha = checksum(original)
        compressed = zlib.compress(original, 9)
        tagged = b'IDAT' + compressed
        merged = struct.pack('>I', len(compressed)) + tagged + struct.pack('>I', zlib.crc32(tagged))
        segments = [SIGNATURE]
        first = True
        for tag, _, encoded in parts:
            if tag != b'IDAT':
                segments.append(encoded)
            elif first:
                segments.append(merged)
                first = False
        candidate = b''.join(segments)
        if len(candidate) < len(data):
            repl = list(chunks(candidate))
            assert [encoded for tag, _, encoded in parts if tag != b'IDAT'] == [
                encoded for tag, _, encoded in repl if tag != b'IDAT']
            assert scanlines(repl) == original
            new = candidate
            temporary = path.with_suffix('.png.pending')
            temporary.write_bytes(new)
            with Image.open(temporary) as image:
                image.load()
                assert (image.size, image.mode) == ((width, height), mode)
            temporary.replace(path)
    return {'path': relative, 'size': [width,height], 'mode': mode, 'scanline_sha256': scanline_sha,
            'before_bytes': len(data), 'after_bytes': len(new), 'before_sha256': checksum(data),
            'after_sha256': checksum(new)}



all_pngs = sorted(ROOT.glob('*/*/**/*.png'))
# Focus recompression on the larger published imports and the equivalent Chicago copies.
selected = {p for p in all_pngs if p.stat().st_size >= 150_000}
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(optimize, all_pngs))
(REPORT / 'png-verified.json').write_text(json.dumps(results, indent=2) + '\n')
print('PNG', len(results), 'optimized', sum(x['after_bytes'] < x['before_bytes'] for x in results),
      'saved', sum(x['before_bytes'] - x['after_bytes'] for x in results), flush=True)

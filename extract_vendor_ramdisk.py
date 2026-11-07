#!/usr/bin/env python3
"""Extract the vendor ramdisk (and its kernel modules) from a stock XOS 16.3
boot/vendor_boot image pair.

The XOS 16.3 vendor_boot image stores a zstd compressed cpio archive which
contains the boot-critical kernel modules (modules.load) together with the
first stage fstab.

Usage:
    extract_vendor_ramdisk.py <vendor_boot.img> <output_dir>
"""

import os
import struct
import sys

try:
    import zstandard as zstd
except ImportError:
    sys.exit('error: the "zstandard" python module is required')


def read_vendor_boot(path):
    """Return the raw (still compressed) vendor ramdisk payload."""
    with open(path, 'rb') as f:
        data = f.read()
    if data[:8] != b'VNDRBOOT':
        raise SystemExit('error: %s is not a vendor_boot image' % path)
    header_version, page_size = struct.unpack('<II', data[8:16])
    ramdisk_size, ramdisk_addr = struct.unpack('<IQ', data[16:28])
    print('vendor_boot header v%d, page size %d' % (header_version, page_size))
    print('vendor ramdisk: %d bytes' % ramdisk_size)
    # The payload starts right after the (page aligned) header.
    offset = page_size
    return data[offset:]


def decompress(payload):
    dctx = zstd.ZstdDecompressor()
    return dctx.decompressobj().decompress(payload)


def parse_cpio(blob):
    """Yield (name, mode, data) for every entry of a newc cpio archive."""
    pos = 0
    while pos < len(blob):
        if blob[pos:pos + 6] != b'070701':
            break
        fields = [int(blob[pos + 6 + i * 8:pos + 6 + (i + 1) * 8], 16)
                  for i in range(13)]
        namesize = fields[11]
        filesize = fields[6]
        mode = fields[1]
        name = blob[pos + 110:pos + 110 + namesize - 1].decode()
        header = (110 + namesize + 3) & ~3
        data = blob[pos + header:pos + header + filesize]
        pos += header + ((filesize + 3) & ~3)
        if name == 'TRAILER!!!':
            break
        yield name, mode, data


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    img, outdir = sys.argv[1], sys.argv[2]

    blob = decompress(read_vendor_boot(img))
    print('decompressed vendor ramdisk: %d bytes' % len(blob))

    count = 0
    for name, mode, data in parse_cpio(blob):
        # Only the kernel modules are of interest for the kernel tree; the
        # sepolicy and the file contexts are rebuilt by the build system.
        if not name.startswith('lib/modules/'):
            continue
        target = os.path.join(outdir, name)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'wb') as f:
            f.write(data)
        count += 1
    print('extracted %d files into %s' % (count, outdir))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Dump or verify a LuCI .lmo compiled translation catalog.

The format below is not folklore: it is read straight off luci-base's own
writer and reader, src/po2lmo.c and src/lib/lmo.c.

File layout -- there is no header:

    [0, idx_offset)          msgstr bytes, back to back. Each entry's data is
                             NUL-padded up to a 4-byte boundary and the next
                             entry starts right after, so offsets stay aligned.
    [idx_offset, size-4)     N index entries of 16 bytes, sorted by key_id
                             ascending (po2lmo qsorts them before writing).
    [size-4, size)           big-endian u32: idx_offset.

N is (size - idx_offset - 4) / 16.

Each index entry is four big-endian u32s, in this order:

    key_id    sfh_hash(msgid, len, len)          -- see below
    val_id    NOT a hash, despite the name. po2lmo computes the msgstr's hash
              and then overwrites the field with plural_num + 1. For a
              translation entry in a catalog without plurals that is 1. The
              one exception is the entry po2lmo synthesises from the PO
              header's "Plural-Forms:" line, which it writes with key_id = 0
              and val_id = 0.
    offset    where this entry's msgstr starts in the file
    length    its length in bytes

The hash is Paul Hsieh's SuperFastHash (sfh_hash in lmo.c) seeded with the
string's own length rather than 0. The msgid text is never stored -- only its
hash -- so a catalog cannot be read back into msgids without the .po it was
built from. That is what `verify` is for.

Usage:
    lmo.py dump   FILE.lmo
    lmo.py verify FILE.lmo FILE.po
"""

import struct
import sys

M32 = 0xFFFFFFFF


def _get16(b, i):
    # lmo.h's sfh_get16 on a little-endian host
    return b[i] | (b[i + 1] << 8)


def sfh_hash(data, init):
    """Paul Hsieh's SuperFastHash, as in luci-base src/lib/lmo.c."""
    n = len(data)
    if n <= 0:
        return 0

    h = init & M32
    rem = n & 3
    i = 0

    for _ in range(n >> 2):
        h = (h + _get16(data, i)) & M32
        tmp = ((_get16(data, i + 2) << 11) ^ h) & M32
        h = ((h << 16) ^ tmp) & M32
        i += 4
        h = (h + (h >> 11)) & M32

    if rem == 3:
        h = (h + _get16(data, i)) & M32
        h ^= (h << 16) & M32
        c = data[i + 2]
        if c >= 128:
            c -= 256
        h ^= (c << 18) & M32
        h = (h + (h >> 11)) & M32
    elif rem == 2:
        h = (h + _get16(data, i)) & M32
        h ^= (h << 11) & M32
        h = (h + (h >> 17)) & M32
    elif rem == 1:
        c = data[i]
        if c >= 128:
            c -= 256
        h = (h + c) & M32
        h ^= (h << 10) & M32
        h = (h + (h >> 1)) & M32

    h ^= (h << 3) & M32
    h = (h + (h >> 5)) & M32
    h ^= (h << 4) & M32
    h = (h + (h >> 17)) & M32
    h ^= (h << 25) & M32
    h = (h + (h >> 6)) & M32
    return h & M32


def key_hash(msgid):
    """po2lmo's key_id: sfh_hash(key, len, len).

    po2lmo hashes the msgid as written in the .po (it does not collapse
    whitespace), while the reader goes through lmo_canon_hash(), which does.
    The two agree for any msgid without a run of whitespace, which is every
    string in these catalogs; a msgid that needs the canonical form is
    rejected rather than hashed the wrong way.
    """
    b = msgid.encode("utf-8")
    canon = " ".join(msgid.split())
    if canon != msgid:
        raise ValueError("msgid needs canonicalisation: %r" % msgid)
    return sfh_hash(b, len(b))


def load(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 4:
        raise ValueError("%s is too short to be an .lmo" % path)
    idx = struct.unpack(">I", data[-4:])[0]
    if idx >= len(data):
        raise ValueError("%s: index offset %d past end" % (path, idx))
    n = (len(data) - idx - 4) // 16
    entries = []
    for k in range(n):
        entries.append(struct.unpack(">IIII", data[idx + 16 * k: idx + 16 * k + 16]))
    return data, entries


def parse_po(path):
    """Yield (msgid, msgstr). Comments and obsolete entries are skipped."""
    out = []
    msgid = msgstr = None
    field = None

    def unescape(s):
        res, i = [], 0
        while i < len(s):
            if s[i] == "\\" and i + 1 < len(s):
                res.append({"n": "\n", "t": "\t", "r": "\r"}.get(s[i + 1], s[i + 1]))
                i += 2
            else:
                res.append(s[i])
                i += 1
        return "".join(res)

    def flush():
        if msgid is not None and msgstr is not None:
            out.append((msgid, msgstr))

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#~") or line.startswith("#"):
                continue
            if line.startswith("msgid "):
                flush()
                msgid, msgstr, field = unescape(line[6:].strip()[1:-1]), None, "id"
            elif line.startswith("msgid_plural "):
                field = "plural"
            elif line.startswith("msgstr "):
                msgstr, field = unescape(line[7:].strip()[1:-1]), "str"
            elif line.startswith("msgstr["):
                field = "plural"
            elif line.startswith('"') and field is not None:
                chunk = unescape(line.strip()[1:-1])
                if field == "id":
                    msgid += chunk
                elif field == "str":
                    msgstr += chunk
            else:
                field = None
    flush()
    return out


def cmd_dump(path):
    data, entries = load(path)
    print("%s: %d bytes, %d entries" % (path, len(data), len(entries)))
    for key_id, val_id, off, ln in entries:
        raw = data[off:off + ln]
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = repr(raw)
        print("  %08x  val_id=%d  @%-5d %3d  %s" % (key_id, val_id, off, ln, text))


def cmd_verify(lmo_path, po_path):
    data, entries = load(lmo_path)
    index = {key_id: (val_id, off, ln) for key_id, val_id, off, ln in entries}
    pairs = parse_po(po_path)
    ok = bad = skipped = 0

    for msgid, msgstr in pairs:
        if msgid == "":
            skipped += 1  # the PO header; po2lmo never emits it as a lookup key
            continue
        if msgstr == "":
            skipped += 1
            continue
        if msgstr == msgid:
            skipped += 1  # po2lmo drops these: key_id == val_id
            continue
        want = msgstr.encode("utf-8")
        try:
            key_id = key_hash(msgid)
        except ValueError as err:
            print("  SKIP  %s" % err)
            skipped += 1
            continue
        got = index.get(key_id)
        if got is None:
            print("  MISS  %08x  %r" % (key_id, msgid))
            bad += 1
            continue
        val_id, off, ln = got
        if data[off:off + ln] != want:
            print("  DIFF  %08x  %r\n        want %r\n        got  %r"
                  % (key_id, msgid, want, data[off:off + ln]))
            bad += 1
            continue
        ok += 1

    print("%s vs %s: %d ok, %d bad, %d skipped, %d entries in file"
          % (lmo_path, po_path, ok, bad, skipped, len(entries)))
    return 1 if bad else 0


def main(argv):
    if len(argv) == 3 and argv[1] == "dump":
        cmd_dump(argv[2])
        return 0
    if len(argv) == 4 and argv[1] == "verify":
        return cmd_verify(argv[2], argv[3])
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

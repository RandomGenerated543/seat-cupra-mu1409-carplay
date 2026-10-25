#!/usr/bin/env python3
"""Read-only offline decoder for observed MU1440 DebugSPI 0x0110/f902 records.

Selects ONLY record tag 0x002e containing five type-1 signed BE int32
elements. The numeric tag is not claimed to equal a DSI method number.
Confirm physical left/right and direction via independent operator notes.
No communication with the vehicle; no input file modification.
"""
import argparse
import csv
import struct
import sys
from collections import Counter
from pathlib import Path

SYNC = b'\x80MLP'
COLUMNS = ('ordinal', 'monotonic_ms', 'keyboard', 'encoder_id',
           'signed_increment', 'extra', 'validity', 'mlp_frame', 'raw_offset')


def decode(raw):
    offset = 0
    counts = Counter()
    events = []
    while offset < len(raw):
        if len(raw) - offset < 26:
            raise ValueError('incomplete MLP frame at offset %d' % offset)
        size = struct.unpack_from('>I', raw, offset)[0] + 4
        if size < 26 or size > 262144 or size > len(raw) - offset:
            raise ValueError('invalid/truncated MLP length at offset %d' % offset)
        if raw[offset+4:offset+8] != SYNC:
            raise ValueError('MLP sync lost at offset %d' % offset)
        frame = raw[offset:offset+size]
        if struct.unpack_from('>I', frame, 22)[0] != size - 26:
            raise ValueError('MLP payload length mismatch at offset %d' % offset)
        counts['frames'] += 1
        pay = frame[26:]
        if frame[20] == 1 and pay.startswith(b'\xff\x01\x10'):
            counts['inner_0110'] += 1
            if len(pay) == 76 and pay[5:7] == b'\xf9\x02' and pay[37:39] == b'\x00\x2e':
                # Two observed prefix fields: 4 and 5. Do not assign their
                # full protocol meaning without an independently verified schema.
                if pay[43:47] == b'\x00\x00\x00\x04' and pay[47:51] == b'\x00\x00\x00\x05':
                    vals = []
                    for j in range(5):
                        at = 51 + 5*j
                        if pay[at] != 1:
                            break
                        vals.append(struct.unpack_from('>i', pay, at+1)[0])
                    if len(vals) == 5:
                        events.append((len(events)+1,
                            struct.unpack_from('>I', pay, 11)[0],
                            *vals, counts['frames'], offset))
                        counts['f902_002e_5int'] += 1
                    else:
                        counts['candidate_rejected_bad_type'] += 1
                else:
                    counts['candidate_rejected_bad_vector'] += 1
        elif frame[20] == 1 and pay.startswith(b'\xff\x01\x04'):
            counts['inner_0104'] += 1
        offset += size
    counts['bytes'] = len(raw)
    return events, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw_bin', type=Path, help='Private debugspi-original.bin')
    parser.add_argument('-o', '--output', type=Path, help='CSV output (default: stdout)')
    args = parser.parse_args()
    try:
        events, counts = decode(args.raw_bin.read_bytes())
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.output:
        with args.output.open('w', newline='', encoding='utf-8') as out:
            writer = csv.writer(out)
            writer.writerow(COLUMNS)
            writer.writerows(events)
    else:
        writer = csv.writer(sys.stdout)
        writer.writerow(COLUMNS)
        writer.writerows(events)
    print('SUMMARY ' + ' '.join('%s=%s' % pair for pair in sorted(counts.items())),
          file=sys.stderr)
    print('NOTICE: physical side and zoom direction depend on operator notes.',
          file=sys.stderr)


if __name__ == '__main__':
    main()

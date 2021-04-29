#!/usr/bin/env python3
import argparse
import csv
from time import strftime, gmtime

import opentimelineio as otio
from tabulate import tabulate


def get_args():
    """Get command line arguments."""
    parser = argparse.ArgumentParser()
    # TODO add handling to determine if file exists
    parser.add_argument('-f', '--file', required=True, help='file to read')
    parser.add_argument('-o', '--output', help='filename to output')
    return parser.parse_args()


def make_timecode(frame, rate):
    """Make timecode from frame and rate."""
    seconds = int(frame // rate)
    remainder = int(frame % rate)

    return f'{strftime("%H:%M:%S", gmtime(seconds))}.{remainder:02}'


def main():
    """Main"""
    args = get_args()

    timeline = otio.adapters.read_from_file(args.file)
    output = []
    rate = timeline.duration().rate
    for track in timeline.tracks:
        for clip in track:
            if not clip.name:
                continue
            parent = clip.range_in_parent()
            start = float(parent.start_time.value)
            end = float(parent.end_time_exclusive().value)

            row = {'name': clip.name,
                   'start': round(start, 2),
                   'end': round(end, 2),
                   'rate': round(rate, 3),
                   'timecode_start': make_timecode(start, rate),
                   'timecode_end': make_timecode(end, rate)}
            output.append(row)

    media = sorted(output, key=lambda x: x['start'])
    print(tabulate(media, headers='keys', tablefmt="simple"))

    if args.output:
        with open(args.output, 'w') as fp:
            writer = csv.DictWriter(fp, media[0].keys())
            writer.writeheader()
            writer.writerows(media)


if __name__ == '__main__':
    main()

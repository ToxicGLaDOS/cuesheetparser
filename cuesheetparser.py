#!/usr/bin/env python

import re
# cue spec taken from https://wyday.com/cuesharp/specification.php

def rem(lines: list[str]) -> dict[str, str]:
    line = lines.pop(0)
    matches = re.match(r"REM ([A-Z]+) (.*)", line)

    if not matches:
        raise ValueError(f"Couldn't parse REM line. Line was: '{line}'")

    key = matches.group(1)
    value = matches.group(2)
    return {key: value}

def performer(lines: list[str]) -> str:
    line = lines.pop(0)
    matches = re.match(r'PERFORMER "(.*)"', line)

    if not matches:
        raise ValueError(f"Couldn't parse PERFORMER line. Line was: '{line}'")

    perfomer = matches.group(1)

    return perfomer

# This is used for the album title and the track title
def title(lines: list[str]) -> str:
    line = lines.pop(0)
    matches = re.match(r'TITLE "(.*)"', line)

    if not matches:
        raise ValueError(f"Couldn't parse TITLE line. Line was: '{line}'")

    t = matches.group(1)

    return t

def file(lines: list[str]) -> dict[str, str|list|dict|None]:
    line = lines.pop(0)
    matches = re.match(r'FILE "(.*)" (BINARY|MOTOROLA|AIFF|WAVE|MP3)?', line)

    if not matches:
        raise ValueError(f"Couldn't parse FILE line. Line was: '{line}'")

    file_name = matches.group(1)
    file_format = matches.group(2)

    if file_format == "":
        file_format = None

    file_data = {'file_name': file_name, 'file_format': file_format, 'tracks': [], 'comments': {}}

    while len(lines) > 0:
        line = lines[0]
        if line.startswith("REM"):
            file_data['comments'].update(rem(lines))
        elif line.startswith("TRACK"):
            file_data['tracks'].append(track(lines))
        elif line.startswith("FILE"):
            return file_data
        else:
            if ' ' in line:
                command = line.split(' ')[0]
                raise ValueError(f'Unexpected command in FILE section. Expected REM|TRACK|FILE, found "{command}". Whole line was: {line}')
            else:
                raise Exception(f"Failed to parse line {line}")


    return file_data

def track(lines: list[str]) -> dict[str, str|int|dict|None]:
    line = lines.pop(0)
    matches = re.match(r'TRACK ([0-9]+) (AUDIO|CDG|MODE1/2048|MODE1/2352|MODE2/2336|MODE2/2352|CDI/2336|CDI/2352)', line)

    if not matches:
        raise ValueError(f"Couldn't parse TRACK line. Line was: '{line}'")

    track_number = int(matches.group(1))
    mode = matches.group(2)

    track_data = {'track_number': track_number, 'title': None, 'performer': None, 'mode': mode, 'isrc': None, 'flag': None, 'comments': {}, 'indicies': {}}

    while len(lines) > 0:
        line = lines[0]
        if line.startswith("PERFORMER"):
            track_data['performer'] = performer(lines)
        elif line.startswith("INDEX"):
            index_data = index(lines)
            index_number = index_data['index_number']
            index_timestamp = index_data['timestamp']

            track_data['indicies'][index_number] = index_timestamp
        elif line.startswith("TITLE"):
            track_data['title'] = title(lines)
        elif line.startswith("REM"):
            track_data['comments'].update(rem(lines))
        elif line.startswith("FLAGS"):
            track_data['flag'] = flags(lines)
        elif line.startswith("ISRC"):
            track_data['isrc'] = isrc(lines)
        # Note: We don't consume this TRACK line, so it get's consumed by
        # the file function which called us
        elif line.startswith("TRACK") or line.startswith("FILE"):
            return track_data
        else:
            if ' ' in line:
                command = line.split(' ')[0]
                raise ValueError(f'Unexpected command in TRACK section. Expected REM|TITLE|PERFORMER|FLAGS|ISRC|TRACK|FILE, found "{command}". Whole line was: {line}')
            else:
                raise Exception(f"Failed to parse line {line}")


    return track_data

def isrc(lines: list[str]) -> str:
    line = lines.pop(0)
    # isrc code structure can be found here: https://isrc.ifpi.org/en/isrc-standard/structure
    matches = re.match(r'ISRC ([a-zA-Z0-9]{5}[0-9]{2}[0-9]{5})', line)

    if not matches:
        raise ValueError(f"Couldn't parse ISRC line. Line was: '{line}'")

    isrc_number = matches.group(1)

    return isrc_number

def flags(lines: list[str]) -> str:
    line = lines.pop(0)
    matches = re.match(r'FLAGS (PRE|DCP|4CH|SCMS)', line)

    if not matches:
        raise ValueError(f"Couldn't parse FLAG line. Line was: '{line}'")

    flag = matches.group(1)

    return flag

def index(lines: list[str]) -> dict[str, str|int]:
    line = lines.pop(0)
    matches = re.match(r'INDEX ([0-9]+) ([0-9][0-9]:[0-9][0-9]:[0-9][0-9])', line)

    if not matches:
        raise ValueError(f"Couldn't parse INDEX line. Line was: '{line}'")

    number = int(matches.group(1))
    timestamp = matches.group(2)

    return {'index_number': number, 'timestamp': timestamp}

def parse(cue_file: str) -> dict[str, str|list|dict|None]:
    lines = cue_file.split('\n')

    # Clean up the lines by removing leading whitespace
    for i, line in enumerate(lines):
        lines[i] = line.lstrip()

    # Remove empty lines (has the effect of removing lines with only whitespace because of the lstrip before)
    lines = [line for line in lines if line != '']

    cue_data = {'title': None, 'performer': None, 'files': [], 'comments': {}}
    while len(lines) > 0:
        line = lines[0]
        if line.startswith("REM"):
            cue_data['comments'].update(rem(lines))
        elif line.startswith("PERFORMER"):
            cue_data['performer'] = performer(lines)
        elif line.startswith('TITLE'):
            cue_data['title'] = title(lines)
        elif line.startswith("FILE"):
            cue_data['files'].append(file(lines))
        else:
            if ' ' in line:
                command = line.split(' ')[0]
                raise ValueError(f'Unexpected command in global section. Expected REM|TITLE|PERFORMER|FILE, found "{command}". Whole line was: {line}')
            else:
                raise Exception(f"Failed to parse line {line}")

    return cue_data

if __name__ == "__main__":
    import sys, pprint
    with open(sys.argv[1], 'r') as f:
        pprint.pprint(parse(f.read()))

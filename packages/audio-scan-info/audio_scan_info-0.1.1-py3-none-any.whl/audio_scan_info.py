# Copyright (c) 2025 Corey Goldberg
# MIT License

import argparse
import logging
import sys
import time
from pathlib import Path

import mutagen
import mutagen.apev2
import mutagen.easyid3

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
logger = logging.getLogger(__name__)


SUPPORTED_FORMATS = ("FLAC", "MP3")
FILE_EXTENSIONS = tuple(f".{x.lower()}" for x in SUPPORTED_FORMATS)


def get_metadata(filepath):
    file_label = f"{light_blue_arrowhead()}  File: {filepath}"
    info = {}
    tags = {}
    try:
        audio = mutagen.File(filepath, easy=True)
        if audio is None:
            logger.error(f"{file_label}\n   {red_x()} Error:\n     unknown error\n")
        else:
            if "audio/x-mp3" in audio.mime:
                info["length"] = time.strftime("%M:%S", time.gmtime(audio.info.length))
                info["bitrate"] = f"{int(audio.info.bitrate / 1000)} kbps"
                info["sample rate"] = f"{(audio.info.sample_rate / 1000.0):.1f} kHz"
                info["bitrate mode"] = str(audio.info.bitrate_mode).split(".")[-1]
                info["channels"] = str(audio.info.channels)
                if audio.info.track_gain:
                    info["track gain"] = f"{audio.info.track_gain:.1f} db"
                if audio.info.track_peak:
                    info["track peak"] = f"{audio.info.track_peak:.1f}"
                if audio.info.album_gain:
                    info["album gain"] = f"{audio.info.album_gain:.1f} db"
                id3_tags = {tag: value[0] for tag, value in audio.tags.items()} if audio.tags is not None else {}
                # some MP3's have APEv2 tags also
                ape = mutagen.apev2.APEv2File(filepath)
                ape_tags = {}
                if ape.tags is not None:
                    for tag, value in ape.tags.items():
                        ape_tags[f"ape_{tag.lower()}"] = (
                            "<BINARY>" if isinstance(value, mutagen.apev2.APEBinaryValue) else value
                        )
                tags = id3_tags | ape_tags
            elif "audio/x-flac" in audio.mime:
                info["length"] = time.strftime("%M:%S", time.gmtime(audio.info.length))
                info["bitrate"] = f"{int(audio.info.bitrate / 1000)} kbps"
                info["bits per sample"] = str(audio.info.bits_per_sample)
                info["sample rate"] = f"{(audio.info.sample_rate / 1000.0):.1f} kHz"
                info["channels"] = str(audio.info.channels)
                if audio.pictures:
                    info["has embedded pictures"] = "true"
                if audio.cuesheet:
                    info["has cuesheet"] = "true"
                if audio.seektable:
                    info["has seek table"] = "true"
                if audio.tags is not None:
                    tags = {tag: value for tag, value in audio.tags}
    except Exception as e:
        logger.error(f"{file_label}\n   {red_x()} Error:\n     {e}\n")
    return tags, info


def analyze_file(filepath):
    file_label = f"{light_blue_arrowhead()}  File: {filepath}"
    if not filepath.exists():
        logger.error(f"{file_label}\n   {red_x()} Error:\n     can't find file\n")
        return
    if filepath.name.lower().endswith(FILE_EXTENSIONS):
        tags, info = get_metadata(filepath)
        if info:
            logger.info(f"{file_label}\n   {light_blue_arrow()} Info:")
            for attr, value in info.items():
                logger.info(f"       {attr}: {value}")
        if tags:
            logger.info(f"   {light_blue_arrow()} Tags:")
            for tag, value in tags.items():
                logger.info(f"       {tag}: {value}")
        logger.info("")


def run(path, filenames):
    if filenames:
        for f in filenames:
            filepath = Path(path / f).resolve()
            analyze_file(filepath)
    else:
        for root, dirs, files in path.walk():
            for f in sorted(files):
                filepath = Path(root / f).resolve()
                analyze_file(filepath)


def colored_symbol(unicode_char, rgb):
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m{unicode_char}\033[0m"


def red_x():
    return colored_symbol("\u2717", (255, 0, 0))


def light_blue_arrow():
    return colored_symbol("\u2794", (144, 213, 255))


def light_blue_arrowhead():
    return colored_symbol("\u27a4", (144, 213, 255))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="*", help="[optional] file to process (multiple allowed)")
    parser.add_argument("-d", "--dir", default=Path.cwd().resolve(), help="start directory")
    args = parser.parse_args()
    path = Path(args.dir)
    filenames = sorted(Path(f) for f in args.filename)
    if not path.exists():
        sys.exit(f"{red_x()} Error: can't find '{path}'")
    try:
        run(path, filenames)
    except KeyboardInterrupt:
        sys.exit()

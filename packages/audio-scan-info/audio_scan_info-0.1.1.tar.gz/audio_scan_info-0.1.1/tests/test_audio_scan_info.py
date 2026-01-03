import logging
import shutil
from pathlib import Path

import mutagen

import audio_scan_info

SAMPLES_PATH = Path("tests", "sample_files").resolve()
LOG_LEVEL = logging.INFO

EXPECTED_ARTIST = "Test Artist"
EXPECTED_TITLE = "Test Title"
EXPECTED_LENGTH = "00:01"
EXPECTED_SAMPLE_RATE = "8.0 kHz"
EXPECTED_CHANNELS = "1"
EXPECTED_MP3_BITRATE = "8 kbps"
EXPECTED_MP3_BITRATE_MODE = "CBR"
EXPECTED_FLAC_BITRATE = "45 kbps"
EXPECTED_FLAC_BITS = "16"


def copy_file(filename, path):
    samples_filepath = Path("tests", "sample_files", filename).resolve()
    Path(path / Path(filename).parent).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SAMPLES_PATH / filename, path / filename)
    try:
        audio = mutagen.File(samples_filepath, easy=True)
        assert EXPECTED_ARTIST in audio["artist"], "test files are tagged incorrectly"
        assert EXPECTED_TITLE in audio["title"], "test files are tagged incorrectly"
    except mutagen.MutagenError:
        pass


def test_get_metadata_mp3(tmp_path):
    filename = "test_file.mp3"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    tags, info = audio_scan_info.get_metadata(filepath)
    assert len(tags) == 2
    assert tags["artist"] == EXPECTED_ARTIST
    assert tags["title"] == EXPECTED_TITLE
    assert len(info) == 5
    assert info["length"] == EXPECTED_LENGTH
    assert info["bitrate"] == EXPECTED_MP3_BITRATE
    assert info["bitrate mode"] == EXPECTED_MP3_BITRATE_MODE
    assert info["sample rate"] == EXPECTED_SAMPLE_RATE
    assert info["channels"] == EXPECTED_CHANNELS


def test_get_metadata_flac(tmp_path):
    filename = "test_file.flac"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    tags, info = audio_scan_info.get_metadata(filepath)
    assert len(tags) == 2
    assert tags["artist"] == EXPECTED_ARTIST
    assert tags["title"] == EXPECTED_TITLE
    assert len(info) == 5
    assert info["length"] == EXPECTED_LENGTH
    assert info["bitrate"] == EXPECTED_FLAC_BITRATE
    assert info["bits per sample"] == EXPECTED_FLAC_BITS
    assert info["sample rate"] == EXPECTED_SAMPLE_RATE
    assert info["channels"] == EXPECTED_CHANNELS


def test_analyze_mp3(tmp_path, caplog):
    filename = "test_file.mp3"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    caplog.set_level(LOG_LEVEL)
    audio_scan_info.analyze_file(filepath)
    for record in caplog.records:
        assert record.levelname == "INFO"
    assert f"\u27a4  File: {filepath}\n" in caplog.text
    assert "   \u2794 Info:\n" in caplog.text
    assert f"       length: {EXPECTED_LENGTH}\n" in caplog.text
    assert f"       bitrate: {EXPECTED_MP3_BITRATE}\n" in caplog.text
    assert f"       sample rate: {EXPECTED_SAMPLE_RATE}\n" in caplog.text
    assert f"       bitrate mode: {EXPECTED_MP3_BITRATE_MODE}\n" in caplog.text
    assert f"       channels: {EXPECTED_CHANNELS}\n" in caplog.text
    assert "   \u2794 Tags:\n" in caplog.text
    assert f"       artist: {EXPECTED_ARTIST}\n" in caplog.text
    assert f"       title: {EXPECTED_TITLE}\n" in caplog.text


def test_analyze_flac(tmp_path, caplog):
    filename = "test_file.flac"
    copy_file(filename, tmp_path)
    filepath = tmp_path / filename
    caplog.set_level(LOG_LEVEL)
    audio_scan_info.analyze_file(filepath)
    for record in caplog.records:
        assert record.levelname == "INFO"
    assert f"\u27a4  File: {filepath}\n" in caplog.text
    assert "   \u2794 Info:\n" in caplog.text
    assert f"       length: {EXPECTED_LENGTH}\n" in caplog.text
    assert f"       bitrate: {EXPECTED_FLAC_BITRATE}\n" in caplog.text
    assert f"       bits per sample: {EXPECTED_FLAC_BITS}\n" in caplog.text
    assert f"       sample rate: {EXPECTED_SAMPLE_RATE}\n" in caplog.text
    assert f"       channels: {EXPECTED_CHANNELS}\n" in caplog.text
    assert "   \u2794 Tags:\n" in caplog.text
    assert f"       artist: {EXPECTED_ARTIST}\n" in caplog.text
    assert f"       title: {EXPECTED_TITLE}\n" in caplog.text


def test_analyze_unknown_file(caplog):
    filename = Path("unknown_file.mp3")
    caplog.set_level(LOG_LEVEL)
    audio_scan_info.analyze_file(filename)
    for record in caplog.records:
        assert record.levelname == "ERROR"
    assert f"\u27a4  File: {filename}\n"
    assert "   \u2717 Error:\n     can't find file\n" in caplog.text


def test_run_filenames(tmp_path, caplog):
    filenames = [f"test_file.{extension}" for extension in ("mp3", "flac")]
    assert len(filenames) == 2
    for filename in filenames:
        copy_file(filename, tmp_path)
    caplog.set_level(LOG_LEVEL)
    audio_scan_info.run(tmp_path, filenames)
    for record in caplog.records:
        assert record.levelname == "INFO"
    for filepath in (tmp_path / filename for filename in filenames):
        assert f"\u27a4  File: {filepath}\n"
    assert "   \u2794 Info:\n" in caplog.text
    assert f"       length: {EXPECTED_LENGTH}\n" in caplog.text
    assert f"       bitrate: {EXPECTED_MP3_BITRATE}\n" in caplog.text
    assert f"       sample rate: {EXPECTED_SAMPLE_RATE}\n" in caplog.text
    assert f"       bitrate mode: {EXPECTED_MP3_BITRATE_MODE}\n" in caplog.text
    assert f"       channels: {EXPECTED_CHANNELS}\n" in caplog.text
    assert "   \u2794 Info:\n" in caplog.text
    assert f"       length: {EXPECTED_LENGTH}\n" in caplog.text
    assert f"       bitrate: {EXPECTED_FLAC_BITRATE}\n" in caplog.text
    assert f"       bits per sample: {EXPECTED_FLAC_BITS}\n" in caplog.text
    assert f"       sample rate: {EXPECTED_SAMPLE_RATE}\n" in caplog.text
    assert f"       channels: {EXPECTED_CHANNELS}\n" in caplog.text
    assert "   \u2794 Tags:\n" in caplog.text
    assert f"       artist: {EXPECTED_ARTIST}\n" in caplog.text
    assert f"       title: {EXPECTED_TITLE}\n" in caplog.text


def test_run_dir(tmp_path, caplog):
    filenames = [path.relative_to(SAMPLES_PATH) for path in SAMPLES_PATH.rglob("**/*") if path.is_file()]
    num_files = len(filenames)
    for filename in filenames:
        copy_file(filename, tmp_path)
    caplog.set_level(LOG_LEVEL)
    audio_scan_info.run(tmp_path, [])
    for record in caplog.records:
        assert record.levelname in ("ERROR", "INFO")
    temp_files = [tmp_path / filename for filename in filenames]
    assert num_files == len(temp_files)
    for filepath in temp_files:
        assert f"\u27a4  File: {filepath}\n" in caplog.text

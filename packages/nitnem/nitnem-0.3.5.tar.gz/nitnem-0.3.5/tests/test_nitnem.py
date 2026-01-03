from nitnem import cli
from nitnem import nitnemplay
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
import time
import os
import sys
import argparse
import pytest


def test_create_parser():
    parser = cli.create_parser()
    result = parser.parse_args([])
    assert result.audio_choice == "auto"
    assert result.audio_file is None
    assert result.delay_duration == 3


def test_create_parser_with_ac():
    parser = cli.create_parser()
    result = parser.parse_args(["-ac", "sukhmani"])
    assert result.audio_choice == "sukhmani"
    assert result.audio_file is None


def test_check_time():
    with patch("nitnem.nitnemplay.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1, 10)  # 10 AM
        assert nitnemplay.check_time() is True

        mock_datetime.now.return_value = datetime(2024, 1, 1, 19)  # 7 PM
        assert nitnemplay.check_time() is False


def test_is_recently_modified():
    with patch("nitnem.nitnemplay.os.path.getmtime") as mock_getmtime:
        # Test case 1: File was modified recently
        mock_getmtime.return_value = time.time()  # Current time
        assert nitnemplay.is_recently_modified("anyfile.txt", 1) is True

        # Test case 2: File was not modified recently
        mock_getmtime.return_value = time.time() - 3700  # 1 hour and 10 minutes ago
        assert nitnemplay.is_recently_modified("anyfile.txt", 1) is False


def test_get_assets_dir():
    assets_dir = nitnemplay.get_assets_dir()
    assert assets_dir.endswith(os.path.join("nitnem", "assets"))
    assert os.path.isabs(assets_dir)


def test_play_audio_if_needed():
    with patch("nitnem.nitnemplay.os.path.exists") as mock_exists:
        with patch("nitnem.nitnemplay.os.path.getmtime") as mock_getmtime:
            with patch("nitnem.nitnemplay.datetime") as mock_datetime:
                with patch("nitnem.nitnemplay.subprocess.run") as mock_subprocess_run:
                    with patch("builtins.open", mock_open()) as mock_file_open:
                        # Mock current time
                        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)

                        # Scenario 1: File has not been played recently (played file exists, but old)
                        mock_exists.return_value = True
                        mock_getmtime.return_value = datetime(
                            2024, 1, 1, 10, 0, 0
                        ).timestamp()  # 2 hours ago

                        nitnemplay.play_audio_if_needed("test.mp3", 1)

                        mock_subprocess_run.assert_called_once_with(
                            nitnemplay.PLAYERS[sys.platform] + ["test.mp3"]
                        )
                        mock_file_open.assert_called_with("test_played.txt", "w")
                        mock_file_open().write.assert_called_with(
                            datetime(2024, 1, 1, 12, 0, 0).isoformat()
                        )

                        mock_subprocess_run.reset_mock()
                        mock_file_open.reset_mock()

                        # Scenario 2: File has been played recently (played file exists and is recent)
                        mock_exists.return_value = True
                        mock_getmtime.return_value = datetime(
                            2024, 1, 1, 11, 30, 0
                        ).timestamp()  # 30 minutes ago

                        nitnemplay.play_audio_if_needed("test.mp3", 1)

                        mock_subprocess_run.assert_not_called()
                        mock_file_open.assert_not_called()

                        mock_subprocess_run.reset_mock()
                        mock_file_open.reset_mock()

                        # Scenario 3: Played file does not exist
                        mock_exists.return_value = False

                        nitnemplay.play_audio_if_needed("test.mp3", 1)

                        mock_subprocess_run.assert_called_once_with(
                            nitnemplay.PLAYERS[sys.platform] + ["test.mp3"]
                        )
                        mock_file_open.assert_called_with("test_played.txt", "w")
                        mock_file_open().write.assert_called_with(
                            datetime(2024, 1, 1, 12, 0, 0).isoformat()
                        )


def test_mainrun():
    with patch("nitnem.nitnemplay.os.path.exists") as mock_exists:
        with patch("nitnem.nitnemplay.check_time") as mock_check_time:
            with patch(
                "nitnem.nitnemplay.play_audio_if_needed"
            ) as mock_play_audio_if_needed:
                with patch("sys.stdin", new_callable=MagicMock) as mock_stdin:
                    with patch(
                        "nitnem.nitnemplay.get_assets_dir"
                    ) as mock_get_assets_dir:
                        mock_get_assets_dir.return_value = "/mock/assets/dir"

                        # Scenario 1: audio_choice is "auto" and it's morning/day
                        args = argparse.Namespace(
                            audio_choice="auto", audio_file=None, delay_duration=3
                        )
                        mock_check_time.return_value = True  # Morning/day
                        nitnemplay.mainrun(args)
                        expected_audio_file = os.path.join(
                            "/mock/assets/dir", nitnemplay.PAATH["japji"]
                        )
                        mock_play_audio_if_needed.assert_called_once_with(
                            expected_audio_file, 3
                        )
                        mock_play_audio_if_needed.reset_mock()

                        # Scenario 2: audio_choice is "auto" and it's evening/night
                        args = argparse.Namespace(
                            audio_choice="auto", audio_file=None, delay_duration=3
                        )
                        mock_check_time.return_value = False  # Evening/night
                        nitnemplay.mainrun(args)
                        expected_audio_file = os.path.join(
                            "/mock/assets/dir", nitnemplay.PAATH["rehras"]
                        )
                        mock_play_audio_if_needed.assert_called_once_with(
                            expected_audio_file, 3
                        )
                        mock_play_audio_if_needed.reset_mock()

                        # Scenario 3: Specific audio_choice is provided
                        args = argparse.Namespace(
                            audio_choice="sukhmani", audio_file=None, delay_duration=3
                        )
                        nitnemplay.mainrun(args)
                        expected_audio_file = os.path.join(
                            "/mock/assets/dir", nitnemplay.PAATH["sukhmani"]
                        )
                        mock_play_audio_if_needed.assert_called_once_with(
                            expected_audio_file, 3
                        )
                        mock_play_audio_if_needed.reset_mock()

                        # Scenario 4: audio_file is provided
                        args = argparse.Namespace(
                            audio_choice="auto",
                            audio_file="/path/to/test.mp3",
                            delay_duration=3,
                        )
                        mock_exists.return_value = True
                        nitnemplay.mainrun(args)
                        mock_play_audio_if_needed.assert_called_once_with(
                            "/path/to/test.mp3", 3
                        )
                        mock_play_audio_if_needed.reset_mock()

                        # Scenario 5: audio_file is provided via stdin
                        args = argparse.Namespace(
                            audio_choice="auto", audio_file=None, delay_duration=3
                        )
                        mock_stdin.isatty.return_value = False
                        mock_stdin.read.return_value = "/path/to/piped.mp3\n"
                        mock_exists.return_value = True
                        nitnemplay.mainrun(args)
                        mock_play_audio_if_needed.assert_called_once_with(
                            "/path/to/piped.mp3", 3
                        )
                        mock_play_audio_if_needed.reset_mock()

                        # Scenario 6: Invalid audio_file path
                        args = argparse.Namespace(
                            audio_choice="auto",
                            audio_file="/path/to/nonexistent.mp3",
                            delay_duration=3,
                        )
                        mock_exists.return_value = False
                        with pytest.raises(FileNotFoundError):
                            nitnemplay.mainrun(args)
                        mock_play_audio_if_needed.reset_mock()

                        # Scenario 7: Non-MP3 audio_file
                        args = argparse.Namespace(
                            audio_choice="auto",
                            audio_file="/path/to/test.wav",
                            delay_duration=3,
                        )
                        mock_exists.return_value = True
                        with pytest.raises(
                            RuntimeError, match="Only MP3 files are Supported."
                        ):
                            nitnemplay.mainrun(args)
                        mock_play_audio_if_needed.reset_mock()

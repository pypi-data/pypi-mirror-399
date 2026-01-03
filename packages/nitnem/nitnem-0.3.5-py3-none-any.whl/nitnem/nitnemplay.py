import subprocess
import os
from datetime import datetime
import sys

PAATH = {
    "auto": None,
    "japji": "JapjiSahibBhaiHarbansSin.mp3",
    "rehras": "RehrasSahib-BhaiHarbansSinghJi.mp3",
    "sukhmani": "SukhmaniSahibBhaiHarbans.mp3",
}

PLAYERS = {
    "darwin": ["afplay"],
    "linux": ["omxplayer"],
    "win32": ["afplay"],
}


def check_time():
    now = datetime.now()
    return (now.hour >= 2) and (now.hour < 15)


def get_assets_dir():
    asset_dir = os.path.dirname(__file__)
    asset_dir = os.path.join(asset_dir, "assets")
    return asset_dir


def is_recently_modified(file_path, delay_duration):
    """
    Check if a file was modified within the specified delay duration.

    Args:
        file_path (str): Path to the file.
        delay_duration (int): Delay duration in hours.

    Returns:
        bool: True if the file was modified within the delay duration, False otherwise.
    """
    # Get the timestamp of when the file was last modified
    modified_time = os.path.getmtime(file_path)

    # Calculate the cutoff timestamp for the delay duration
    delay_duration_seconds = delay_duration * 60 * 60
    cutoff_time = datetime.now().timestamp() - delay_duration_seconds

    # Check if the modified time is within the delay duration
    return modified_time > cutoff_time


def play_audio_if_needed(audio_file, delay_duration):
    # Generate a unique tracking file name based on the audio file name
    played_file_path = os.path.splitext(audio_file)[0] + "_played.txt"

    # Create the played file if it does not exist
    if not os.path.exists(played_file_path):
        with open(played_file_path, "w") as f:
            f.write(datetime.now().isoformat())
        subprocess.run(PLAYERS[sys.platform] + [audio_file])
        return

    # Check if the played file was modified within the delay duration
    if not is_recently_modified(played_file_path, delay_duration):
        # Update the played file with the current timestamp
        with open(played_file_path, "w") as f:
            f.write(datetime.now().isoformat())
        print(f"Playing: {audio_file}")
        # Run the subprocess to play the audio
        subprocess.run(PLAYERS[sys.platform] + [audio_file])
    else:
        print(
            f"Audio file '{audio_file}' was played within the last {delay_duration} hours. skipping playback."
        )


def mainrun(args):
    # If -a flag was given but no value, check if something is piped in
    if args.audio_file is None and not sys.stdin.isatty():
        piped_value = sys.stdin.read().strip()
        if piped_value:
            args.audio_file = piped_value

    if args.audio_file is not None:
        # Validate the audio file path
        if not os.path.exists(args.audio_file):
            raise FileNotFoundError(f"Audio file '{args.audio_file}' does not exist.")
        if not args.audio_file.lower().endswith(".mp3"):
            raise RuntimeError("Only MP3 files are Supported.")
        audio_file = args.audio_file
    else:
        if args.audio_choice == "auto":
            if check_time():  # Morning and day time
                audio_file = os.path.join(get_assets_dir(), PAATH["japji"])
            else:
                audio_file = os.path.join(get_assets_dir(), PAATH["rehras"])
        else:
            if args.audio_choice.lower() in PAATH.keys():
                audio_file = os.path.join(
                    get_assets_dir(), PAATH[args.audio_choice.lower()]
                )

    delay_duration = max(0, args.delay_duration)
    try:
        _ = play_audio_if_needed(audio_file, delay_duration)
    except KeyboardInterrupt:
        print("User Stopped.")

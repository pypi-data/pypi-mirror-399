import argparse
from nitnem.nitnemplay import mainrun, PAATH


def create_parser():
    parser = argparse.ArgumentParser(
        description="Nitnem using python for Mac and possibly windows latter"
    )
    parser.add_argument(
        "-ac",
        "--audio-choice",
        type=str,
        default="auto",
        choices=list(PAATH.keys()),
        help="Which `Paath` to Play, auto will choose between `Japji sahib` or `Rehrash path` based on the time of the day.",
    )

    parser.add_argument(
        "-a",
        "--audio-file",
        type=str,
        default=None,
        nargs="?",
        help="Path to MP3 file, or pipe a file name.",
    )
    parser.add_argument(
        "-d",
        "--delay-duration",
        type=int,
        default=3,
        help="Delay duration in hours to wait before playing the file again.",
    )

    return parser


def cli():
    "Nitnem using python for Mac and possibly windows latter"
    parser = create_parser()
    args = parser.parse_args()
    mainrun(args)

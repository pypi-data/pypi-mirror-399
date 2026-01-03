import argparse
from   datau       import autorun, __version__

def main():
    parser = argparse.ArgumentParser(
        description="Run statistical and numerical files in batch mode."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"%(prog)s {__version__}",
        help="Show version and exit."
    )
    parser.add_argument(
        "path", nargs="?", default=".",
        help="Path to directory (default: current directory)."
    )
    parser.add_argument(
        "-p", "--pattern", default="",
        help="Regex pattern to match filenames (case-insensitive)."
    )
    parser.add_argument(
        "-d", "--date-fmt", default="%Y%m%d_%H%M%S",
        help="Datetime format for log files (default: %%Y%%m%%d_%%H%%M%%S)."
    )
    parser.add_argument(
        "-l", "--log-limit", type=int, default=None,
        help="Maximum number of log files kept. Older logs will be deleted."
    )
    parser.add_argument(
        "--powershell", action="store_true",
        help="Use PowerShell redirection (only on Windows)."
    )

    args = parser.parse_args()
    autorun(
        path_data=args.path,
        pattern=args.pattern,
        date_fmt=args.date_fmt,
        log_limit=args.log_limit,
        use_powershell=args.powershell
    )

if __name__ == "__main__":
    main()

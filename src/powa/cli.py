import argparse
import logging

from powa.daemon import start_daemon, stop_daemon


logger = logging.getLogger(__name__)


def parse_args():
    """ Parse arguments given to this CLI. """
    parser = argparse.ArgumentParser(description="Power Warden application, used to manage and monitor power domains.")

    parser.add_argument("--log-level", default="INFO", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set logging level")

    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start the daemon")
    start_parser.add_argument("--config", type=str, required=True, help="The path to the configuration file.")

    _ = subparsers.add_parser("stop", help="Stop the daemon")

    return parser.parse_args()


def main():
    args = parse_args()

    logging.basicConfig(level=args.log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if args.command == "start":
        start_daemon(config=args.config)
    elif args.command == "stop":
        stop_daemon()
    else:
        logger.error("Invalid command. Use 'start' or 'stop'.")

if __name__ == "__main__":
    main()

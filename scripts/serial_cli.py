import argparse
import logging
import os
import subprocess
import sys

from flipper.utils.cdc import resolve_port


def main():
    logger = logging.getLogger()
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="CDC Port", default="auto")
    parser.add_argument("args", nargs="*", help="Subcommands")
    args = parser.parse_args()
    
    if args.args and args.args[0] == "bridge":
        # Dispatch to marauder_bridge.py
        import subprocess
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "marauder_bridge.py"), "--port", args.port]
        if len(args.args) > 1:
            cmd.extend(args.args[1:])
        sys.exit(subprocess.call(cmd))

    if not (port := resolve_port(logger, args.port)):
        logger.error("Is Flipper connected via USB and not in DFU mode?")
        return 1
    subprocess.call(
        [
            os.path.basename(sys.executable),
            "-m",
            "serial.tools.miniterm",
            "--raw",
            port,
            "230400",
        ]
    )


if __name__ == "__main__":
    main()

import os
import serial.tools.list_ports as list_ports


# Returns a valid port or None, if it cannot be found
def resolve_port(logger, portname: str = "auto"):
    if portname != "auto":
        return portname
    # Try guessing
    flippers = list(list_ports.grep("flip_"))
    if len(flippers) >= 1:
        def _rank(port):
            dev = (port.device or "").lower()
            # Prefer USB-C CDC ports when multiple Flippers are present.
            return (0 if "usbmodem" in dev else 1, dev)

        flippers.sort(key=_rank)
        flipper = flippers[0]
        logger.info(f"Using {flipper.serial_number} on {flipper.device}")
        return flipper.device
    elif len(flippers) == 0:
        logger.error("Failed to find connected Flipper")
    env_path = os.environ.get("FLIPPER_PATH")
    if env_path:
        if os.path.exists(env_path):
            logger.info(f"Using FLIPPER_PATH from environment: {env_path}")
            return env_path

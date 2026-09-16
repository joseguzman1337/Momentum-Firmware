"""Virtual CDC/RPC transport compatible with Flipper protobuf framing."""

from .device import VirtualFlipperRpc
from .service import VirtualCdcService

__all__ = ["VirtualFlipperRpc", "VirtualCdcService"]

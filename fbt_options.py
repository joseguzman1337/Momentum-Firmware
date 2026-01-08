# fbt_options wrapper for reorganized structure
from fbt_options import *
import os
import sys

# Import from actual location
sys.path.insert(
    0, os.path.join(os.getcwd(), "upstream", "flipperzero-firmware", "scripts")
)

FBT_TOOLCHAIN_VERSIONS = (" 10.3.", " 12.3.")

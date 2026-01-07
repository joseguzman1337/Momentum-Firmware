# SConstruct wrapper for reorganized structure
import sys
import os

# Add upstream/momentum-fork/scripts to path
# NOTE: This assumes an upstream/momentum-fork tree is available locally.
# When that directory is missing, invoking SCons via this entrypoint will
# fail until the upstream build scripts are restored.
sys.path.insert(0, os.path.join(os.getcwd(), "upstream", "momentum-fork", "scripts"))

# Load the actual SConstruct
SConscript("upstream/momentum-fork/scripts/SConstruct")

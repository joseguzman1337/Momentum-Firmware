import os
import filecmp
import shutil

DIRS_TO_CLEAN = ["firmware", "targets", "furi", "lib", "documentation", "applications"]
UPSTREAM_BASE = "upstream/flipperzero-firmware"

def clean_redundant_files():
    for root_dir in DIRS_TO_CLEAN:
        if not os.path.exists(root_dir):
            continue
            
        print(f"Processing {root_dir}...")
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                root_file = os.path.join(dirpath, filename)
                
                # Construct upstream path
                # root_file is like "furi/core/check.c"
                # upstream_file should be "upstream/flipperzero-firmware/furi/core/check.c"
                upstream_file = os.path.join(UPSTREAM_BASE, root_file)
                
                try:
                    if os.path.exists(upstream_file):
                        # check if symlink
                        if os.path.islink(root_file):
                             # Special handling for symlinks if needed, or just skip
                             pass
                        elif filecmp.cmp(root_file, upstream_file, shallow=False):
                            print(f"Replacing with symlink: {root_file}")
                            os.remove(root_file)
                            rel_upstream = os.path.relpath(upstream_file, os.path.dirname(root_file))
                            os.symlink(rel_upstream, root_file)
                        else:
                            # print(f"Keeping modified file: {root_file}")
                            pass
                    else:
                        # print(f"Keeping unique file: {root_file}")
                        pass
                except OSError as e:
                    print(f"Error processing {root_file}: {e}")

        # Cleanup empty directories
        for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
            if not os.listdir(dirpath):
                print(f"Removing empty directory: {dirpath}")
                os.rmdir(dirpath)

if __name__ == "__main__":
    clean_redundant_files()

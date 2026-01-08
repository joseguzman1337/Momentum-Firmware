import os

UPSTREAM_BASE = "upstream/flipperzero-firmware"
ROOT_BASE = "."

# Directories to sync FROM root TO upstream
DIRS_TO_SYNC = ["applications", "assets", "documentation", "furi", "lib", "scripts", "site_scons", "targets"]

def sync_momentum():
    for d in DIRS_TO_SYNC:
        root_dir = os.path.join(ROOT_BASE, d)
        upstream_dir = os.path.join(UPSTREAM_BASE, d)
        
        if not os.path.exists(root_dir):
            continue
            
        print(f"Syncing {d} to upstream...")
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip upstream and other special dirs
            if UPSTREAM_BASE in dirpath or ".git" in dirpath or ".ai" in dirpath:
                continue
                
            rel_path = os.path.relpath(dirpath, root_dir)
            target_upstream_dir = os.path.join(upstream_dir, rel_path)
            
            if not os.path.exists(target_upstream_dir):
                os.makedirs(target_upstream_dir)
                
            for filename in filenames:
                if filename.startswith(".git"):
                    continue
                root_file = os.path.join(dirpath, filename)
                # Skip symlinks (they are either to upstream or other stuff we don't want to loop back)
                if os.path.islink(root_file):
                    continue
                # Skip the script itself
                if filename == "sync_momentum_to_upstream.py" or filename == "overlay_symlinks.py":
                    continue
                    
                target_upstream_file = os.path.join(target_upstream_dir, filename)
                
                if not os.path.exists(target_upstream_file):
                    print(f"Symlinking Momentum file to upstream: {target_upstream_file}")
                    rel_root = os.path.relpath(root_file, target_upstream_dir)
                    os.symlink(rel_root, target_upstream_file)
                else:
                    # If it exists in upstream, check if it's already a symlink to root
                    if os.path.islink(target_upstream_file):
                        # print(f"Already symlinked: {target_upstream_file}")
                        pass
                    else:
                        # It's a real file in upstream. 
                        # This means we have a modified file in root.
                        # We should replace the upstream file with a symlink to root's modified one!
                        # (But only if we want the build to use the modified one)
                        print(f"Overriding upstream file with Momentum version: {target_upstream_file}")
                        os.remove(target_upstream_file)
                        rel_root = os.path.relpath(root_file, target_upstream_dir)
                        os.symlink(rel_root, target_upstream_file)

if __name__ == "__main__":
    sync_momentum()

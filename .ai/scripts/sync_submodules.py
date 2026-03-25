
import os
import subprocess
import configparser
import sys

# Configuration
GITHUB_USER = "joseguzman1337"
SYNC_BRANCH = "momentum-sync"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))


def run_command(command, cwd=None):
    """Executes a shell command and returns the output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return None


def main():
    print(f"Starting Submodule Sync for user: {GITHUB_USER}")
    print(f"Root Directory: {ROOT_DIR}")

    # Read .gitmodules
    gitmodules_path = os.path.join(ROOT_DIR, ".gitmodules")
    if not os.path.exists(gitmodules_path):
        print("Error: .gitmodules not found.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(gitmodules_path)

    for section in config.sections():
        path = config[section]['path']
        url = config[section]['url']

        full_path = os.path.join(ROOT_DIR, path)
        print(f"\nProcessing submodule: {path}")

        if not os.path.exists(full_path):
            print(f"  Warning: Path {path} does not exist. Skipping.")
            continue

        # 1. Verify/Set Remote
        current_remote = run_command(
            "git remote get-url origin", cwd=full_path)
        expected_url = f"https://github.com/{GITHUB_USER}/{os.path.basename(url)}"

        # Handle .git extension consistency
        if expected_url.endswith('.git') and not current_remote.endswith('.git'):
            current_remote += '.git'

        # Simple check if the remote contains the username.
        # A more rigorous check would be exact URL matching, but forks can vary.
        if GITHUB_USER not in current_remote:
            print(
                f"  Current remote ({current_remote}) does not belong to {GITHUB_USER}.")
            # Optional: Automate forking here? For now, we assume user wants to sync what they have.
            # But the prompt implied "automate this", so let's enforce the fork URL pattern if possible.
            # For safety, we warn.
            print("  ⚠️  WARNING: Skipping push to avoid overwriting upstream.")
            continue

        # 2. Push HEAD to sync branch
        print(f"  Pushing current HEAD to {SYNC_BRANCH}...")
        push_cmd = f"git push origin HEAD:refs/heads/{SYNC_BRANCH} --force"
        if run_command(push_cmd, cwd=full_path) is not None:
            print("  ✅ Push successful.")
        else:
            print("  ❌ Push failed.")
            continue

        # 3. Checkout/Track the sync branch locally
        print(f"  Tracking {SYNC_BRANCH} locally...")
        checkout_cmd = f"git checkout -B {SYNC_BRANCH}"
        track_cmd = f"git branch -u origin/{SYNC_BRANCH}"

        if run_command(checkout_cmd, cwd=full_path) is not None and \
           run_command(track_cmd, cwd=full_path) is not None:
            print("  ✅ Local branch updated.")
        else:
            print("  ❌ Failed to update local branch.")

    print("\n---------------------------------------------------")
    print("Sync complete. Don't forget to commit the updated submodule pointers in the main repo!")


if __name__ == "__main__":
    main()

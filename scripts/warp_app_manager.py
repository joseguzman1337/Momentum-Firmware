#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import subprocess
import re

# Add scripts to path to import fbt modules if needed
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
CATALOG_URL = "https://catalog.flipperzero.one/api/v0/application?limit=500"
EXTERNAL_APPS_DIR = os.path.join(ROOT_DIR, "applications/external")
USER_APPS_DIR = os.path.join(ROOT_DIR, "applications_user")

def get_installed_appids():
    """Scans application.fam files to find installed appids."""
    appids = set()
    
    def scan_dir(base_path):
        if not os.path.exists(base_path):
            return
        for item in os.listdir(base_path):
            fam_path = os.path.join(base_path, item, "application.fam")
            if os.path.exists(fam_path):
                try:
                    with open(fam_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        # Extract appid="value"
                        m = re.search(r'appid=["\']([^"\']+)["\']', content)
                        if m:
                            appids.add(m.group(1))
                except Exception:
                    pass
    
    scan_dir(EXTERNAL_APPS_DIR)
    scan_dir(USER_APPS_DIR)
    return appids

def fetch_catalog():
    """Fetches the application list from Flipper Catalog."""
    print("Fetching Flipper App Catalog...")
    req = urllib.request.Request(CATALOG_URL, headers={'User-Agent': 'Mozilla/5.0 (Momentum-Firmware-Warp-Agent)'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except Exception as e:
        print(f"Error fetching catalog: {e}")
        return []

def update_external_apps():
    """Updates the applications/external submodule."""
    print("Updating applications/external submodule...")
    try:
        subprocess.run(["git", "submodule", "update", "--remote", "applications/external"], cwd=ROOT_DIR, check=True)
        print("External apps updated.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update submodule: {e}")

def install_missing_apps():
    """Clones missing apps from Catalog to applications_user."""
    installed = get_installed_appids()
    catalog = fetch_catalog()
    
    print(f"Found {len(installed)} installed apps locally.")
    print(f"Found {len(catalog)} apps in catalog.")
    
    if not os.path.exists(USER_APPS_DIR):
        os.makedirs(USER_APPS_DIR)
    
    new_count = 0
    for app in catalog:
        alias = app.get("alias")
        
        # Check if alias is in installed first
        if alias in installed:
            continue

        # Check if directory exists
        target_dir = os.path.join(USER_APPS_DIR, alias)
        if os.path.exists(target_dir):
            continue

        # Not installed. Fetch full details to get repo URL.
        app_id = app.get("_id")
        # print(f"Fetching details for {alias}...") # Verbose
        
        repo_url = None
        try:
            req = urllib.request.Request(f"https://catalog.flipperzero.one/api/v0/application/{app_id}", headers={'User-Agent': 'Mozilla/5.0 (Momentum-Firmware-Warp-Agent)'})
            with urllib.request.urlopen(req) as response:
                details = json.load(response)
                # Extract from details
                repo_url = details.get("repository")
                if not repo_url:
                     repo_url = details.get("current_version", {}).get("links", {}).get("source_code", {}).get("uri")
        except Exception as e:
            print(f"Failed to fetch details for {alias}: {e}")
            continue

        # Skip if no repo
        if not repo_url:
            print(f"Skipping {alias}: No repo URL found in details")
            continue

        print(f"Installing new app: {alias}...")
        try:
            # Clone only the latest commit to save space/time
            subprocess.run(["git", "clone", "--depth", "1", repo_url, target_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            new_count += 1
            print(f"  Cloned {alias} -> {target_dir}")
        except subprocess.CalledProcessError:
            print(f"  Failed to clone {alias}")
            
    print(f"Installed {new_count} new apps.")

def deploy_all():
    """Builds and deploys all apps using fbt."""
    print("Deploying apps via fbt (fap_deploy)... This may take a while.")
    try:
        # Run fbt fap_deploy from root
        subprocess.run(["./fbt", "fap_deploy"], cwd=ROOT_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--deploy-only":
        deploy_all()
        return

    update_external_apps()
    install_missing_apps()
    
    # Check if user wants to skip deploy (for testing)
    if "--no-deploy" not in sys.argv:
        deploy_all()

if __name__ == "__main__":
    main()

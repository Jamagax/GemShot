import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(__file__, ".."))
DIST = os.path.join(ROOT, "dist_zero_install")
EXCLUDE = {"prototype", "dist_zero_install", "logs", "__pycache__", ".git"}

def clean():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)

def copy_runtime():
    # Files to copy directly (runtime essentials)
    for item in ["GemShot Launch.bat", "requirements.txt", "README.md", "LICENSE", "config.yaml"]:
        src_path = os.path.join(ROOT, item)
        if os.path.isfile(src_path):
            shutil.copy(src_path, DIST)
    # Copy the src folder (runtime code) excluding development artefacts
    src_dir = os.path.join(ROOT, "src")
    dst_dir = os.path.join(DIST, "src")
    shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns(*EXCLUDE))
    
    # Compile the proxy to an executable (requires pyinstaller)
    proxy_path = os.path.join(ROOT, "src", "proxy", "main.py")
    if os.path.isfile(proxy_path):
        print("Compiling proxy...")
        # Use sys.executable to ensure we use the same python environment
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            proxy_path,
            "--distpath",
            DIST,
            "--name",
            "gemshot_proxy"
        ]
        subprocess.run(cmd, check=False)

def main():
    clean()
    copy_runtime()
    print("Distribution prepared in dist_zero_install/")

if __name__ == "__main__":
    main()

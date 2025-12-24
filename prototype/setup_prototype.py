import os
import shutil

ROOT = os.path.abspath(os.path.join(__file__, ".."))
PROTO = os.path.join(ROOT, "prototype")
EXCLUDE = {"dist_zero_install", "prototype", ".git", "__pycache__"}

def clean():
    if os.path.isdir(PROTO):
        shutil.rmtree(PROTO)
    os.makedirs(PROTO, exist_ok=True)

def copy_repo():
    for item in os.listdir(ROOT):
        if item in EXCLUDE:
            continue
        src = os.path.join(ROOT, item)
        dst = os.path.join(PROTO, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__'))
        else:
            # Rename the main installer for the prototype workspace
            if item == "setup_gemshot_windows.bat":
                shutil.copy2(src, os.path.join(PROTO, "setup_dev.bat"))
            else:
                shutil.copy2(src, dst)

def main():
    clean()
    copy_repo()
    print(f"Prototype workspace created at {PROTO}")
    print("Installer for prototype is 'setup_dev.bat'.")

if __name__ == "__main__":
    main()

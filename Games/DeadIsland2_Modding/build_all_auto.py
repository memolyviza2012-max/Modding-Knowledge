import os
import subprocess
import sys
import shutil

workspace = r"E:\Mod_Workspace\DeadIsland2_Mod_Workspace"

def run_command(cmd, cwd=workspace):
    print(f"Running: {cmd}")
    try:
        subprocess.run(cmd, cwd=cwd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {cmd}")
        sys.exit(1)

def main():
    print("=== Step 1: Run Translation ===")
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # run_command("python run_translation_DI2.py") # Translation disabled for distribution

    print("=== Step 2: Convert CSV to Locres ===")
    csv_file = os.path.join(workspace, "Translation", "Game_th.csv")
    locres_out = os.path.join(workspace, "Pack", "DeadIsland", "Content", "Localization", "Game", "en", "Game.locres")
    run_command(f"pylocres from-csv -p \"{csv_file}\" -o \"{locres_out}\" -v 2")

    print("=== Step 2.5: Inject Dialogue Subtitles ===")
    run_command("python inject_translated_subtitles.py")

    print("=== Step 3: Run pack_mod.py ===")
    run_command("python pack_mod.py")

    print("=== Step 4: Update Release_Mod_Manual ===")
    pak_src = os.path.join(workspace, "DeadIsland2_TH_P.pak")
    manual_mod_dir = os.path.join(workspace, "Release_Mod_Manual", "DeadIsland", "Content", "Paks", "~mods")
    sig_src = os.path.join(manual_mod_dir, "pakchunk_default-WindowsNoEditor_Thai_P.sig")
    
    os.makedirs(manual_mod_dir, exist_ok=True)
    shutil.copy2(pak_src, os.path.join(manual_mod_dir, "pakchunk_default-WindowsNoEditor_Thai_P.pak"))

    print("=== Step 5: Update Release_Mod (Compile Patcher) ===")
    release_dir = os.path.join(workspace, "Release_Mod")
    # Copy new pak to Release_Mod for inclusion in pyinstaller
    shutil.copy2(pak_src, os.path.join(release_dir, "pakchunk_default-WindowsNoEditor_Thai_P.pak"))
    if os.path.exists(sig_src):
        shutil.copy2(sig_src, os.path.join(release_dir, "pakchunk_default-WindowsNoEditor_Thai_P.sig"))
    shutil.copy2(os.path.join(workspace, "installer.py"), release_dir)
    shutil.copy2(os.path.join(workspace, "Pack", "DeadIsland", "Content", "DI2", "UI", "Fonts", "fonts_en.uasset"), release_dir)
    
    # Run PyInstaller
    run_command('pyinstaller --onefile --noconsole --add-data "fonts_en.uasset;." --add-data "pakchunk_default-WindowsNoEditor_Thai_P.pak;." --add-data "pakchunk_default-WindowsNoEditor_Thai_P.sig;." -n DeadIsland2_Thai_Installer installer.py', cwd=release_dir)
    
    # Move EXE and cleanup
    dist_exe = os.path.join(release_dir, "dist", "DeadIsland2_Thai_Installer.exe")
    final_exe = os.path.join(release_dir, "DeadIsland2_Thai_Installer.exe")
    if os.path.exists(dist_exe):
        if os.path.exists(final_exe):
            os.remove(final_exe)
        shutil.move(dist_exe, final_exe)
        
    for item in ["build", "dist", "installer.py", "fonts_en.uasset", "pakchunk_default-WindowsNoEditor_Thai_P.pak", "DeadIsland2_Thai_Installer.spec"]:
        p = os.path.join(release_dir, item)
        if os.path.exists(p):
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)

    print("\n[SUCCESS] ALL BUILD STEPS COMPLETED!")

if __name__ == "__main__":
    main()


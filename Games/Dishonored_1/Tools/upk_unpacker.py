"""
DISHONORED-007 Phase 3: UPK Unpacker
Uses umodel.exe to extract Flash/Scaleform files from UPK
"""
import os
import subprocess

# Paths
TOOLS_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools"
UMODEL_PATH = os.path.join(TOOLS_DIR, "umodel.exe")
SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files"
OUTPUT_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\unpacked_upk"


def unpack_upk(upk_filename):
    """Unpack a single UPK file using umodel.exe"""
    source_file = os.path.join(SOURCE_DIR, upk_filename)
    file_output_dir = os.path.join(OUTPUT_DIR, upk_filename.replace(".upk", ""))
    
    print(f"\n{'='*60}")
    print(f"UNPACKING: {upk_filename}")
    print(f"{'='*60}")
    
    # Check umodel exists
    if not os.path.exists(UMODEL_PATH):
        print(f"[ERROR] umodel.exe not found at: {UMODEL_PATH}")
        return False
    
    # Check source file exists
    if not os.path.exists(source_file):
        print(f"[ERROR] Source file not found: {source_file}")
        return False
    
    # Create output directory
    os.makedirs(file_output_dir, exist_ok=True)
    
    # Build command
    command = [
        UMODEL_PATH,
        "-export",
        f"-out={file_output_dir}",
        source_file
    ]
    
    print(f"Command: {' '.join(command)}")
    print()
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print("--- Umodel Output ---")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # List extracted files
        print(f"\n[RESULT] Extracted to: {file_output_dir}")
        print("\nExtracted files:")
        for root, dirs, files in os.walk(file_output_dir):
            for f in files:
                filepath = os.path.join(root, f)
                size = os.path.getsize(filepath)
                ext = os.path.splitext(f)[1].upper()
                print(f"  {ext:8} | {os.path.relpath(filepath, file_output_dir)} ({size:,} bytes)")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("[ERROR] Umodel timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return False


def main():
    print("DISHONORED-007 Phase 3: UPK Unpacker")
    print("=" * 60)
    
    # Files to unpack - DISHONORED-008 targets
    files_to_unpack = [
        "Dishonored_MainMenu.upk",
        "UI_PauseMenu_SF.upk",
        "UI_Journal_SF.upk"
    ]
    
    for filename in files_to_unpack:
        unpack_upk(filename)
        print()
    
    print("=" * 60)
    print("ALL UNPACK OPERATIONS COMPLETE!")


if __name__ == "__main__":
    main()

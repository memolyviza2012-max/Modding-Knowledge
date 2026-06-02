import sys
sys.path.insert(0, r"D:\Mod_Workspace\Dishonored_Mod_Workspace")
import batch_translate
print("Imported OK")
try:
    batch_translate.main()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

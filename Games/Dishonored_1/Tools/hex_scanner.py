"""
DISHONORED-012: Hex Scanner for Flash/GFX Signatures
"""
import os

files_to_scan = [
    r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole\DisFonts_SF.upk",
    r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole\DisFonts_LCZEHUNPOL_SF.upk"
]

# SWF/GFx signatures
sigs = [b'FWS', b'CWS', b'ZWS', b'GFX', b'CFX']

print("DISHONORED-012: Hex Scanner for Flash/GFX Signatures")
print("=" * 60)

for file_path in files_to_scan:
    if not os.path.exists(file_path):
        print(f"\n[ERROR] File not found: {file_path}")
        continue
        
    print(f"\n[SCANNING] {os.path.basename(file_path)}")
    print(f"  Size: {os.path.getsize(file_path):,} bytes")
    
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            
        found_count = 0
        for sig in sigs:
            pos = data.find(sig)
            while pos != -1:
                # Show context around the signature
                start = max(0, pos - 4)
                end = min(len(data), pos + 16)
                context = data[start:end]
                context_hex = ' '.join(f'{b:02X}' for b in context)
                
                print(f"  [+] Found '{sig.decode()}' at Offset: {pos} (0x{pos:X})")
                print(f"      Context: {context_hex}")
                found_count += 1
                pos = data.find(sig, pos + 1)
                
        if found_count == 0:
            print("  [EMPTY] No Flash/GFX signatures found in this file")
        else:
            print(f"  [RESULT] Total {found_count} signature(s) found")
            
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("SCAN COMPLETE")

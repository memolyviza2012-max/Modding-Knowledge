import os

def fix_bom_in_file(th_path):
    """Remove BOM character from any ID in TH file."""
    with open(th_path, 'rb') as f:
        raw = f.read()
    
    # Check for BOM bytes (EF BB BF) at start of an ID field
    # The issue is \ufeff (UTF-8 BOM) appearing mid-line before an ID
    bom_bytes = b'\xef\xbb\xbf'
    
    if bom_bytes not in raw:
        print(f'  No BOM found in {os.path.basename(th_path)}')
        return False
    
    # Replace BOM in text
    text = raw.decode('utf-8', errors='replace')
    fixed = text.replace('\ufeff', '')
    
    # Write back as UTF-8 (without BOM)
    with open(th_path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    
    print(f'  Fixed BOM in {os.path.basename(th_path)}')
    return True

def add_trailing_newline(th_path):
    """Ensure TH file ends with newline to match INT."""
    with open(th_path, 'rb') as f:
        raw = f.read()
    
    if raw.endswith(b'\n'):
        print(f'  Already has trailing newline: {os.path.basename(th_path)}')
        return False
    
    # Add trailing newline
    with open(th_path, 'ab') as f:
        f.write(b'\n')
    
    print(f'  Added trailing newline: {os.path.basename(th_path)}')
    return True

# Fix BOM for L_Pub_FromFlooded_Script
th_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script\L_Pub_FromFlooded_Script_TH.yaml'
print('=== Fixing BOM ===')
fix_bom_in_file(th_path)

# Fix trailing newlines for 5 files
print()
print('=== Fixing Trailing Newlines ===')

trailing_files = [
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Boyle_Int_Script', 'L_Boyle_Int_Script_TH.yaml'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_LightH_HighChaos_Script', 'L_LightH_HighChaos_Script_TH.yaml'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_PrsnSewer_RatScene', 'L_PrsnSewer_RatScene_TH.yaml'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromBridge_Script_Sleep', 'L_Pub_FromBridge_Script_Sleep_TH.yaml'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Ext_Script', 'DLC06_Slaughter_Ext_Script_TH.yaml'),
]

for folder, filename in trailing_files:
    th_path = os.path.join(folder, filename)
    add_trailing_newline(th_path)
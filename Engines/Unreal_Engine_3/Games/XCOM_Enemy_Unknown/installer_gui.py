import os
import sys
import shutil
import winreg
import re
import fileinput
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_steam_path():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
            return winreg.QueryValueEx(key, "InstallPath")[0]
    except Exception:
        pass
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam") as key:
            return winreg.QueryValueEx(key, "InstallPath")[0]
    except Exception:
        pass
    return None

def get_library_folders(steam_path):
    libraries = [steam_path]
    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if os.path.exists(vdf_path):
        with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            matches = re.findall(r'"path"\s+"([^"]+)"', content)
            for match in matches:
                path = match.replace('\\\\', '\\')
                if path not in libraries:
                    libraries.append(path)
    return libraries

def find_xcom_path():
    steam_path = get_steam_path()
    if not steam_path:
        return None
    libraries = get_library_folders(steam_path)
    for lib in libraries:
        xcom_path = os.path.join(lib, "steamapps", "common", "XCom-Enemy-Unknown")
        if os.path.exists(xcom_path):
            return xcom_path
    return None

def find_documents_path():
    try:
        from ctypes import wintypes, windll, ctypes
        CSIDL_PERSONAL = 5
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return buf.value
    except Exception:
        return os.path.join(os.environ.get('USERPROFILE', ''), 'Documents')

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("XCOM: Enemy Unknown & Within - Thai Localization Installer")
        self.geometry("550x400")
        self.resizable(False, False)
        
        style = ttk.Style(self)
        style.theme_use('clam')
        
        self.xcom_path = find_xcom_path()
        self.doc_path = find_documents_path()
        
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="ตัวติดตั้งม็อดภาษาไทย XCOM: EU & EW", font=("Arial", 14, "bold")).pack(pady=15)
        
        frame = ttk.Frame(self)
        frame.pack(padx=20, fill="x")
        
        ttk.Label(frame, text="ตำแหน่งเกมที่ค้นพบ:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
        path_label = self.xcom_path if self.xcom_path else "ไม่พบตัวเกม (กรุณาติดตั้ง XCOM ใน Steam)"
        ttk.Label(frame, text=path_label, foreground="green" if self.xcom_path else "red").pack(anchor="w")
        
        ttk.Label(frame, text="โฟลเดอร์เซฟเกม (Documents):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
        ttk.Label(frame, text=self.doc_path, foreground="blue").pack(anchor="w")
        
        ttk.Label(frame, text="* ม็อดนี้รองรับทั้งภาคหลัก (Enemy Unknown) และภาคเสริม (Enemy Within)\n* ระบบจะนำไฟล์ไปลงใน Documents อัตโนมัติเพื่อป้องกันเกมโหลดทับ\n* ระบบจะตั้งค่าฟอนต์ซับไตเติ้ลให้อัตโนมัติ", foreground="gray", justify="left").pack(anchor="w", pady=15)
        
        btn_state = "normal" if self.xcom_path else "disabled"
        self.install_btn = ttk.Button(self, text="ติดตั้งม็อดภาษาไทย", command=self.install_mod, state=btn_state)
        self.install_btn.pack(pady=20, ipadx=20, ipady=10)

    def copy_files(self, src_dir, dest_dir):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dest_dir, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)

    def update_ini_file(self, ini_path):
        if not os.path.exists(ini_path):
            return
        updated = False
        with fileinput.FileInput(ini_path, inplace=True, backup='.bak') as f:
            for line in f:
                if line.startswith("SubtitleFontName="):
                    print("SubtitleFontName=XcomThaiFont.SubtitleThai", end='\n')
                    updated = True
                else:
                    print(line, end='')
        return updated

    def install_mod(self):
        try:
            self.install_btn.config(state="disabled", text="กำลังติดตั้ง...")
            self.update()
            
            base_dir = get_base_path()
            
            # --- Base Game (EU) ---
            game_cooked = os.path.join(self.xcom_path, "XComGame", "CookedPCConsole")
            game_loc = os.path.join(self.xcom_path, "XComGame", "Localization", "INT")
            engine_loc = os.path.join(self.xcom_path, "Engine", "Localization", "INT")
            
            eu_doc = os.path.join(self.doc_path, "My Games", "XCOM - Enemy Unknown", "XComGame", "Localization", "INT")
            eu_ini = os.path.join(self.doc_path, "My Games", "XCOM - Enemy Unknown", "XComGame", "Config", "XComEngine.ini")
            eu_default_ini = os.path.join(self.xcom_path, "XComGame", "Config", "DefaultEngine.ini")
            
            src_cooked = os.path.join(base_dir, "XComGame", "CookedPCConsole")
            if os.path.exists(src_cooked): self.copy_files(src_cooked, game_cooked)
            
            src_game_loc = os.path.join(base_dir, "XComGame", "Localization", "INT")
            if os.path.exists(src_game_loc):
                self.copy_files(src_game_loc, game_loc)
                self.copy_files(src_game_loc, eu_doc)
                
            src_engine_loc = os.path.join(base_dir, "Engine", "Localization", "INT")
            if os.path.exists(src_engine_loc): self.copy_files(src_engine_loc, engine_loc)

            self.update_ini_file(eu_ini)
            self.update_ini_file(eu_default_ini)

            # --- Expansion (EW) ---
            xew_path = os.path.join(self.xcom_path, "XEW")
            if os.path.exists(xew_path):
                xew_cooked = os.path.join(xew_path, "XComGame", "CookedPCConsole")
                xew_loc = os.path.join(xew_path, "XComGame", "Localization", "INT")
                
                xew_doc = os.path.join(self.doc_path, "My Games", "XCOM - Enemy Within", "XComGame", "Localization", "INT")
                xew_ini = os.path.join(self.doc_path, "My Games", "XCOM - Enemy Within", "XComGame", "Config", "XComEngine.ini")
                xew_default_ini = os.path.join(xew_path, "XComGame", "Config", "DefaultEngine.ini")
                
                src_xew_loc = os.path.join(base_dir, "XEW", "XComGame", "Localization", "INT")
                if os.path.exists(src_xew_loc):
                    self.copy_files(src_xew_loc, xew_loc)
                    self.copy_files(src_xew_loc, xew_doc)
                
                if os.path.exists(src_cooked):
                    self.copy_files(src_cooked, xew_cooked)
                    
                self.update_ini_file(xew_ini)
                self.update_ini_file(xew_default_ini)
                
            messagebox.showinfo("สำเร็จ", "ติดตั้งม็อดภาษาไทยสำหรับ XCOM: EU & EW เสร็จสมบูรณ์!\nเข้าเกมเพื่อสนุกได้เลยครับ")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดขณะติดตั้ง:\n{str(e)}")
            self.install_btn.config(state="normal", text="ติดตั้งม็อดภาษาไทย")

if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()

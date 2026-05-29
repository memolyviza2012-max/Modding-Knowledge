@echo off
chcp 65001 >nul
echo ========================================
echo แพ็คไฟล์ Mod: SpaceHulkGame-WindowsNoEditor_TH.pak
echo ========================================
Tools\repak.exe pack Pack SpaceHulkGame-WindowsNoEditor_TH.pak --version V3
echo.
echo สำเร็จ! ให้นำไฟล์ SpaceHulkGame-WindowsNoEditor_TH.pak 
echo ไปวางในโฟลเดอร์เกม: F:\SteamLibrary\steamapps\common\Space Hulk Deathwing - Enhanced Edition\SpaceHulkGame\Content\Paks\
pause

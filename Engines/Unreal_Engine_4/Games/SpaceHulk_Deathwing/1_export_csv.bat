@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo ========================================
echo แปลงไฟล์ SHDW.locres ให้เป็นไฟล์ SHDW_th.csv
echo ========================================
pylocres to-csv -p "Extracted\SpaceHulkGame\Content\Localization\SHDW\en\SHDW.locres" -o "Translation\SHDW_th.csv"
echo.
echo สำเร็จ! ไฟล์ SHDW_th.csv อยู่ในโฟลเดอร์ Translation
pause

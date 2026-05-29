@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo ========================================
echo นำไฟล์แปลภาษา SHDW_th.csv กลับเข้าไปใน SHDW.locres
echo ========================================
pylocres from-csv -p "Translation\SHDW_th.csv" -o "Pack\SpaceHulkGame\Content\Localization\SHDW\en\SHDW.locres" -v 0
echo.
echo สำเร็จ! ไฟล์ SHDW.locres ถูกสร้างใหม่ที่โฟลเดอร์ Pack\...
pause

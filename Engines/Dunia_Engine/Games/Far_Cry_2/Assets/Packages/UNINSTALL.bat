@echo off
setlocal EnableDelayedExpansion
title Far Cry 2 - Thai Language Mod - Uninstaller

echo.
echo  ============================================================
echo    Far Cry 2  -  Thai Language Mod
echo    UNINSTALLER  (restore the original English files)
echo  ============================================================
echo.

set "GAME="
if exist "%~dp0..\Data_Win32\patch.dat" set "GAME=%~dp0.."
if not defined GAME if exist "%~dp0..\..\Data_Win32\patch.dat" set "GAME=%~dp0..\.."
if not defined GAME for %%D in (C D E F G H) do (
  if not defined GAME if exist "%%D:\Far Cry 2\Data_Win32\patch.dat.original_backup" set "GAME=%%D:\Far Cry 2"
  if not defined GAME if exist "%%D:\Program Files (x86)\Steam\steamapps\common\Far Cry 2\Data_Win32\patch.dat.original_backup" set "GAME=%%D:\Program Files (x86)\Steam\steamapps\common\Far Cry 2"
  if not defined GAME if exist "%%D:\SteamLibrary\steamapps\common\Far Cry 2\Data_Win32\patch.dat.original_backup" set "GAME=%%D:\SteamLibrary\steamapps\common\Far Cry 2"
  if not defined GAME if exist "%%D:\Steam\steamapps\common\Far Cry 2\Data_Win32\patch.dat.original_backup" set "GAME=%%D:\Steam\steamapps\common\Far Cry 2"
  if not defined GAME if exist "%%D:\Games\Far Cry 2\Data_Win32\patch.dat.original_backup" set "GAME=%%D:\Games\Far Cry 2"
)

if not defined GAME (
  echo  Type the game folder path, then press Enter.
  echo  Example:  D:\Far Cry 2
  echo.
  set /p "GAME=  Game folder: "
)

if not exist "!GAME!\Data_Win32\patch.dat.original_backup" (
  echo.
  echo  [ERROR] patch.dat.original_backup not found in:
  echo          !GAME!\Data_Win32
  echo.
  echo  The mod was never installed from here.
  echo  If the game is broken, use Verify / Repair in Steam
  echo  or Ubisoft Connect to restore the original files.
  echo.
  pause
  exit /b 1
)

copy /Y "!GAME!\Data_Win32\patch.dat.original_backup" "!GAME!\Data_Win32\patch.dat" >nul
if errorlevel 1 goto failed
copy /Y "!GAME!\Data_Win32\patch.fat.original_backup" "!GAME!\Data_Win32\patch.fat" >nul
if errorlevel 1 goto failed

echo  DONE - the game is back to English.
echo  The backup files are kept, so you can reinstall any time.
echo.
pause
exit /b 0

:failed
echo.
echo  [ERROR] Could not restore the files.
echo  Right-click UNINSTALL.bat and choose "Run as administrator",
echo  and make sure the game is closed.
echo.
pause
exit /b 1

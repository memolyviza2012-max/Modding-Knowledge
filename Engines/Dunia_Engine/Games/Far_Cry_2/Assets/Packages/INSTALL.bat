@echo off
setlocal EnableDelayedExpansion
title Far Cry 2 - Thai Language Mod - Installer

echo.
echo  ============================================================
echo    Far Cry 2  -  Thai Language Mod  by Lung Dear
echo    INSTALLER
echo  ============================================================
echo.

set "GAME="

rem 1) extracted inside the game folder?
if exist "%~dp0..\Data_Win32\patch.dat" set "GAME=%~dp0.."
if not defined GAME if exist "%~dp0..\..\Data_Win32\patch.dat" set "GAME=%~dp0..\.."

rem 2) scan the usual install locations
if not defined GAME for %%D in (C D E F G H) do (
  if not defined GAME if exist "%%D:\Far Cry 2\Data_Win32\patch.dat" set "GAME=%%D:\Far Cry 2"
  if not defined GAME if exist "%%D:\Program Files (x86)\Steam\steamapps\common\Far Cry 2\Data_Win32\patch.dat" set "GAME=%%D:\Program Files (x86)\Steam\steamapps\common\Far Cry 2"
  if not defined GAME if exist "%%D:\SteamLibrary\steamapps\common\Far Cry 2\Data_Win32\patch.dat" set "GAME=%%D:\SteamLibrary\steamapps\common\Far Cry 2"
  if not defined GAME if exist "%%D:\Steam\steamapps\common\Far Cry 2\Data_Win32\patch.dat" set "GAME=%%D:\Steam\steamapps\common\Far Cry 2"
  if not defined GAME if exist "%%D:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\games\Far Cry 2\Data_Win32\patch.dat" set "GAME=%%D:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\games\Far Cry 2"
  if not defined GAME if exist "%%D:\Games\Far Cry 2\Data_Win32\patch.dat" set "GAME=%%D:\Games\Far Cry 2"
  if not defined GAME if exist "%%D:\Program Files (x86)\Far Cry 2\Data_Win32\patch.dat" set "GAME=%%D:\Program Files (x86)\Far Cry 2"
)

rem 3) ask the user
if not defined GAME (
  echo  Could not find Far Cry 2 automatically.
  echo.
  echo  Type the game folder path, then press Enter.
  echo  Example:  D:\Far Cry 2
  echo.
  set /p "GAME=  Game folder: "
)

if not exist "!GAME!\Data_Win32\patch.dat" (
  echo.
  echo  [ERROR] Data_Win32\patch.dat not found in:
  echo          !GAME!
  echo.
  echo  Check the path, or copy this folder into your Far Cry 2
  echo  folder and run INSTALL.bat again.
  echo.
  pause
  exit /b 1
)

if not exist "%~dp0patch.dat" (
  echo.
  echo  [ERROR] patch.dat is missing next to this file.
  echo  Extract the whole ZIP first, then run INSTALL.bat.
  echo.
  pause
  exit /b 1
)

echo  Game found:  !GAME!
echo.

if not exist "!GAME!\Data_Win32\patch.dat.original_backup" (
  echo  [1/2] Backing up original files...
  copy /Y "!GAME!\Data_Win32\patch.dat" "!GAME!\Data_Win32\patch.dat.original_backup" >nul
  copy /Y "!GAME!\Data_Win32\patch.fat" "!GAME!\Data_Win32\patch.fat.original_backup" >nul
  echo        saved as patch.dat.original_backup
) else (
  echo  [1/2] Backup already exists - skipped
)

echo  [2/2] Copying mod files...
copy /Y "%~dp0patch.dat" "!GAME!\Data_Win32\patch.dat" >nul
if errorlevel 1 goto failed
copy /Y "%~dp0patch.fat" "!GAME!\Data_Win32\patch.fat" >nul
if errorlevel 1 goto failed

echo.
echo  ============================================================
echo    DONE - Thai mod installed. Start the game.
echo  ============================================================
echo.
echo  To remove the mod later, run UNINSTALL.bat
echo.
pause
exit /b 0

:failed
echo.
echo  [ERROR] Could not copy the files.
echo.
echo  Fix: right-click INSTALL.bat, choose "Run as administrator",
echo       and make sure the game is closed.
echo.
pause
exit /b 1

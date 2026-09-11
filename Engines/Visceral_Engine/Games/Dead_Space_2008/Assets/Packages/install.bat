@echo off
rem ============================================================
rem  Dead Space (2008) - Thai Language Mod
rem  Mod Thai By Lung Dear
rem
rem  Messages are in English on purpose: a .bat file with Thai
rem  text inside renders as garbage on any machine whose console
rem  codepage is not 874, and that is most of them.  The Thai
rem  instructions live in the .txt file next to this one.
rem ============================================================
setlocal enabledelayedexpansion
title Dead Space Thai Mod - Install

set "SRC=%~dp0text_assets"
set "MARKER=Dead Space.exe"
set "BACKUP=_ThaiMod_Backup_Original"
set "GAME="

if not exist "%SRC%" (
    echo [ERROR] text_assets folder not found next to this script.
    echo         Extract the whole zip first, then run this again.
    goto :fail
)

rem --- 1. path given on the command line, or a folder dropped on the .bat
if not "%~1"=="" if exist "%~1\%MARKER%" set "GAME=%~1"

rem --- 2. the script sitting inside the game folder itself
if not defined GAME if exist "%~dp0%MARKER%" set "GAME=%~dp0"

rem --- 3. the usual install locations of every store
if not defined GAME call :probe "%ProgramFiles(x86)%\Steam\steamapps\common\Dead Space"
if not defined GAME call :probe "%ProgramFiles%\Steam\steamapps\common\Dead Space"
if not defined GAME call :probe "%ProgramFiles(x86)%\GOG Galaxy\Games\Dead Space"
if not defined GAME call :probe "%ProgramFiles(x86)%\GOG Games\Dead Space"
if not defined GAME call :probe "%ProgramFiles%\GOG Games\Dead Space"
if not defined GAME call :probe "%ProgramFiles(x86)%\EA Games\Dead Space"
if not defined GAME call :probe "%ProgramFiles%\EA Games\Dead Space"
if not defined GAME call :probe "%ProgramFiles(x86)%\Origin Games\Dead Space"
if not defined GAME for %%D in (C D E F G H) do (
    if not defined GAME call :probe "%%D:\GOG Games\Dead Space"
    if not defined GAME call :probe "%%D:\Games\Dead Space"
    if not defined GAME call :probe "%%D:\SteamLibrary\steamapps\common\Dead Space"
    if not defined GAME call :probe "%%D:\Steam\steamapps\common\Dead Space"
)

rem --- 4. ask
if not defined GAME (
    echo Could not find the game automatically.
    echo Paste the folder that contains "%MARKER%" and press Enter,
    echo or just drag the folder onto this window.
    echo.
    set /p "GAME=Game folder: "
    set "GAME=!GAME:"=!"
)

if not exist "%GAME%\%MARKER%" (
    echo.
    echo [ERROR] "%MARKER%" is not in:
    echo         %GAME%
    goto :fail
)

echo.
echo Game folder : %GAME%
echo.

rem --- back up the originals, once and only once
if exist "%GAME%\%BACKUP%" (
    echo Backup already exists - keeping the one from the first install.
) else (
    echo Backing up the original files...
    xcopy "%GAME%\text_assets" "%GAME%\%BACKUP%\text_assets\" /E /I /Y /Q >nul
    if errorlevel 1 (
        echo [ERROR] Backup failed. Nothing was changed.
        echo         Try again with "Run as administrator".
        goto :fail
    )
)

echo Installing the Thai files...
xcopy "%SRC%" "%GAME%\text_assets\" /E /I /Y /Q >nul
if errorlevel 1 (
    echo [ERROR] Copy failed - the game folder is write protected.
    echo         Right-click this .bat and choose "Run as administrator".
    goto :fail
)

echo.
echo   DONE. Start the game - the text is Thai now.
echo   To undo, run uninstall.bat in this same folder.
echo.
echo                       Mod Thai By Lung Dear
echo.
pause
exit /b 0

:probe
if exist "%~1\%MARKER%" set "GAME=%~1"
exit /b 0

:fail
echo.
pause
exit /b 1

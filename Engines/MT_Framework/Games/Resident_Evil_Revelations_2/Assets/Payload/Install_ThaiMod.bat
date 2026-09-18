@echo off
rem ======================================================================
rem  Resident Evil Revelations 2 - Thai Mod by Lung Dear  v1.0
rem  Batch installer: copies the mod files in mod\ over the game, backing
rem  up every original once to <game>\_ThaiMod_Backup_Original.
rem
rem  Usage:  double-click                           menu (asks for admin)
rem          Install_ThaiMod.bat install   "GAME" /quiet
rem          Install_ThaiMod.bat uninstall "GAME" /quiet
rem
rem  Notes for anyone editing this file:
rem   * Keep it ASCII with CRLF line endings. cmd misparses UTF-8 and LF.
rem   * Never put a %path% expansion inside a ( ... ) block: a ")" in the
rem     path (e.g. "Program Files (x86)") closes the block early. That is
rem     why everything below is goto/call based.
rem ======================================================================
setlocal EnableExtensions DisableDelayedExpansion
title Resident Evil Revelations 2 - Thai Mod by Lung Dear v1.0

set "ROOT=%~dp0"
set "MOD=%ROOT%mod"
set "LIST=%ROOT%mod\files.txt"
set "BK=_ThaiMod_Backup_Original"
set "LOG=%ROOT%install_log.txt"
set "ACTION=%~1"
set "GAME=%~2"
set "QUIET="
if /i "%~3"=="/quiet" set "QUIET=1"

if not exist "%LIST%" goto :err_nopack

if defined QUIET goto :admin_ok
net session >nul 2>&1
if not errorlevel 1 goto :admin_ok
echo Requesting administrator permission...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs" >nul 2>&1
exit /b 0
:admin_ok

if defined GAME call :normalize_game
if /i "%ACTION%"=="install" goto :cli_install
if /i "%ACTION%"=="uninstall" goto :cli_uninstall
if /i "%ACTION%"=="detect" goto :cli_detect

rem ------------------------------------------------------------------ menu
:menu
cls
echo.
echo  ==============================================================
echo    RESIDENT EVIL REVELATIONS 2  -  Thai Mod  v1.0
echo    By Lung Dear  -  free download, do not sell
echo  ==============================================================
echo.
if not defined GAME call :detect
if defined GAME call :check_game
if errorlevel 1 set "GAME="
if not defined GAME echo    Game folder : NOT FOUND - choose 3 to enter it
if defined GAME echo    Game folder : %GAME%
echo.
echo    1. Install Thai mod
echo    2. Uninstall (restore English files)
echo    3. Change game folder
echo    4. Exit
echo.
set "CH="
set /p "CH=  Choose 1-4 and press Enter: "
if "%CH%"=="1" goto :menu_install
if "%CH%"=="2" goto :menu_uninstall
if "%CH%"=="3" goto :ask_game
if "%CH%"=="4" exit /b 0
goto :menu

:ask_game
echo.
echo    Paste the folder that contains rerev2.exe
echo    (Steam: right-click the game - Manage - Browse local files)
echo.
set "GAME="
set /p "GAME=  Folder: "
if not defined GAME goto :menu
call :normalize_game
call :check_game
if not errorlevel 1 goto :menu
echo.
echo    rerev2.exe or nativePCNext\arc was not found in that folder.
set "GAME="
pause
goto :menu

:menu_install
if not defined GAME goto :need_game
call :do_install
pause
goto :menu

:menu_uninstall
if not defined GAME goto :need_game
call :do_uninstall
pause
goto :menu

:need_game
echo.
echo    Set the game folder first (option 3).
pause
goto :menu

:cli_install
call :check_game
if errorlevel 1 goto :err_game
call :do_install
exit /b %ERR%

:cli_uninstall
call :check_game
if errorlevel 1 goto :err_game
call :do_uninstall
exit /b %ERR%

rem  Install_ThaiMod.bat detect "" /quiet  -> prints the folder it would use
:cli_detect
set "GAME="
call :detect
if defined GAME echo %GAME%
if not defined GAME echo NOT FOUND
exit /b 0

rem --------------------------------------------------------------- install
:do_install
call :game_running
if errorlevel 1 exit /b 1
echo.
echo  Installing Thai mod into:
echo    %GAME%
echo.
set /a N=0, B=0, SK=0, AM=0, MISS=0, ERR=0
echo [%date% %time%] install "%GAME%" >> "%LOG%"
for /f "usebackq delims=" %%r in ("%LIST%") do call :inst_one "%%r"
echo.
echo  --------------------------------------------------------------
echo    Files installed      : %N%
echo    Originals backed up  : %B%   (in %BK%)
echo    DLC files skipped    : %SK%   (episodes not installed)
if not "%MISS%"=="0" echo    Missing in game      : %MISS%   (skipped - game version differs?)
if not "%ERR%"=="0" echo    ERRORS               : %ERR%   (see install_log.txt)
echo  --------------------------------------------------------------
echo   files %N% backup %B% dlc_skip %SK% already %AM% missing %MISS% errors %ERR% >> "%LOG%"
if not "%AM%"=="0" call :warn_already
if not "%ERR%"=="0" goto :install_failed
echo.
echo    Done. Start the game and set the language to English.
echo.
exit /b 0

:install_failed
echo.
echo    Some files could not be written. Close the game and run this
echo    file again as administrator. To undo a partial install use
echo    Steam - Properties - Installed Files - Verify integrity.
echo.
exit /b 1

:warn_already
echo.
echo    NOTE: %AM% game files were already the Thai version before this
echo    install, so no English backup exists for them. To go back to
echo    English later use Steam - Verify integrity of game files.
exit /b 0

:inst_one
set "R=%~1"
set "SRC=%MOD%\%R%"
set "DST=%GAME%\%R%"
set "BKF=%GAME%\%BK%\%R%"
if /i not "%R:~0,4%"=="dat\" goto :inst_base
for /f "tokens=2 delims=\" %%e in ("%R%") do set "EP=%%e"
if exist "%GAME%\dat\%EP%\" goto :inst_base
set /a SK+=1
exit /b 0
:inst_base
if exist "%DST%" goto :inst_backup
set /a MISS+=1
echo   missing in game: %R% >> "%LOG%"
exit /b 0
:inst_backup
rem back up exactly once - a second install must never replace the
rem English original with the Thai file that is now in the game
if exist "%BKF%" goto :inst_copy
fc /b "%DST%" "%SRC%" >nul 2>&1
if errorlevel 1 goto :inst_backup_copy
set /a AM+=1
goto :inst_copy
:inst_backup_copy
for %%p in ("%BKF%") do if not exist "%%~dpp" mkdir "%%~dpp" >nul 2>&1
copy /y "%DST%" "%BKF%" >nul 2>&1
if errorlevel 1 goto :inst_err
set /a B+=1
:inst_copy
copy /y "%SRC%" "%DST%.new" >nul 2>&1
if errorlevel 1 goto :inst_err
move /y "%DST%.new" "%DST%" >nul 2>&1
if errorlevel 1 goto :inst_err
set /a N+=1
set /a P=N %% 40
if "%P%"=="0" echo    %N% files...
exit /b 0
:inst_err
set /a ERR+=1
if exist "%DST%.new" del /q "%DST%.new" >nul 2>&1
echo   FAILED: %R% >> "%LOG%"
exit /b 0

rem ------------------------------------------------------------- uninstall
:do_uninstall
call :game_running
if errorlevel 1 exit /b 1
set /a N=0, ERR=0
if exist "%GAME%\%BK%\" goto :un_start
echo.
echo    No backup folder (%BK%) in the game folder.
echo    Use Steam - Properties - Installed Files - Verify integrity
echo    of game files to get the English files back.
echo.
set "ERR=1"
exit /b 1
:un_start
echo.
echo  Restoring original files...
echo [%date% %time%] uninstall "%GAME%" >> "%LOG%"
for /f "usebackq delims=" %%r in ("%LIST%") do call :un_one "%%r"
echo   restored %N% errors %ERR% >> "%LOG%"
echo.
echo    Files restored : %N%
if not "%ERR%"=="0" goto :un_failed
rem backups are only removed after a clean restore, so the next install
rem backs up whatever the game has then (e.g. after a game update)
rd /s /q "%GAME%\%BK%" >nul 2>&1
echo.
echo    Done. The game is back to English.
echo.
exit /b 0
:un_failed
echo    ERRORS         : %ERR%   (see install_log.txt)
echo    The backup folder was kept. Close the game and try again.
exit /b 1

:un_one
set "R=%~1"
if not exist "%GAME%\%BK%\%R%" exit /b 0
copy /y "%GAME%\%BK%\%R%" "%GAME%\%R%.new" >nul 2>&1
if errorlevel 1 goto :un_err
move /y "%GAME%\%R%.new" "%GAME%\%R%" >nul 2>&1
if errorlevel 1 goto :un_err
set /a N+=1
exit /b 0
:un_err
set /a ERR+=1
if exist "%GAME%\%R%.new" del /q "%GAME%\%R%.new" >nul 2>&1
echo   FAILED restore: %R% >> "%LOG%"
exit /b 0

rem --------------------------------------------------------------- helpers
:game_running
tasklist /fi "imagename eq rerev2.exe" 2>nul | find /i "rerev2.exe" >nul
if errorlevel 1 exit /b 0
echo.
echo    The game is running. Close Resident Evil Revelations 2 first.
echo.
set "ERR=1"
exit /b 1

:normalize_game
set "GAME=%GAME:"=%"
if "%GAME:~-1%"=="\" set "GAME=%GAME:~0,-1%"
exit /b 0

:check_game
if not exist "%GAME%\rerev2.exe" exit /b 1
if not exist "%GAME%\nativePCNext\arc\" exit /b 1
exit /b 0

:detect
rem 1. the pack was extracted straight into the game folder
set "GAME=%ROOT:~0,-1%"
call :check_game
if not errorlevel 1 exit /b 0
set "GAME="
rem 2. Steam, including every library folder
for /f "tokens=2,*" %%a in ('reg query "HKCU\Software\Valve\Steam" /v SteamPath 2^>nul ^| find /i "SteamPath"') do call :try_steam "%%b"
if defined GAME exit /b 0
for /f "tokens=2,*" %%a in ('reg query "HKLM\SOFTWARE\WOW6432Node\Valve\Steam" /v InstallPath 2^>nul ^| find /i "InstallPath"') do call :try_steam "%%b"
if defined GAME exit /b 0
rem 3. usual places on every drive
for %%d in (C D E F G H I J K L M) do call :try_drive %%d
exit /b 0

:try_steam
if defined GAME exit /b 0
set "S=%~1"
set "S=%S:/=\%"
call :try_lib "%S%"
if defined GAME exit /b 0
if not exist "%S%\steamapps\libraryfolders.vdf" exit /b 0
for /f "usebackq tokens=1,*" %%a in (`findstr /i /c:"\"path\"" "%S%\steamapps\libraryfolders.vdf"`) do call :try_lib %%b
exit /b 0

:try_lib
if defined GAME exit /b 0
set "L=%~1"
set "L=%L:\\=\%"
if not exist "%L%\steamapps\common\" exit /b 0
set "GAME=%L%\steamapps\common\RESIDENT EVIL REVELATIONS 2"
call :check_game
if not errorlevel 1 exit /b 0
set "GAME="
rem the folder may have been renamed - look inside every game folder
for /d %%g in ("%L%\steamapps\common\*") do if not defined GAME if exist "%%~g\rerev2.exe" if exist "%%~g\nativePCNext\arc\" set "GAME=%%~g"
exit /b 0

:try_drive
if defined GAME exit /b 0
if not exist "%1:\" exit /b 0
call :try_lib "%1:\Program Files (x86)\Steam"
call :try_lib "%1:\Steam"
call :try_lib "%1:\SteamLibrary"
if defined GAME exit /b 0
set "GAME=%1:\Games\RESIDENT EVIL REVELATIONS 2"
call :check_game
if not errorlevel 1 exit /b 0
set "GAME="
exit /b 0

rem ---------------------------------------------------------------- errors
:err_nopack
echo.
echo    mod\files.txt was not found next to this file.
echo    Extract the whole zip first and run Install_ThaiMod.bat from
echo    the extracted folder - not from inside the zip.
echo.
if not defined QUIET pause
exit /b 1

:err_game
echo    Not a Resident Evil Revelations 2 folder: %GAME%
exit /b 1

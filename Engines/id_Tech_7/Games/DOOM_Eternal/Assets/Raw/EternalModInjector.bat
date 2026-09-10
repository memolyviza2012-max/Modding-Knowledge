@ECHO OFF

SETLOCAL ENABLEEXTENSIONS

SET ___DATE=2026-07-26
TITLE EternalModInjector    (%___DATE%)



SET RANDOM=
IF "%RANDOM%"=="" (
	:NoCommandExtensions
	ECHO/
	ECHO 	+-------------------------------------+
	ECHO 	^| EternalModInjector (%___DATE%^)     ^|
	ECHO 	^|     by Zwip-Zwap Zapony and friends ^|
	ECHO 	+-------------------------------------+
	ECHO/
	ECHO/
	ECHO 	ERROR: Command Processor Extensions are unavailable!
	ECHO/
	ECHO 	This batch file requires command extensions version 2, which seems to be unavailable on your system.
	ECHO/
	PAUSE
	EXIT /B 1
)
IF NOT CMDEXTVERSION 2 GOTO NoCommandExtensions



FOR /F "delims=." %%A IN ('VER') DO SET "___TEMP=%%~A"
IF NOT "%___TEMP:~-2,1%"==" " (
	SET ___ESC=[X
	SET ___EOL_COLOUR=[0;30m-[39m
) ELSE (
	SET ___ESC=
	SET ___EOL_COLOUR=
)



ECHO/
IF DEFINED ___ESC (
	ECHO 	%___ESC:X=44m%                                       %___EOL_COLOUR%
	ECHO 	%___ESC:X=44;96m%  EternalModInjector (%___DATE%^)      %___EOL_COLOUR%
	ECHO 	%___ESC:X=44;96m%      by Zwip-Zwap Zapony and friends  %___EOL_COLOUR%
	IF "%RANDOM:~-3%"=="100" ECHO 	%___ESC:X=44;96m%          (Gotta mod 'em all!^)         %___EOL_COLOUR%
	ECHO 	%___ESC:X=44m%                                       %___EOL_COLOUR%
) ELSE (
	ECHO 	+-------------------------------------+
	ECHO 	^| EternalModInjector (%___DATE%^)     ^|
	ECHO 	^|     by Zwip-Zwap Zapony and friends ^|
	IF "%RANDOM:~-3%"=="100" ECHO 	^|         (Gotta mod 'em all!^)        ^|
	ECHO 	+-------------------------------------+
)
ECHO/
ECHO/



SET ___CONFIGURATION_FILE=EternalModInjector Settings.txt
SET ___CONFIGURATION_FILE_OLD=EternalModInjector.dat
SET ___GAME_EXE=DOOMEternalx64vk.exe
SET ___SANDBOX_EXE=doomSandBox\DOOMSandBox64vk.exe

SET ___ASSET_VERSION=2026-04-03
SET ___DISPLAYED_GAME_VERSION=2026-05-19
SET ___DETERNAL_PATCHMANIFEST_KEY_BETHESDA=2C05001C1BF0134D1B17D4D5C4D784C0
SET ___DETERNAL_PATCHMANIFEST_KEY_STEAM=8B031F6A24C5C4F3950130C57EF660E9
SET ___MD5_BLANGPARSER=d895a1806377da3b6ee509f88180801f
SET ___MD5_DETERNAL_LOADMODS=f33a1b90cfe6ab7844a5503f3f77f19c
SET ___MD5_DETERNAL_PATCHMANIFEST=b23125f7d22cdce268d4370c0d0585f2
SET ___MD5_ETERNALPATCHER=1c6af381073cce58f855a4db12d1022a
SET ___MD5_GAME=baa2815a445bfdc8784c7bd62f78d291
SET ___MD5_GAME_PATCHED=6d12e4973061ccd3bba8463e5777cd2d
SET ___MD5_GAME_PATCHED_OLD=
SET ___MD5_IDREHASH=b09f6a76ad86a65b568b0b6afa9d9a73
SET ___MD5_META=01d29a39725e426a87e805f4a9a0e0e5
SET ___MD5_PACKAGEMAPSPEC=d1f84156e81b2e524430746943ff2b26
SET ___MD5_RS_DATA=bc9cce3cdf17e026175867d2e7c4bb3f
SET ___MD5_SANDBOX=361bb11d4860b7de68a27202b998bdb6
SET ___MD5_SANDBOX_PATCHED=07742801e2fed29062a59d0d41b3edb1

SET ___CERTUTIL_EXISTS=1
SET ___CONFIGURATION_EXISTS=
SET ___DETERNAL_LOADMODS_PARAMETERS="." --redirectBlangContainer "gameresources_patch3"
SET ___EOL_COLOUR=%___EOL_COLOUR%
SET ___ESC=%___ESC%
SET ___GAME_HAS_BEEN_PATCHED=
SET ___MODS_EXIST=
SET ___OWNS_ANCIENT_GODS_ONE=
SET ___OWNS_ANCIENT_GODS_TWO=
SET ___OWNS_BATTLEMODE=
SET ___OWNS_CAMPAIGN=
SET ___OWNS_HORDE=
SET ___PLATFORM=
SET ___PLATFORM_REPAIR=
SET ___SANDBOX_HAS_BEEN_PATCHED=
SET ___TEMP=

SET ___AUTO_LAUNCH_GAME=1
SET ___AUTO_UPDATE=
SET ___COMPRESS_TEXTURES=
SET ___DISABLE_MULTITHREADING=
SET ___GAME_PARAMETERS=
SET ___HAS_CHECKED_RESOURCES=
SET ___HAS_READ_FIRST_TIME=
SET ___ONLINE_SAFE=
SET ___RESET_BACKUPS=
SET ___SLOW=
SET ___VERBOSE=

2>NUL CD /D "%~dp0"
SET "PATH=%WINDIR:"=%\System32;%SYSTEMDRIVE:"=%\Windows\System32;C:\Windows\System32;%PATH:"=%"

IF EXIST ".\steam_api64.dll" (
	SET ___PLATFORM=Steam
	SET ___PLATFORM_REPAIR=verify
) ELSE IF EXIST ".\Galaxy64.dll" (
	SET ___PLATFORM=GOG Galaxy
	SET ___PLATFORM_REPAIR=verify
	SET ___ASSET_VERSION=2026-04-16
	SET ___DISPLAYED_GAME_VERSION=2026-04-14
	SET ___MD5_GAME=2779176f10354f0d5b6399bbaf31325d
	SET ___MD5_GAME_PATCHED=6434df9ef87702604b537f941e4765bb
	SET ___MD5_META=dcd02d4db19829a949309d35ce69367f
) ELSE (
	SET ___PLATFORM=the Xbox App
	SET ___PLATFORM_REPAIR=repair
	SET ___MD5_GAME=a50d12f0b104036df67086e9f6367acc
	SET ___MD5_GAME_PATCHED=146ee3b4acb1fd1f4a6429f1dd55b3dd
	SET ___MD5_SANDBOX=12a140aa2dd58d1bdd5e52b665259e9b
	SET ___MD5_SANDBOX_PATCHED=75e6bb5827ae4255aceb26098a3af0b5
)

IF EXIST ".\base\game\sp\"    SET ___OWNS_CAMPAIGN=1
IF EXIST ".\base\game\dlc\"   SET ___OWNS_ANCIENT_GODS_ONE=1
IF EXIST ".\base\game\dlc2\"  SET ___OWNS_ANCIENT_GODS_TWO=1
IF EXIST ".\base\game\horde\" SET ___OWNS_HORDE=1
IF EXIST ".\base\game\pvp\"   SET ___OWNS_BATTLEMODE=1

FOR %%A IN (".\Mods\*.zip") DO SET ___MODS_EXIST=1
FOR /D %%A IN (".\Mods\*")  DO SET ___MODS_EXIST=1

CALL :FunctionCallForModdables :FunctionInitializeBackupVariable
CALL :FunctionCallForModdables :FunctionInitializeModdedVariable

2>NUL "where.exe" /Q "certutil.exe"
IF ERRORLEVEL 1 SET ___CERTUTIL_EXISTS=





IF EXIST ".\%___CONFIGURATION_FILE%" GOTO ConfigurationFile
IF EXIST ".\%___CONFIGURATION_FILE_OLD%" GOTO ConfigurationFileOld
:PostConfigurationFile


IF DEFINED ___RESET_BACKUPS GOTO ResetBackups
:PostResetBackups


GOTO CheckForNeededFiles
:PostCheckForNeededFiles


IF NOT DEFINED ___HAS_READ_FIRST_TIME GOTO FirstTimeInformation
:PostFirstTimeInformation


IF DEFINED ___CONFIGURATION_EXISTS GOTO RestoreArchives
:PostRestoreArchives


GOTO ModLoader





:ConfigurationFile
ECHO 	Loading configuration file... (%___CONFIGURATION_FILE:\=/%)
SET ___CONFIGURATION_EXISTS=1


>NUL 2>&1 FINDSTR /B /E /C:":ASSET_VERSION=%___ASSET_VERSION%" ".\%___CONFIGURATION_FILE%"
IF ERRORLEVEL 1 SET ___RESET_BACKUPS=AssetUpdate

>NUL 2>&1 FINDSTR /B /E /L ":AUTO_LAUNCH_GAME=0" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 SET ___AUTO_LAUNCH_GAME=

>NUL 2>&1 FINDSTR /B /E /L ":AUTO_UPDATE=1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 SET ___AUTO_UPDATE=1

>NUL 2>&1 FINDSTR /B /E /L ":AUTO_UPDATE=0" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 SET ___AUTO_UPDATE=0

>NUL 2>&1 FINDSTR /B /E /L ":COMPRESS_TEXTURES=1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 (
	SET ___COMPRESS_TEXTURES=1
	SET ___DETERNAL_LOADMODS_PARAMETERS=%___DETERNAL_LOADMODS_PARAMETERS% --compress-textures
)

>NUL 2>&1 FINDSTR /B /E /L ":DISABLE_MULTITHREADING=1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 (
	SET ___DISABLE_MULTITHREADING=1
	SET ___DETERNAL_LOADMODS_PARAMETERS=%___DETERNAL_LOADMODS_PARAMETERS% --disable-multithreading
)

SET ___TEMP=
FOR /F "delims=" %%A IN ('FINDSTR /B /L ":GAME_PARAMETERS=" ".\%___CONFIGURATION_FILE%"') DO SET "___TEMP=%%~A"
SET "___TEMP=%___TEMP:"=%"
IF DEFINED ___TEMP SET "___GAME_PARAMETERS=%___TEMP:~17%"

>NUL 2>&1 FINDSTR /B /E /L ":HAS_CHECKED_RESOURCES=1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 SET ___HAS_CHECKED_RESOURCES=1

>NUL 2>&1 FINDSTR /B /E /L ":HAS_READ_FIRST_TIME=1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 SET ___HAS_READ_FIRST_TIME=1

>NUL 2>&1 FINDSTR /B /E /L ":ONLINE_SAFE=1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 (
	SET ___ONLINE_SAFE=1
	SET ___DETERNAL_LOADMODS_PARAMETERS=%___DETERNAL_LOADMODS_PARAMETERS% --online-safe
)

>NUL 2>&1 FINDSTR /B /E /L ":RESET_BACKUPS=1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 IF NOT DEFINED ___RESET_BACKUPS SET ___RESET_BACKUPS=1

>NUL 2>&1 FINDSTR /B /E /L ":SLOW=1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 (
	SET ___SLOW=1
	SET ___DETERNAL_LOADMODS_PARAMETERS=%___DETERNAL_LOADMODS_PARAMETERS% --slow
)

>NUL 2>&1 FINDSTR /B /E /L ":VERBOSE=1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 (
	SET ___VERBOSE=1
	SET ___DETERNAL_LOADMODS_PARAMETERS=%___DETERNAL_LOADMODS_PARAMETERS% --verbose
)

CALL :FunctionCallForModdables :FunctionSetResourceVariable

GOTO PostConfigurationFile


:ConfigurationFileOld
>NUL MOVE /Y ".\%___CONFIGURATION_FILE_OLD%" ".\%___CONFIGURATION_FILE%"
IF EXIST ".\%___CONFIGURATION_FILE%" GOTO ConfigurationFile

CALL :FunctionEchoError "%___CONFIGURATION_FILE_OLD:\=/%" couldn't be renamed!
ECHO/
ECHO 	Please manually rename "%___CONFIGURATION_FILE_OLD:\=/%" to "%___CONFIGURATION_FILE:\=/%", then run this batch file again.
ECHO/
GOTO Exit


:FunctionSetResourceVariable
>NUL 2>&1 FINDSTR /B /E /L "%~n2.backup" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 SET ___BACKED_UP_%~n2=1

>NUL 2>&1 FINDSTR /B /E /L "%~n2%~x1" ".\%___CONFIGURATION_FILE%"
IF NOT ERRORLEVEL 1 SET ___MODDED_%~n2=1

EXIT /B 0





:ResetBackups
IF "%___RESET_BACKUPS%"=="AssetUpdate" GOTO ResetBackupsAssetUpdate

ECHO/
ECHO/
ECHO 	":RESET_BACKUPS" is currently set to "1" in "%___CONFIGURATION_FILE:\=/%".
ECHO/
ECHO 	Do you want to delete the current backups?
ECHO 	Make sure to %___PLATFORM_REPAIR% DOOM Eternal's installation through %___PLATFORM% before continuing.
ECHO/
ECHO/
ECHO (After %___PLATFORM_REPAIR%ing DOOM Eternal, press %___ESC:X=1m%[Y]%___ESC:X=22m% to delete the old backups.)
ECHO (Press %___ESC:X=1m%[N]%___ESC:X=22m% to keep the current backups.)
ECHO (Press %___ESC:X=1m%[I]%___ESC:X=22m% for more information and instructions on %___PLATFORM_REPAIR%ing DOOM Eternal.)
<NUL SET /P ="(Press %___ESC:X=1m%[Ctrl+C]%___ESC:X=22m% to close this batch file without changes.) "
CHOICE /C YNI /N
ECHO/
ECHO/

IF NOT ERRORLEVEL 1 EXIT /B 1
IF ERRORLEVEL 4 EXIT /B 1

IF ERRORLEVEL 3 GOTO ResetBackupsInformation
IF ERRORLEVEL 2 GOTO ResetBackupsNo

:ResetBackupsYes
ECHO 	Deleting backups...

SET ___HAS_CHECKED_RESOURCES=
CALL :FunctionCallForModdables :FunctionDeleteBackup
CALL :FunctionWriteConfiguration

ECHO/
ECHO/
ECHO 	The backups have been deleted.

IF DEFINED ___MODS_EXIST GOTO ResetBackupsYesY

ECHO 	No mods were found in the "Mods" folder, so this batch file will close now.
ECHO/
GOTO Exit

:ResetBackupsYesY
ECHO 	Would you like to install mods now?
ECHO/
ECHO (Press %___ESC:X=1m%[Y]%___ESC:X=22m% to install mods.)
:ResetBackupsYesN
<NUL SET /P ="(Press %___ESC:X=1m%[N]%___ESC:X=22m% to close this batch file.) "
CHOICE /C YN /N
ECHO/
ECHO/

IF NOT ERRORLEVEL 1 EXIT /B 1
IF ERRORLEVEL 2 EXIT /B 1

GOTO PostResetBackups


:ResetBackupsNo
CALL :FunctionWriteConfiguration
ECHO 	The backups have been kept as they were.

IF DEFINED ___MODS_EXIST GOTO ResetBackupsYesY

ECHO 	Would you like to uninstall mods now?
ECHO/
ECHO (Press %___ESC:X=1m%[Y]%___ESC:X=22m% to uninstall mods.)
GOTO ResetBackupsYesN


:ResetBackupsInformation
ECHO/
ECHO/
ECHO 	More information:
ECHO/
ECHO 	DOOM Eternal mods are applied to the game files.
ECHO 	Since they're applied to existing files, not brand-new ones, it's necessary to have backups of the original/default/vanilla files.
ECHO 	The backups are used to restore the vanilla files, so that you can avoid unwanted mods' changes being kept when you try to uninstall a mod.
ECHO 	This batch file automatically handles the backup and restoration process for you, backing up game files the first time that they're about to be modified, and restoring them the next time that you run this batch file.
ECHO/
ECHO/
PAUSE

ECHO/
ECHO/
ECHO/
ECHO/
ECHO 	However, if the backups are outdated or already-modified, it's wise to delete them in order to make new, up-to-date backups.
ECHO 	This should only be done when the current game files are original/default/vanilla/non-modified, so make sure to %___PLATFORM_REPAIR% DOOM Eternal's installation through %___PLATFORM% first.
ECHO/
CALL :FunctionRedownloadInstructions 0
ECHO/
ECHO/
PAUSE

ECHO/
ECHO/
ECHO/
ECHO/
ECHO 	After %___PLATFORM_REPAIR%ing DOOM Eternal, if you press %___ESC:X=1m%[Y]%___ESC:X=22m%, the backup files will be deleted from the disk, and then new backups will be made the next first time that you install a mod for a game file.
ECHO/
ECHO 	With the %___ESC:X=1m%[N]%___ESC:X=22m% option, the current backup files will remain on the disk, and they will continue to be used (without updating them).
ECHO/
ECHO 	With the %___ESC:X=1m%[Ctrl+C]%___ESC:X=22m% option, this batch file will close without doing any changes anywhere.
ECHO/
ECHO/
PAUSE

ECHO/
ECHO/
ECHO (Press %___ESC:X=1m%[Y]%___ESC:X=22m%, %___ESC:X=1m%[N]%___ESC:X=22m%, or %___ESC:X=1m%[Ctrl+C]%___ESC:X=22m%.
CHOICE /C YN /N /M "See above for what the options do.)"
ECHO/
ECHO/

IF NOT ERRORLEVEL 1 EXIT /B 1
IF ERRORLEVEL 3 EXIT /B 1

IF ERRORLEVEL 2 GOTO ResetBackupsNo
GOTO ResetBackupsYes



:ResetBackupsAssetUpdate
ECHO/
ECHO/
ECHO 	This batch file has been updated for a new version of DOOM Eternal (%___DISPLAYED_GAME_VERSION%) since you last used it.
ECHO 	By extension, this implies that DOOM Eternal has been updated, and so the game file backups must be updated too.
ECHO/
ECHO 	Make sure to %___PLATFORM_REPAIR% DOOM Eternal's installation through %___PLATFORM% before continuing.
ECHO/
ECHO/
ECHO (After %___PLATFORM_REPAIR%ing DOOM Eternal, press %___ESC:X=1m%[Y]%___ESC:X=22m% to delete the old backups.)
ECHO (Press %___ESC:X=1m%[I]%___ESC:X=22m% for instructions on %___PLATFORM_REPAIR%ing DOOM Eternal.)
<NUL SET /P ="(Press %___ESC:X=1m%[Ctrl+C]%___ESC:X=22m% to close this batch file without changes.) "
CHOICE /C YI /N
ECHO/
ECHO/

IF NOT ERRORLEVEL 1 EXIT /B 1
IF ERRORLEVEL 3 EXIT /B 1

IF NOT ERRORLEVEL 2 GOTO ResetBackupsYes

ECHO/
ECHO/
CALL :FunctionRedownloadInstructions 0
ECHO/
ECHO/
PAUSE

ECHO/
ECHO/
ECHO/
ECHO/
ECHO 	After having %___PLATFORM_REPAIR:y=i%ed DOOM Eternal's installation, press %___ESC:X=1m%[Y]%___ESC:X=22m% to delete the old backups.
ECHO/
ECHO 	If you'd rather %___PLATFORM_REPAIR% DOOM Eternal later instead of now, you can instead press %___ESC:X=1m%[Ctrl+C]%___ESC:X=22m% to close this batch file without changes.
ECHO/
ECHO/
ECHO (Press %___ESC:X=1m%[Y]%___ESC:X=22m% or %___ESC:X=1m%[Ctrl+C]%___ESC:X=22m%.
CHOICE /C Y /N /M "See above for what the options do.)"
ECHO/
ECHO/

IF NOT ERRORLEVEL 1 EXIT /B 1
IF ERRORLEVEL 2 EXIT /B 1

GOTO ResetBackupsYes


:FunctionDeleteBackup
IF EXIST ".\base\%~1.backup" (
	ECHO 		Deleting "%~nx1.backup"...
	>NUL DEL ".\base\%~1.backup"
) ELSE IF DEFINED ___BACKED_UP_%~n2 ECHO 		"%~nx1.backup" was already deleted...

SET ___BACKED_UP_%~n2=
SET ___MODDED_%~n2=
EXIT /B 0





:CheckForNeededFiles
ECHO 	Checking for needed files, please be patient...

IF EXIST ".\Eternal Mod Loader.exe" GOTO CheckForNeededFilesNewModLoader

CALL :FunctionCheckForGameExe
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForSandboxExe
IF ERRORLEVEL 1 EXIT /B 1

IF NOT DEFINED ___HAS_CHECKED_RESOURCES (
	CALL :FunctionCallForModdables :FunctionCheckForResourceFile
	IF ERRORLEVEL 1 EXIT /B 1
)

CALL :FunctionCheckForMeta "base\meta.resources" "%___MD5_META%"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForMeta "base\packagemapspec.json" "%___MD5_PACKAGEMAPSPEC%"
IF ERRORLEVEL 1 EXIT /B 1

CALL :FunctionCheckForToolFile "base\DEternal_loadMods.exe" "%___MD5_DETERNAL_LOADMODS%"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\DEternal_patchManifest.exe" "%___MD5_DETERNAL_PATCHMANIFEST%"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\EternalPatcher.exe" "%___MD5_ETERNALPATCHER%"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\idRehash.exe" "%___MD5_IDREHASH%"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\BlangParser.dll" "%___MD5_BLANGPARSER%"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\EternalPatcher.def"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\EternalPatcher.exe.config"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\Newtonsoft.Json.dll"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\opusdec.exe"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\opusenc.exe"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\rs_data" "%___MD5_RS_DATA%"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForToolFile "base\zlib64.dll"
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCheckForModsFolder
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionCallForModdables :FunctionCheckForBackupFile
IF ERRORLEVEL 1 EXIT /B 1

CALL :FunctionIdRehashGet
IF ERRORLEVEL 1 EXIT /B 1

GOTO PostCheckForNeededFiles


:CheckForNeededFilesNewModLoader
ECHO/
ECHO/
ECHO 	%___ESC:X=1;42;92m%NOTE: You should use Eternal Mod Loader instead!%___EOL_COLOUR%
ECHO/
ECHO 	You have an "Eternal Mod Loader.exe" file. That's the new mod-loading tool, so you should use it instead of this batch file.
ECHO/
ECHO/
GOTO Exit


:FunctionCheckForBackupFile
IF NOT DEFINED ___MODDED_%~n2 EXIT /B 0
IF NOT DEFINED ___BACKED_UP_%~n2 GOTO FunctionCheckForBackupFileUndefined
IF EXIST ".\base\%~1.backup" EXIT /B 0

SET "___TEMP=%~1"
CALL :FunctionEchoError "%~nx1.backup" not found!
ECHO/
ECHO 	"%~nx1.backup" should be located at -/DOOMEternal/base/%___TEMP:\=/%.backup, but it's missing!
ECHO/
CALL :FunctionRedownloadInstructions 1
ECHO/
GOTO Exit

:FunctionCheckForBackupFileUndefined
CALL :FunctionEchoError "%~nx1" is not backed up!
ECHO/
ECHO 	The last time that you ran EternalModInjector, "%~nx1" was marked as modified, but not marked as backed up. This should be impossible.
ECHO/
CALL :FunctionRedownloadInstructions 1
ECHO/
GOTO Exit


:FunctionCheckForGameExe
IF NOT EXIST ".\%___GAME_EXE%" GOTO FunctionCheckForGameExeMissing
IF NOT DEFINED ___CERTUTIL_EXISTS EXIT /B 0

SETLOCAL ENABLEDELAYEDEXPANSION
SET ___TEMP=:
FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%___GAME_EXE%" MD5') DO SET "___TEMP=!___TEMP!  %%~A"
ENDLOCAL & SET "___TEMP=%___TEMP%"

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_GAME_PATCHED%"
IF NOT ERRORLEVEL 1 (
	SET ___GAME_HAS_BEEN_PATCHED=1
	EXIT /B 0
)

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_GAME%"
IF NOT ERRORLEVEL 1 EXIT /B 0

IF DEFINED ___MD5_GAME_PATCHED_OLD (
	ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_GAME_PATCHED_OLD%"
	IF NOT ERRORLEVEL 1 GOTO FunctionCheckForGameExeRestore
)

GOTO FunctionCheckForGameExeWrongHash

:FunctionCheckForGameExeMissing
CALL :FunctionEchoError "%___GAME_EXE:\=/%" not found!
ECHO/
ECHO 	Did you misplace this batch file, or is your DOOM Eternal installation incomplete?
ECHO 	%___GAME_EXE:\=/% should be located at -/DOOMEternal/%___GAME_EXE:\=/%
ECHO 	This batch file should be located at -/DOOMEternal/EternalModInjector.bat
ECHO/
GOTO Exit

:FunctionCheckForGameExeRestore
IF NOT EXIST ".\%___GAME_EXE%.backup" GOTO FunctionCheckForGameExeRestoreNoBackup

SETLOCAL ENABLEDELAYEDEXPANSION
SET ___TEMP=:
FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%___GAME_EXE%.backup" MD5') DO SET "___TEMP=!___TEMP!  %%~A"
ENDLOCAL & SET "___TEMP=%___TEMP%"

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_GAME%"
IF NOT ERRORLEVEL 1 GOTO FunctionCheckForGameExeRestoreNoBackup

ECHO 		Restoring "%___GAME_EXE:\=/%" to apply new EXE patches...
>NUL COPY /Y ".\%___GAME_EXE%.backup" ".\%___GAME_EXE%"
IF NOT ERRORLEVEL 1 EXIT /B 0

ECHO/
ECHO/
ECHO 	Couldn't restore "%___GAME_EXE:\=/%"; maybe it's in use by another program? You have outdated (but still valid) EXE patches as a result.
ECHO 	If you want to get the latest EXE patches, reboot your computer or %___PLATFORM_REPAIR% DOOM Eternal's installation through %___PLATFORM%, then run this batch file again.
ECHO/
CALL :FunctionRedownloadInstructions 0
ECHO/
PAUSE
EXIT /B 0

:FunctionCheckForGameExeRestoreNoBackup
ECHO/
ECHO/
ECHO 	You have outdated (but still valid) EXE patches.
ECHO 	If you want to get the latest EXE patches, %___PLATFORM_REPAIR% DOOM Eternal's installation through %___PLATFORM%, then run this batch file again.
ECHO/
CALL :FunctionRedownloadInstructions 0
ECHO/
PAUSE
EXIT /B 0

:FunctionCheckForGameExeWrongHash
ECHO/
ECHO/
ECHO %___TEMP:~3%
ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "0837596fa36a34dcbc97475bd3d27e7 0fdc1a727fb06608d37fa2c5c292638 2a3ffa77c438979b863f27beab2f119 441e4947171cb997f236d57b5c9e305 477db375313d87a9a861d315ba8b00b 740f7803d808e7a3d8934e929af04c9 77db375313d87a9a861d315ba8b00b9 82a3ffa77c438979b863f27beab2f11 837596fa36a34dcbc97475bd3d27e70 8740f7803d808e7a3d8934e929af04c f441e4947171cb997f236d57b5c9e30 fdc1a727fb06608d37fa2c5c2926386"
IF ERRORLEVEL 1 (
	CALL :FunctionEchoError "%___GAME_EXE:\=/%" has a wrong MD5 hash!
) ELSE CALL :FunctionEchoError "%___GAME_EXE:\=/%" has a bad MD5 hash!
ECHO/
ECHO 	This means that your copy of "%___GAME_EXE:\=/%" doesn't match the version that this batch file was made for.
ECHO/
ECHO 	Please update EternalModInjector and %___PLATFORM_REPAIR% DOOM Eternal's installation through %___PLATFORM%.
ECHO 	This version of this batch file is designed for the %___DISPLAYED_GAME_VERSION% version of DOOM Eternal.
ECHO/
CALL :FunctionRedownloadInstructions 0
ECHO/
GOTO Exit


:FunctionCheckForSandboxExe
IF NOT EXIST ".\%___SANDBOX_EXE%" EXIT /B 0
IF NOT DEFINED ___CERTUTIL_EXISTS EXIT /B 0

SETLOCAL ENABLEDELAYEDEXPANSION
SET ___TEMP=:
FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%___SANDBOX_EXE%" MD5') DO SET "___TEMP=!___TEMP!  %%~A"
ENDLOCAL & SET "___TEMP=%___TEMP%"

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_SANDBOX_PATCHED%"
IF NOT ERRORLEVEL 1 (
	SET ___SANDBOX_HAS_BEEN_PATCHED=1
	EXIT /B 0
)

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_SANDBOX%"
IF NOT ERRORLEVEL 1 EXIT /B 0

ECHO/
ECHO/
ECHO %___TEMP:~3%
CALL :FunctionEchoError "%___SANDBOX_EXE:\=/%" has a wrong MD5 hash!
ECHO/
ECHO 	This means that your copy of "%___SANDBOX_EXE:\=/%" doesn't match the version that this batch file was made for.
ECHO/
ECHO 	Please update EternalModInjector, delete "%___SANDBOX_EXE:\=/%", and %___PLATFORM_REPAIR% DOOM Eternal's installation through %___PLATFORM%.
ECHO 	This version of this batch file is designed for the %___DISPLAYED_GAME_VERSION% version of DOOM Eternal.
ECHO/
CALL :FunctionRedownloadInstructions 0
ECHO/
GOTO Exit


:FunctionCheckForMeta
IF NOT EXIST ".\%~1" GOTO FunctionCheckForMetaMissing
IF NOT DEFINED ___CERTUTIL_EXISTS EXIT /B 0

IF DEFINED ___MODDED_%~n1 (
	IF NOT DEFINED ___BACKED_UP_%~n1 EXIT /B 0
	IF NOT EXIST ".\%~1.backup" EXIT /B 0
)

SETLOCAL ENABLEDELAYEDEXPANSION
SET ___TEMP=:
IF DEFINED ___MODDED_%~n1 (
	FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%~1.backup" MD5') DO SET "___TEMP=!___TEMP!  %%~A"
) ELSE FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%~1" MD5') DO SET "___TEMP=!___TEMP!  %%~A"
ENDLOCAL & SET "___TEMP=%___TEMP%"

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%~2"
IF NOT ERRORLEVEL 1 EXIT /B 0

ECHO/
ECHO/
ECHO %___TEMP:~3%
CALL :FunctionEchoError "%~nx1" has a wrong MD5 hash!
ECHO/
ECHO 	This means that your copy of "%~nx1" doesn't match the version that this batch file was made for, or is somehow pre-modded when it shouldn't be.
ECHO/
ECHO 	This version of this batch file is designed for the %___DISPLAYED_GAME_VERSION% version of DOOM Eternal.
ECHO/
IF EXIST ".\%___CONFIGURATION_FILE%" (
	CALL :FunctionRedownloadInstructions 1
) ELSE CALL :FunctionRedownloadInstructions 0
ECHO/
GOTO Exit

:FunctionCheckForMetaMissing
SET "___TEMP=%~1"
CALL :FunctionEchoError "%~nx1" not found!
ECHO/
ECHO 	Did you misplace this batch file, or is your DOOM Eternal installation incomplete?
ECHO 	"%~nx1" should be located at -/DOOMEternal/%___TEMP:\=/%
ECHO 	This batch file should be located at -/DOOMEternal/EternalModInjector.bat
ECHO/
GOTO Exit


:FunctionCheckForModsFolder
IF EXIST ".\Mods\" EXIT /B 0
CALL :FunctionEchoError "Mods" not found!
ECHO/
ECHO 	Did you misplace this batch file, or did you forget to make a "Mods" folder?
ECHO 	The "Mods" folder should be located at -/DOOMEternal/Mods/
ECHO 	This batch file should be located at -/DOOMEternal/EternalModInjector.bat
ECHO/
ECHO 	If you're trying to uninstall mods, simply make an empty "Mods" folder, then run this batch file again.
ECHO/
GOTO Exit


:FunctionCheckForResourceFile
IF EXIST ".\base\%~1" EXIT /B 0
SET "___TEMP=%~1"
CALL :FunctionEchoError "%~nx1" not found!
ECHO/
ECHO 	Did you misplace this batch file, or is your DOOM Eternal installation incomplete?
ECHO 	"%~nx1" should be located at -/DOOMEternal/base/%___TEMP:\=/%
ECHO 	This batch file should be located at -/DOOMEternal/EternalModInjector.bat
ECHO/
GOTO Exit


:FunctionCheckForToolFile
IF NOT EXIST ".\%~1" GOTO FunctionCheckForToolFileMissing
IF "%~2"=="" EXIT /B 0
IF NOT DEFINED ___CERTUTIL_EXISTS EXIT /B 0

SETLOCAL ENABLEDELAYEDEXPANSION
SET ___TEMP=:
FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%~1" MD5') DO SET "___TEMP=!___TEMP!  %%~A"
ENDLOCAL & SET "___TEMP=%___TEMP%"

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%~2"
IF NOT ERRORLEVEL 1 EXIT /B 0

ECHO/
ECHO/
ECHO %___TEMP:~3%
CALL :FunctionEchoError "%~nx1" has a wrong MD5 hash!
ECHO/
ECHO 	This means that your copy of %~n1 doesn't match the version that this batch file was made for.
ECHO/
ECHO 	Try redownloading and re-extracting EternalModInjector. The "base" folder is important too.
ECHO/
GOTO Exit

:FunctionCheckForToolFileMissing
SET "___TEMP=%~1"
CALL :FunctionEchoError "%~nx1" not found!
ECHO/
ECHO 	Did you misplace %~n1 or this batch file, or did you extract EternalModInjector incorrectly?
ECHO 	"%~nx1" should be located at -/DOOMEternal/%___TEMP:\=/%
ECHO 	This batch file should be located at -/DOOMEternal/EternalModInjector.bat
ECHO/
ECHO 	Try redownloading and re-extracting EternalModInjector. The "base" folder is important too.
ECHO/
GOTO Exit


:FunctionIdRehashGet
IF DEFINED ___HAS_CHECKED_RESOURCES EXIT /B 0

ECHO 		Getting vanilla resource hash offsets... (idRehash)

IF DEFINED ___MODDED_meta (
	SET ___MODDED_meta=
	>NUL COPY /Y ".\base\meta.resources.backup" ".\base\meta.resources"
	IF ERRORLEVEL 1 GOTO FunctionIdRehashGetRestoreError
)

>NUL START "idRehash" /D ".\base" /WAIT /B ".\base\idRehash.exe" --getoffsets
IF ERRORLEVEL 1 GOTO FunctionIdRehashGetError
IF NOT ERRORLEVEL -1073741514 IF ERRORLEVEL -1073741515 GOTO FunctionIdRehashMissingVC
IF NOT ERRORLEVEL 0 GOTO FunctionIdRehashGetError

SET ___HAS_CHECKED_RESOURCES=1
EXIT /B 0

:FunctionIdRehashGetError
ECHO/
ECHO/
START "idRehash" /D ".\base" /WAIT /B ".\base\idRehash.exe" --getoffsets
CALL :FunctionEchoError idRehash couldn't find the resource hash offsets!
ECHO/
CALL :FunctionRedownloadInstructions 1
ECHO/
GOTO Exit

:FunctionIdRehashGetRestoreError
CALL :FunctionEchoError "meta.resources" couldn't be restored!
ECHO/
ECHO 	Something went wrong while trying to copy -/DOOMEternal/base/meta.resources.backup to -/DOOMEternal/base/meta.resources
ECHO/
ECHO 	Please make sure that neither of the files are in use by another program (such as DOOM Eternal itself, %___PLATFORM%, anti-virus programs, or other software), then run this batch file again.
ECHO/
GOTO Exit

:FunctionIdRehashMissingVC
CALL :FunctionEchoError idRehash didn't work!
ECHO/
ECHO 	idRehash requires the 64-bit 2015/2017/2019/2022 Visual C++ Redistributable to function.
ECHO 	Please download and install %___ESC:X=1m%https://aka.ms/vs/17/release/vc_redist.x64.exe%___ESC:X=22m%, then run this batch file again.
ECHO/
ECHO/
ECHO 	Would you like to open a web page to do so now?
ECHO/
ECHO (Press %___ESC:X=1m%[Y]%___ESC:X=22m% to open the web page.)
<NUL SET /P ="(Press %___ESC:X=1m%[N]%___ESC:X=22m% to close this batch file.) "
CHOICE /C YN /N
ECHO/
ECHO/

IF NOT ERRORLEVEL 1 EXIT /B 1
IF ERRORLEVEL 2 EXIT /B 1

START "" "https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022"
ECHO 	Opened the web page.
ECHO 	Please download and install the 2015/2017/2019/2022 "%___ESC:X=1m%X64: vc_redist.x64.exe%___ESC:X=22m%" from it, then run this batch file again.
ECHO/
GOTO Exit


:FunctionRestoreAndDeleteBackup
IF NOT DEFINED ___MODDED_%~n2 GOTO FunctionRestoreAndDeleteBackupDelete

SET ___BACKED_UP_%~n2=
SET ___MODDED_%~n2=
IF EXIST ".\base\%~1.backup" (
	ECHO 		Restoring "%~nx1"...
	>NUL COPY /Y ".\base\%~1.backup" ".\base\%~1"
	IF ERRORLEVEL 1 SET ___TEMP=1
	ECHO 		Deleting "%~nx1.backup"...
	>NUL DEL ".\base\%~1.backup"
) ELSE (
	ECHO 		Couldn't restore "%~nx1", since "%~nx1.backup" was already deleted...
	SET ___TEMP=1
)
EXIT /B 0

:FunctionRestoreAndDeleteBackupDelete
IF EXIST ".\base\%~1.backup" (
	ECHO 		Deleting "%~nx1.backup"...
	>NUL DEL ".\base\%~1.backup"
) ELSE IF DEFINED ___BACKED_UP_%~n2 ECHO 		"%~nx1.backup" was already deleted...

SET ___BACKED_UP_%~n2=
EXIT /B 0





:FirstTimeInformation
ECHO/
ECHO/
ECHO/
ECHO/
ECHO 	First-time information:
ECHO/
ECHO 	This batch file automatically...
ECHO 	- Makes backups of DOOM Eternal's game files the first time that they will be modified.
ECHO 	- Restores ones that were modified last time (to prevent uninstalled mods from lingering around) on subsequent uses.
ECHO 	- Runs EternalPatcher to apply EXE patches to DOOM Eternal's game executable.
ECHO 	- Runs DEternal_loadMods to load all mods in -/DOOMEternal/Mods/.
ECHO 	- Runs idRehash to rehash the modified files' hashes.
ECHO 	- Runs DEternal_patchManifest to set the modified files' new file sizes.
ECHO 	- Launches DOOM Eternal for you once that's all done.
ECHO/
ECHO/
PAUSE

ECHO/
ECHO/
ECHO/
ECHO/
ECHO 	I, Zwip-Zwap Zapony, take no credit for the creation of any of those things, only of this batch file that runs those things.
ECHO/
ECHO 	Full credits go to...
ECHO 	DEternal_loadMods: SutandoTsukai181 for making it in Python (based on a QuickBMS-based unpacker made for Wolfenstein II: The New Colossus by aluigi and edited for DOOM Eternal by one of infogram's friends), proteh for remaking it in C#, and PowerBall253 and SamPT for contributing to it
ECHO 	DEternal_patchManifest: SutandoTsukai181 for making it in Python (based on a script by Visual Studio), proteh for remaking it in C#, and PowerBall253 for remaking it in Rust
ECHO 	EternalPatcher: proteh for making it (based on EXE patches made by infogram that were based on Cheat Engine patches made by SunBeam, as well as based on EXE patches made by Visual Studio)
ECHO 	idRehash: infogram for making it, and proteh for updating it
ECHO 	DOOM Eternal: Bethesda Softworks, id Software, and everyone else involved, for making and updating it
ECHO/
ECHO/
PAUSE

ECHO/
ECHO/
ECHO/
ECHO/
ECHO 	If any mods are currently installed and/or you have some outdated files when EternalModInjector makes backups, the subsequent backups will contain those mods and/or be outdated.
ECHO/
ECHO 	Don't worry, though; If you ever mess up in a way that results in an already-modified/outdated backup, simply %___PLATFORM_REPAIR% DOOM Eternal's installation through %___PLATFORM%, open "%___CONFIGURATION_FILE:\=/%" in Notepad, change the ":RESET_BACKUPS=0" line to ":RESET_BACKUPS=1", and save the file.
ECHO/
ECHO/
PAUSE

ECHO/
ECHO/
ECHO/
ECHO/
ECHO 	Now, without further ado, press any key to continue one last time, and this batch file will initiate mod-loading mode.
ECHO/
ECHO/
PAUSE

CALL :FunctionWriteConfiguration
ECHO/
ECHO/
GOTO PostFirstTimeInformation





:RestoreArchives
ECHO 	Restoring modified files...

CALL :FunctionCallForModdables :FunctionRestoreArchive
IF ERRORLEVEL 1 EXIT /B 1
CALL :FunctionDeleteEternalModStreamDB
IF ERRORLEVEL 1 EXIT /B 1

GOTO PostRestoreArchives


:FunctionRestoreArchive
IF NOT DEFINED ___MODDED_%~n2 EXIT /B 0
IF NOT DEFINED ___BACKED_UP_%~n2 GOTO FunctionRestoreArchiveNoBackup

SET ___MODDED_%~n2=

ECHO 		Restoring "%~nx1"...
>NUL COPY /Y ".\base\%~1.backup" ".\base\%~1"
IF NOT ERRORLEVEL 1 EXIT /B 0

SET ___MODDED_%~n2=1
CALL :FunctionWriteConfiguration

SET "___TEMP=%~1"
CALL :FunctionEchoError "%~nx1" couldn't be restored!
ECHO/
ECHO 	Something went wrong while trying to copy -/DOOMEternal/base/%___TEMP:\=/%.backup to -/DOOMEternal/base/%___TEMP:\=/%
ECHO/
ECHO 	Please make sure that neither of the files are in use by another program (such as DOOM Eternal itself, %___PLATFORM%, anti-virus programs, or other software), then run this batch file again.
ECHO/
GOTO Exit


:FunctionRestoreArchiveNoBackup
CALL :FunctionEchoError "%~nx1" was modified last time, but is not backed up!
ECHO/
CALL :FunctionRedownloadInstructions 1
ECHO/
GOTO Exit





:ModLoader
IF DEFINED ___GAME_HAS_BEEN_PATCHED GOTO ModLoaderPatchSandbox

IF DEFINED ___CERTUTIL_EXISTS (
	ECHO 	Backing up the game EXE...
	>NUL COPY /Y ".\%___GAME_EXE%" ".\%___GAME_EXE%.backup"
)

ECHO 	Patching the game EXE... (EternalPatcher)
>NUL START "EternalPatcher" /D ".\base" /MIN /WAIT /B ".\base\EternalPatcher.exe" --patch "..\%___GAME_EXE%"

IF NOT DEFINED ___CERTUTIL_EXISTS GOTO ModLoaderPatchSandbox

ECHO 	Verifying that EternalPatcher worked...

SETLOCAL ENABLEDELAYEDEXPANSION
SET ___TEMP=:
FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%___GAME_EXE%" MD5') DO SET "___TEMP=!___TEMP!%%~A"
ENDLOCAL & SET "___TEMP=%___TEMP%"

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_GAME_PATCHED%"
IF NOT ERRORLEVEL 1 GOTO ModLoaderPatchSandbox

ECHO/
ECHO/
ECHO 	WARNING: EternalPatcher didn't work!
ECHO/
ECHO 	Sometimes, this batch file can fail to patch -/DOOMEternal/%___GAME_EXE:\=/% automatically.
ECHO 	When that happens, you have to patch it manually. Would you like to do so now?
ECHO/
ECHO/
ECHO (Press %___ESC:X=1m%[Y]%___ESC:X=22m% to open EternalPatcher.)
<NUL SET /P ="(Press %___ESC:X=1m%[N]%___ESC:X=22m% to close this batch file.) "
CHOICE /C YN /N
ECHO/
ECHO/

IF NOT ERRORLEVEL 1 EXIT /B 1
IF ERRORLEVEL 2 EXIT /B 1

ECHO 	Launching EternalPatcher...
ECHO 	Please close EternalPatcher after patching -/DOOMEternal/%___GAME_EXE:\=/%...
>NUL START "EternalPatcher" /D ".\base" /WAIT ".\base\EternalPatcher.exe"

ECHO 	Verifying that EternalPatcher worked, again...

SETLOCAL ENABLEDELAYEDEXPANSION
SET ___TEMP=:
FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%___GAME_EXE%" MD5') DO SET "___TEMP=!___TEMP!%%~A"
ENDLOCAL & SET "___TEMP=%___TEMP%"

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_GAME_PATCHED%"
IF NOT ERRORLEVEL 1 GOTO ModLoaderPatchSandbox

CALL :FunctionEchoError EternalPatcher still didn't work!
ECHO/
ECHO 	Or alternatively, you forgot to patch -/DOOMEternal/%___GAME_EXE:\=/% with it before closing it just now.
ECHO/
ECHO 	Try running -/DOOMEternal/base/EternalPatcher.exe, manually patching -/DOOMEternal/%___GAME_EXE:\=/% with it, then running this batch file again afterwards.
ECHO/
GOTO Exit


:ModLoaderPatchSandbox
IF DEFINED ___SANDBOX_HAS_BEEN_PATCHED GOTO ModLoaderLoadMods
IF NOT EXIST ".\%___SANDBOX_EXE%" GOTO ModLoaderLoadMods

IF DEFINED ___CERTUTIL_EXISTS (
	ECHO 	Backing up the official mods EXE...
	>NUL COPY /Y ".\%___SANDBOX_EXE%" ".\%___SANDBOX_EXE%.backup"
)

ECHO 	Patching the official mods EXE... (EternalPatcher)
>NUL START "EternalPatcher" /D ".\base" /MIN /WAIT /B ".\base\EternalPatcher.exe" --patch "..\%___SANDBOX_EXE%"

IF NOT DEFINED ___CERTUTIL_EXISTS GOTO ModLoaderLoadMods

ECHO 	Verifying that EternalPatcher worked...

SETLOCAL ENABLEDELAYEDEXPANSION
SET ___TEMP=:
FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%___SANDBOX_EXE%" MD5') DO SET "___TEMP=!___TEMP!%%~A"
ENDLOCAL & SET "___TEMP=%___TEMP%"

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_SANDBOX_PATCHED%"
IF NOT ERRORLEVEL 1 GOTO ModLoaderLoadMods

ECHO/
ECHO/
ECHO 	WARNING: EternalPatcher didn't work!
ECHO/
ECHO 	Sometimes, this batch file can fail to patch -/DOOMEternal/%___SANDBOX_EXE:\=/% automatically.
ECHO 	When that happens, you have to patch it manually. Would you like to do so now?
ECHO/
ECHO/
ECHO (Press %___ESC:X=1m%[Y]%___ESC:X=22m% to open EternalPatcher.)
<NUL SET /P ="(Press %___ESC:X=1m%[N]%___ESC:X=22m% to close this batch file.) "
CHOICE /C YN /N
ECHO/
ECHO/

IF NOT ERRORLEVEL 1 EXIT /B 1
IF ERRORLEVEL 2 EXIT /B 1

ECHO 	Launching EternalPatcher...
ECHO 	Please close EternalPatcher after patching -/DOOMEternal/%___SANDBOX_EXE:\=/%...
>NUL START "EternalPatcher" /D ".\base" /WAIT ".\base\EternalPatcher.exe"

ECHO 	Verifying that EternalPatcher worked, again...

SETLOCAL ENABLEDELAYEDEXPANSION
SET ___TEMP=:
FOR /F "delims=" %%A IN ('certutil.exe -hashfile ".\%___SANDBOX_EXE%" MD5') DO SET "___TEMP=!___TEMP!%%~A"
ENDLOCAL & SET "___TEMP=%___TEMP%"

ECHO %___TEMP: =%| >NUL 2>&1 FINDSTR /L /I "%___MD5_SANDBOX_PATCHED%"
IF NOT ERRORLEVEL 1 GOTO ModLoaderLoadMods

CALL :FunctionEchoError EternalPatcher still didn't work!
ECHO/
ECHO 	Or alternatively, you forgot to patch -/DOOMEternal/%___SANDBOX_EXE:\=/% with it before closing it just now.
ECHO/
ECHO 	Try running -/DOOMEternal/base/EternalPatcher.exe, manually patching -/DOOMEternal/%___SANDBOX_EXE:\=/% with it, then running this batch file again afterwards.
ECHO/
GOTO Exit


:ModLoaderLoadMods
ECHO 	Checking for mods... (DEternal_loadMods)

IF NOT DEFINED ___MODS_EXIST GOTO ModLoaderModsDontExist

SET ___TEMP=
FOR /F "delims=" %%A IN ('.\base\DEternal_loadMods.exe %___DETERNAL_LOADMODS_PARAMETERS% --list-res') DO (
	CALL :FunctionBackUpAndMarkAsModded "%%~A"
	IF ERRORLEVEL 1 EXIT /B 1
)
CALL :FunctionBackUpAndMarkAsModded ".\base\meta.resources"
IF ERRORLEVEL 1 EXIT /B 1

CALL :FunctionDeleteEternalModStreamDB
IF ERRORLEVEL 1 EXIT /B 1

CALL :FunctionWriteConfiguration


ECHO 	Loading mods... (DEternal_loadMods)
ECHO/
.\base\DEternal_loadMods.exe %___DETERNAL_LOADMODS_PARAMETERS%
IF NOT ERRORLEVEL 0 GOTO ModLoaderLoadModsError
IF ERRORLEVEL 1 GOTO ModLoaderLoadModsError
ECHO/


ECHO %___ESC:X=0m%	Rehashing resource hashes... (idRehash)
>NUL START "idRehash" /D ".\base" /WAIT /B ".\base\idRehash.exe"
IF ERRORLEVEL 1 GOTO ModLoaderIdRehashSetError


ECHO 	Patching manifest... (DEternal_patchManifest)
:ModLoaderPatchManifest
>NUL START "DEternal_patchManifest" /D ".\base" /WAIT /B ".\base\DEternal_patchManifest.exe" "%___DETERNAL_PATCHMANIFEST_KEY_STEAM%"
IF ERRORLEVEL 1 >NUL START "DEternal_patchManifest" /D ".\base" /WAIT /B ".\base\DEternal_patchManifest.exe" "%___DETERNAL_PATCHMANIFEST_KEY_BETHESDA%"
IF ERRORLEVEL 1 GOTO ModLoaderPatchManifestError
IF NOT ERRORLEVEL 0 GOTO ModLoaderPatchManifestError


GOTO ModLoaderLaunchGame


:ModLoaderModsDontExist
CALL :FunctionWriteConfiguration
ECHO 		No mods were found in the "Mods" folder...
ECHO 		The modified files were restored, so mods should be uninstalled now...

ECHO 	Unpatching manifest... (DEternal_patchManifest)
GOTO ModLoaderPatchManifest


:ModLoaderLaunchGame
ECHO/
ECHO/

IF NOT DEFINED ___AUTO_LAUNCH_GAME GOTO ModLoaderDontLaunchGame

SET "___TEMP=%___GAME_PARAMETERS:^=^^%"
SET "___TEMP=%___TEMP:&=^&%"
SET "___TEMP=%___TEMP:<=^<%"
SET "___TEMP=%___TEMP:>=^>%"
SET "___TEMP=%___TEMP:|=^|%"
IF "%___PLATFORM%"=="Steam" (
	IF NOT DEFINED ___GAME_PARAMETERS (
		START "" "steam://run/782330"
	) ELSE START "" "steam://run/782330//%___GAME_PARAMETERS%"
) ELSE IF NOT DEFINED ___GAME_PARAMETERS (
	START "DOOM Eternal" ".\%___GAME_EXE%"
) ELSE START "DOOM Eternal" ".\%___GAME_EXE%" %___TEMP%

ECHO 	DOOM Eternal has been launched!
ECHO/
ECHO 	This batch file will auto-close in 10 seconds.
ECHO 	Press [Ctrl+C] to keep it open to view the batch output above.
ECHO/
ECHO/
>NUL TIMEOUT /T 10 /NOBREAK
EXIT /B 0

:ModLoaderDontLaunchGame
IF DEFINED ___MODS_EXIST (
	ECHO 	Mods have been installed!
) ELSE ECHO 	Mods have been uninstalled!
ECHO/
ECHO 	However, DOOM Eternal has not been launched, as you've disabled that.
ECHO 	If you want to re-enable automatic game launching, open "%___CONFIGURATION_FILE:\=/%" in Notepad, change ":AUTO_LAUNCH_GAME=0" to ":AUTO_LAUNCH_GAME=1", and save the file.
ECHO/
ECHO/
<NUL SET /P ="Press any key to exit . . . "
>NUL PAUSE
EXIT /B 0


:ModLoaderLoadModsError
CALL :FunctionEchoError DEternal_loadMods didn't work!
ECHO/
ECHO 	Please make sure that none of the game files are in use by another program (such as DOOM Eternal itself, %___PLATFORM%, anti-virus programs, or other software), then run this batch file again.
ECHO/
ECHO 	If that doesn't work, try rebooting your computer and running this batch file again afterwards.
ECHO/
GOTO Exit


:ModLoaderIdRehashSetError
ECHO/
ECHO/
START "idRehash" /D ".\base" /WAIT /B ".\base\idRehash.exe"
CALL :FunctionEchoError idRehash couldn't generate new resource hashes!
ECHO/
ECHO 	Please make sure that none of the game files are in use by another program (such as DOOM Eternal itself, %___PLATFORM%, anti-virus programs, or other software), then run this batch file again.
ECHO/
ECHO 	If that doesn't work, try rebooting your computer and running this batch file again afterwards.
ECHO/
ECHO 	If that also doesn't work...
CALL :FunctionRedownloadInstructions 1
ECHO/
GOTO Exit


:ModLoaderPatchManifestError
ECHO/
ECHO/
START "DEternal_patchManifest" /D ".\base" /WAIT /B ".\base\DEternal_patchManifest.exe" "%___DETERNAL_PATCHMANIFEST_KEY_STEAM%"
CALL :FunctionEchoError DEternal_patchManifest didn't work!
ECHO/
ECHO 	Please make sure that "build-manifest.bin" isn't in use by another program (such as DOOM Eternal itself, %___PLATFORM%, anti-virus programs, or other software), then run this batch file again.
ECHO/
ECHO 	If that doesn't work, try rebooting your computer and running this batch file again afterwards.
ECHO/
ECHO 	If that also doesn't work...
CALL :FunctionRedownloadInstructions 0
ECHO/
GOTO Exit





:FunctionBackUpAndMarkAsModded
SET "___FOLDER=%~p1"
IF "%___FOLDER:~-9%"=="\dlc\hub\" (
	SET "___FOLDER=dlc_%~n1"
) ELSE SET "___FOLDER=%~n1"

SET ___MODDED_%___FOLDER%=1

IF DEFINED ___BACKED_UP_%___FOLDER% EXIT /B 0

IF "%~1"==".\base\EternalMod.streamdb" EXIT /B 0

IF NOT DEFINED ___TEMP (
	ECHO 		Backing up game files...
	SET ___TEMP=1
)

SET ___BACKED_UP_%___FOLDER%=1
ECHO 			Backing up "%~nx1"...
>NUL COPY /Y "%~1" "%~1.backup"
IF NOT ERRORLEVEL 1 EXIT /B 0

SET ___BACKED_UP_%___FOLDER%=
CALL :FunctionCallForModdables :FunctionInitializeModdedVariable
CALL :FunctionWriteConfiguration

SET "___TEMP=%~1"
SET "___TEMP=%___TEMP:~7%"
CALL :FunctionEchoError "%~nx1" couldn't be backed up!
ECHO/
ECHO 	Something went wrong while trying to copy -/DOOMEternal/base/%___TEMP:\=/% to -/DOOMEternal/base/%___TEMP:\=/%.backup
ECHO/
ECHO 	Please make sure that neither of the files are in use by another program (such as DOOM Eternal itself, %___PLATFORM%, anti-virus programs, or other software), then run this batch file again.
ECHO/
GOTO Exit


:FunctionCallForModdables
IF NOT DEFINED ___OWNS_CAMPAIGN GOTO FunctionCallForModdablesPostCampaignA

CALL %1 game\sp\e1m1_intro\e1m1_intro.resources                               e1m1_intro
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m1_intro\e1m1_intro_patch1.resources                        e1m1_intro_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m1_intro\e1m1_intro_patch2.resources                        e1m1_intro_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m1_intro\e1m1_intro_patch3.resources                        e1m1_intro_patch3
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m2_battle\e1m2_battle.resources                             e1m2_battle
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m2_battle\e1m2_battle_patch1.resources                      e1m2_battle_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m2_battle\e1m2_battle_patch2.resources                      e1m2_battle_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m2_battle\e1m2_battle_patch3.resources                      e1m2_battle_patch3
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m3_cult\e1m3_cult.resources                                 e1m3_cult
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m3_cult\e1m3_cult_patch1.resources                          e1m3_cult_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m3_cult\e1m3_cult_patch2.resources                          e1m3_cult_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m3_cult\e1m3_cult_patch3.resources                          e1m3_cult_patch3
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m4_boss\e1m4_boss.resources                                 e1m4_boss
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m4_boss\e1m4_boss_patch1.resources                          e1m4_boss_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e1m4_boss\e1m4_boss_patch2.resources                          e1m4_boss_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m1_nest\e2m1_nest.resources                                 e2m1_nest
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m1_nest\e2m1_nest_patch1.resources                          e2m1_nest_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m1_nest\e2m1_nest_patch2.resources                          e2m1_nest_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m2_base\e2m2_base.resources                                 e2m2_base
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m2_base\e2m2_base_patch1.resources                          e2m2_base_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m2_base\e2m2_base_patch2.resources                          e2m2_base_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m2_base\e2m2_base_patch3.resources                          e2m2_base_patch3
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m3_core\e2m3_core.resources                                 e2m3_core
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m3_core\e2m3_core_patch1.resources                          e2m3_core_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m3_core\e2m3_core_patch2.resources                          e2m3_core_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m3_core\e2m3_core_patch3.resources                          e2m3_core_patch3
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m4_boss\e2m4_boss.resources                                 e2m4_boss
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m4_boss\e2m4_boss_patch1.resources                          e2m4_boss_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e2m4_boss\e2m4_boss_patch2.resources                          e2m4_boss_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m1_slayer\e3m1_slayer.resources                             e3m1_slayer
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m1_slayer\e3m1_slayer_patch1.resources                      e3m1_slayer_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m1_slayer\e3m1_slayer_patch2.resources                      e3m1_slayer_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m1_slayer\e3m1_slayer_patch3.resources                      e3m1_slayer_patch3
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m2_hell\e3m2_hell.resources                                 e3m2_hell
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m2_hell\e3m2_hell_patch1.resources                          e3m2_hell_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m2_hell\e3m2_hell_patch2.resources                          e3m2_hell_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m2_hell_b\e3m2_hell_b.resources                             e3m2_hell_b
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m2_hell_b\e3m2_hell_b_patch1.resources                      e3m2_hell_b_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m2_hell_b\e3m2_hell_b_patch2.resources                      e3m2_hell_b_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m3_maykr\e3m3_maykr.resources                               e3m3_maykr
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m3_maykr\e3m3_maykr_patch1.resources                        e3m3_maykr_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m3_maykr\e3m3_maykr_patch2.resources                        e3m3_maykr_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m3_maykr\e3m3_maykr_patch3.resources                        e3m3_maykr_patch3
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m4_boss\e3m4_boss.resources                                 e3m4_boss
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m4_boss\e3m4_boss_patch1.resources                          e3m4_boss_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m4_boss\e3m4_boss_patch2.resources                          e3m4_boss_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\sp\e3m4_boss\e3m4_boss_patch3.resources                          e3m4_boss_patch3
IF ERRORLEVEL 1 EXIT /B 1

:FunctionCallForModdablesPostCampaignA
IF NOT DEFINED ___OWNS_ANCIENT_GODS_ONE GOTO FunctionCallForModdablesPostAncientGodsOneA

CALL %1 game\dlc\e4m1_rig\e4m1_rig.resources                                  e4m1_rig
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc\e4m1_rig\e4m1_rig_patch1.resources                           e4m1_rig_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc\e4m1_rig\e4m1_rig_patch2.resources                           e4m1_rig_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc\e4m2_swamp\e4m2_swamp.resources                              e4m2_swamp
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc\e4m2_swamp\e4m2_swamp_patch1.resources                       e4m2_swamp_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc\e4m2_swamp\e4m2_swamp_patch2.resources                       e4m2_swamp_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc\e4m3_mcity\e4m3_mcity.resources                              e4m3_mcity
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc\e4m3_mcity\e4m3_mcity_patch1.resources                       e4m3_mcity_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc\e4m3_mcity\e4m3_mcity_patch2.resources                       e4m3_mcity_patch2
IF ERRORLEVEL 1 EXIT /B 1

:FunctionCallForModdablesPostAncientGodsOneA
IF NOT DEFINED ___OWNS_ANCIENT_GODS_TWO GOTO FunctionCallForModdablesPostAncientGodsTwo

CALL %1 game\dlc2\e5m1_spear\e5m1_spear.resources                             e5m1_spear
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m1_spear\e5m1_spear_patch1.resources                      e5m1_spear_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m1_spear\e5m1_spear_patch2.resources                      e5m1_spear_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m2_earth\e5m2_earth.resources                             e5m2_earth
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m2_earth\e5m2_earth_patch1.resources                      e5m2_earth_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m2_earth\e5m2_earth_patch2.resources                      e5m2_earth_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m3_hell\e5m3_hell.resources                               e5m3_hell
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m3_hell\e5m3_hell_patch1.resources                        e5m3_hell_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m3_hell\e5m3_hell_patch2.resources                        e5m3_hell_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m4_boss\e5m4_boss.resources                               e5m4_boss
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc2\e5m4_boss\e5m4_boss_patch1.resources                        e5m4_boss_patch1
IF ERRORLEVEL 1 EXIT /B 1

:FunctionCallForModdablesPostAncientGodsTwo
IF NOT DEFINED ___OWNS_HORDE GOTO FunctionCallForModdablesPostHorde

CALL %1 game\horde\e6m1_cult_horde\e6m1_cult_horde.resources                  e6m1_cult_horde
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\horde\e6m1_cult_horde\e6m1_cult_horde_patch1.resources           e6m1_cult_horde_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\horde\e6m2_earth_horde\e6m2_earth_horde.resources                e6m2_earth_horde
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\horde\e6m2_earth_horde\e6m2_earth_horde_patch1.resources         e6m2_earth_horde_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\horde\e6m3_mcity_horde\e6m3_mcity_horde.resources                e6m3_mcity_horde
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\horde\e6m3_mcity_horde\e6m3_mcity_horde_patch1.resources         e6m3_mcity_horde_patch1
IF ERRORLEVEL 1 EXIT /B 1

:FunctionCallForModdablesPostHorde
CALL %1 gameresources.resources                                               gameresources
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 gameresources_patch1.resources                                        gameresources_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 gameresources_patch2.resources                                        gameresources_patch2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 gameresources_patch3.resources                                        gameresources_patch3
IF ERRORLEVEL 1 EXIT /B 1

IF NOT DEFINED ___OWNS_ANCIENT_GODS_ONE GOTO FunctionCallForModdablesPostAncientGodsOneB

CALL %1 game\dlc\hub\hub.resources                                            dlc_hub
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\dlc\hub\hub_patch1.resources                                     dlc_hub_patch1
IF ERRORLEVEL 1 EXIT /B 1

:FunctionCallForModdablesPostAncientGodsOneB
IF NOT DEFINED ___OWNS_CAMPAIGN GOTO FunctionCallForModdablesPostCampaignB

CALL %1 game\hub\hub.resources                                                hub
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\hub\hub_patch1.resources                                         hub_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\hub\hub_patch2.resources                                         hub_patch2
IF ERRORLEVEL 1 EXIT /B 1

:FunctionCallForModdablesPostCampaignB
CALL %1 meta.resources                                                        meta
IF ERRORLEVEL 1 EXIT /B 1

IF NOT DEFINED ___OWNS_BATTLEMODE GOTO FunctionCallForModdablesPostBattleMode

CALL %1 game\pvp\pvp_bronco\pvp_bronco.resources                              pvp_bronco
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_bronco\pvp_bronco_patch1.resources                       pvp_bronco_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_darkmetal\pvp_darkmetal.resources                        pvp_darkmetal
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_darkmetal\pvp_darkmetal_patch1.resources                 pvp_darkmetal_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_deathvalley\pvp_deathvalley.resources                    pvp_deathvalley
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_deathvalley\pvp_deathvalley_patch1.resources             pvp_deathvalley_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_inferno\pvp_inferno.resources                            pvp_inferno
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_inferno\pvp_inferno_patch1.resources                     pvp_inferno_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_laser\pvp_laser.resources                                pvp_laser
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_laser\pvp_laser_patch1.resources                         pvp_laser_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_shrapnel\pvp_shrapnel.resources                          pvp_shrapnel
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_shrapnel\pvp_shrapnel_patch1.resources                   pvp_shrapnel_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_sideswipe\pvp_sideswipe.resources                        pvp_sideswipe
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_sideswipe\pvp_sideswipe_patch1.resources                 pvp_sideswipe_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_thunder\pvp_thunder.resources                            pvp_thunder
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_thunder\pvp_thunder_patch1.resources                     pvp_thunder_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_zap\pvp_zap.resources                                    pvp_zap
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\pvp\pvp_zap\pvp_zap_patch1.resources                             pvp_zap_patch1
IF ERRORLEVEL 1 EXIT /B 1

:FunctionCallForModdablesPostBattleMode
CALL %1 game\shell\shell.resources                                            shell
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\shell\shell_patch1.resources                                     shell_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\tutorials\tutorial_demons.resources                              tutorial_demons
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\tutorials\tutorial_pvp_laser\tutorial_pvp_laser.resources        tutorial_pvp_laser
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\tutorials\tutorial_pvp_laser\tutorial_pvp_laser_patch1.resources tutorial_pvp_laser_patch1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 game\tutorials\tutorial_sp.resources                                  tutorial_sp
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 warehouse.resources                                                   warehouse
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 warehouse_patch1.resources                                            warehouse_patch1
IF ERRORLEVEL 1 EXIT /B 1

CALL %1 sound\soundbanks\pc\music.snd                                         music
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\music_patch_1.snd                                 music_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\music_patch_2.snd                                 music_patch_2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\sfx.snd                                           sfx
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\sfx_patch_1.snd                                   sfx_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\sfx_patch_2.snd                                   sfx_patch_2
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\sfx_patch_3.snd                                   sfx_patch_3
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_English(US).snd                                vo_English(US)
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_English(US)_patch_1.snd                        vo_English(US)_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_French(France).snd                             vo_French(France)
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_French(France)_patch_1.snd                     vo_French(France)_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_German.snd                                     vo_German
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_German_patch_1.snd                             vo_German_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Italian.snd                                    vo_Italian
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Italian_patch_1.snd                            vo_Italian_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Japanese.snd                                   vo_Japanese
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Japanese_patch_1.snd                           vo_Japanese_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Polish.snd                                     vo_Polish
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Polish_patch_1.snd                             vo_Polish_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Portuguese(Brazil).snd                         vo_Portuguese(Brazil)
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Portuguese(Brazil)_patch_1.snd                 vo_Portuguese(Brazil)_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Russian.snd                                    vo_Russian
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Russian_patch_1.snd                            vo_Russian_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Spanish(Mexico).snd                            vo_Spanish(Mexico)
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Spanish(Mexico)_patch_1.snd                    vo_Spanish(Mexico)_patch_1
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Spanish(Spain).snd                             vo_Spanish(Spain)
IF ERRORLEVEL 1 EXIT /B 1
CALL %1 sound\soundbanks\pc\vo_Spanish(Spain)_patch_1.snd                     vo_Spanish(Spain)_patch_1
IF ERRORLEVEL 1 EXIT /B 1

CALL %1 packagemapspec.json                                                   packagemapspec
IF ERRORLEVEL 1 EXIT /B 1

EXIT /B 0


:FunctionDeleteEternalModStreamDB
IF NOT EXIST ".\base\EternalMod.streamdb" EXIT /B 0

ECHO 		Deleting "EternalMod.streamdb"...
>NUL DEL ".\base\EternalMod.streamdb"
IF NOT ERRORLEVEL 1 EXIT /B 0

CALL :FunctionWriteConfiguration

CALL :FunctionEchoError "EternalMod.streamdb" couldn't be deleted!
ECHO/
ECHO 	Something went wrong while trying to delete -/DOOMEternal/base/EternalMod.streamdb
ECHO/
ECHO 	Please make sure that that file isn't in use by another program (such as DOOM Eternal itself, %___PLATFORM%, anti-virus programs, or other software), then run this batch file again.
ECHO/
GOTO Exit


:FunctionEchoError
ECHO/
ECHO/
ECHO 	%___ESC:X=1;41;93m%ERROR: %*%___EOL_COLOUR%
EXIT /B 0


:FunctionInitializeBackupVariable
SET ___BACKED_UP_%~n2=
EXIT /B 0


:FunctionInitializeModdedVariable
SET ___MODDED_%~n2=
EXIT /B 0


:FunctionRedownloadInstructions
IF "%~1"=="1" (
	ECHO 	Please %___PLATFORM_REPAIR% DOOM Eternal's installation through %___PLATFORM%, open "%___CONFIGURATION_FILE:\=/%" in Notepad, change ":RESET_BACKUPS=0" to ":RESET_BACKUPS=1", save the file, and choose to update the backups the next time that you run this batch file.
	ECHO/
	ECHO/
)
IF "%___PLATFORM%"=="Steam" (
	ECHO 	To verify DOOM Eternal through Steam, right-click DOOM Eternal in your Steam library, choose "Properties..." ^> "Installed Files" ^> "Verify integrity of game files", and wait for Steam to redownload the default files.
) ELSE IF "%___PLATFORM%"=="GOG Galaxy" (
	ECHO 	To verify DOOM Eternal through GOG Galaxy, right-click DOOM Eternal in your owned games, choose "Manage installation" ^> "Verify / Repair", and wait for GOG Galaxy to redownload the default files.
) ELSE IF "%___PLATFORM%"=="the Xbox App" (
	ECHO 	I'm not sure how to repair games through Microsoft Store or the Xbox App, sorry. You might have to reinstall DOOM Eternal and use UWPDumper to dump it again.
) ELSE IF "%___PLATFORM%"=="the Epic Games Launcher" (
	ECHO 	To verify DOOM Eternal through the Epic Games Launcher, click on the three dots next to DOOM Eternal in your Epic Games Library, choose "Manage" ^> "Verify", and wait for the Epic Games Launcher to redownload the default files.
) ELSE ECHO 	Please look up how to repair games through %___PLATFORM%. Worst-case scenario, uninstalling and reinstalling DOOM Eternal should do the trick.
EXIT /B 0


:FunctionWriteConfiguration
>".\%___CONFIGURATION_FILE%" ECHO :ASSET_VERSION=%___ASSET_VERSION%
IF DEFINED ___AUTO_LAUNCH_GAME (
	>>".\%___CONFIGURATION_FILE%" ECHO :AUTO_LAUNCH_GAME=1
) ELSE (
	>>".\%___CONFIGURATION_FILE%" ECHO :AUTO_LAUNCH_GAME=0
)
IF DEFINED ___AUTO_UPDATE (
	>>".\%___CONFIGURATION_FILE%" ECHO :AUTO_UPDATE=%___AUTO_UPDATE%
)
IF DEFINED ___COMPRESS_TEXTURES (
	>>".\%___CONFIGURATION_FILE%" ECHO :COMPRESS_TEXTURES=1
) ELSE (
	>>".\%___CONFIGURATION_FILE%" ECHO :COMPRESS_TEXTURES=0
)
IF DEFINED ___DISABLE_MULTITHREADING (
	>>".\%___CONFIGURATION_FILE%" ECHO :DISABLE_MULTITHREADING=1
) ELSE (
	>>".\%___CONFIGURATION_FILE%" ECHO :DISABLE_MULTITHREADING=0
)
SET "___TEMP=%___GAME_PARAMETERS:^=^^%"
SET "___TEMP=%___TEMP:&=^&%"
SET "___TEMP=%___TEMP:)=^)%"
SET "___TEMP=%___TEMP:<=^<%"
SET "___TEMP=%___TEMP:>=^>%"
SET "___TEMP=%___TEMP:|=^|%"
IF DEFINED ___GAME_PARAMETERS (
	>>".\%___CONFIGURATION_FILE%" ECHO :GAME_PARAMETERS=%___TEMP%
) ELSE (
	>>".\%___CONFIGURATION_FILE%" ECHO :GAME_PARAMETERS=
)
IF DEFINED ___HAS_CHECKED_RESOURCES (
	>>".\%___CONFIGURATION_FILE%" ECHO :HAS_CHECKED_RESOURCES=1
) ELSE (
	>>".\%___CONFIGURATION_FILE%" ECHO :HAS_CHECKED_RESOURCES=0
)
>>".\%___CONFIGURATION_FILE%" ECHO :HAS_READ_FIRST_TIME=1
IF DEFINED ___ONLINE_SAFE (
	>>".\%___CONFIGURATION_FILE%" ECHO :ONLINE_SAFE=1
) ELSE (
	>>".\%___CONFIGURATION_FILE%" ECHO :ONLINE_SAFE=0
)
>>".\%___CONFIGURATION_FILE%" ECHO :RESET_BACKUPS=0
IF DEFINED ___SLOW (
	>>".\%___CONFIGURATION_FILE%" ECHO :SLOW=1
) ELSE (
	>>".\%___CONFIGURATION_FILE%" ECHO :SLOW=0
)
IF DEFINED ___VERBOSE (
	>>".\%___CONFIGURATION_FILE%" ECHO :VERBOSE=1
) ELSE (
	>>".\%___CONFIGURATION_FILE%" ECHO :VERBOSE=0
)
>>".\%___CONFIGURATION_FILE%" ECHO/
CALL :FunctionCallForModdables :FunctionWriteConfigurationResources
EXIT /B 0

:FunctionWriteConfigurationResources
IF DEFINED ___BACKED_UP_%~n2 >>".\%___CONFIGURATION_FILE%" ECHO %~n2.backup
IF DEFINED ___MODDED_%~n2    >>".\%___CONFIGURATION_FILE%" ECHO %~n2%~x1
EXIT /B 0


:Exit
<NUL SET /P ="Press any key to exit . . . "
>NUL PAUSE
EXIT /B 1


TODO Instead of telling the user to set ":RESET_BACKUPS" to "1" manually, set it to a different number for them and have the batch file not let them say "no" to updating resources
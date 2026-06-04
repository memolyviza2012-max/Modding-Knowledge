@echo off
set PYTHONIOENCODING=utf-8
echo ========================================
echo  Step 2: Import Translation CSV back into Game.locres
echo ========================================

set CSV_PATH=Translation\Game_th.csv
set OUTPUT_LOCRES=Pack\DeadIsland\Content\Localization\Game\en\Game.locres

if not exist "%CSV_PATH%" (
    echo [ERROR] Translation CSV file not found at: %CSV_PATH%
    pause
    exit /b
)

if not exist Pack\DeadIsland\Content\Localization\Game\en mkdir Pack\DeadIsland\Content\Localization\Game\en
pylocres from-csv -p "%CSV_PATH%" -o "%OUTPUT_LOCRES%" -v 0
echo.
echo Success! New Game.locres created inside Pack folder!
pause

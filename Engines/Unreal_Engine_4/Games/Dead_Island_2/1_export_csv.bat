@echo off
set PYTHONIOENCODING=utf-8
echo ========================================
echo  Step 0: Extract Game.locres from Dead Island 2
echo ========================================

echo Running DI2_Extractor (CUE4Parse CLI)...
dotnet run --project DI2_Extractor\DI2_Extractor.csproj -c Release -- --filter "Localization/Game/en"

echo.
echo ========================================
echo  Step 1: Convert Game.locres to Game_th.csv
echo ========================================

set LOCRES_PATH=Extracted\DeadIsland\Content\Localization\Game\en\Game.locres
set CSV_PATH=Translation\Game_th.csv

if not exist "%LOCRES_PATH%" (
    echo [ERROR] Game.locres not found at: %LOCRES_PATH%
    echo Please make sure Step 0 completed successfully.
    pause
    exit /b
)

if not exist Translation mkdir Translation
pylocres to-csv -p "%LOCRES_PATH%" -o "%CSV_PATH%"
echo.
echo Success! File %CSV_PATH% has been created in the Translation folder!
pause

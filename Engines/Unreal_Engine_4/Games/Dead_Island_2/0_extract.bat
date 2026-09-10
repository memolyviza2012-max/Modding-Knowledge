@echo off
echo ========================================
echo  Dead Island 2 - CUE4Parse CLI Extractor
echo ========================================
echo.
echo Usage:
echo   0_extract.bat                    - Extract all .locres files
echo   0_extract.bat --list             - List all .locres files in game
echo   0_extract.bat --filter <pattern> - Extract files matching pattern
echo.

dotnet run --project DI2_Extractor\DI2_Extractor.csproj -c Release -- %*

echo.
pause

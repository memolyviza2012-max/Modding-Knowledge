# Deploy_Mod.ps1
# Deploys GOTG Thai Mod files to the game directory
# Target: F:\Epic Games\MarvelGOTG\retail\

param(
    [string]$GameDir = "F:\Epic Games\MarvelGOTG\retail",
    [string]$ModSource = "E:\Mod_Workspace\MarvelGOTG_Mod_Workspace\GOTG_Translation"
)

$ErrorActionPreference = "Stop"

Write-Host "GOTG Thai Mod Deployment Script"
Write-Host "================================"

# Validate game directory exists
if (!(Test-Path $GameDir)) {
    Write-Host "[ERROR] Game directory not found: $GameDir"
    exit 1
}

# Validate gotg.exe exists in target
if (!(Test-Path "$GameDir\gotg.exe")) {
    Write-Host "[ERROR] gotg.exe not found in: $GameDir"
    exit 1
}

Write-Host "[OK] Game directory: $GameDir"

# Files to deploy
$files = @(
    @{Source = "$ModSource\build\version.dll"; Dest = "version.dll" },
    @{Source = "$ModSource\GOTG_Mod.ini"; Dest = "GOTG_Mod.ini" },
    @{Source = "$ModSource\rsrc\strings_th.json"; Dest = "strings_th.json" }
)

$deployCount = 0
foreach ($file in $files) {
    $sourcePath = $file.Source
    $destPath = Join-Path $GameDir $file.Dest

    if (!(Test-Path $sourcePath)) {
        Write-Host "[WARNING] Source file not found: $sourcePath"
        continue
    }

    Copy-Item -Path $sourcePath -Destination $destPath -Force
    if ($?) {
        Write-Host "[OK] Copied: $($file.Dest)"
        $deployCount++
    }
    else {
        Write-Host "[ERROR] Failed to copy: $($file.Dest)"
    }
}

Write-Host ""
if ($deployCount -eq $files.Count) {
    Write-Host "[OK] Deployment complete! $deployCount files copied."
    Write-Host ""
    Write-Host "Deployed files:"
    foreach ($file in $files) {
        $destPath = Join-Path $GameDir $file.Dest
        $size = (Get-Item $destPath).Length
        Write-Host "    $($file.Dest) ($size bytes)"
    }
}
else {
    Write-Host "[WARNING] Partial deployment: $deployCount/$($files.Count) files copied"
}

Write-Host ""
Write-Host "You can now launch the game to test the mod."
Write-Host "Enable Debug=1 in GOTG_Mod.ini to view mod logs."


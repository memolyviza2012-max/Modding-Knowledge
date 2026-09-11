#Requires -Version 5.1
<#
    ติดตั้งม็อดภาษาไทย XCOM: Chimera Squad
    - สำรองไฟล์ต้นฉบับ "ครั้งเดียว" ลงโฟลเดอร์ backup ข้าง ๆ สคริปต์ (ไม่ทับของเดิม)
    - คัดลอกไฟล์ม็อดทับ
    ใช้ uninstall.ps1 เพื่อคืนไฟล์เดิม
#>
param(
    [string]$GamePath = ''
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$files = Join-Path $root 'files'

function Find-Game {
    # 1) พาธที่ผู้ใช้ระบุ
    if ($GamePath -ne '' -and (Test-Path (Join-Path $GamePath 'XComGame\CookedPCConsole\DioShell_Main.upk'))) { return $GamePath }

    # 2) ไล่จาก Steam library ทุกไดรฟ์ — ยืนยันด้วย "ไฟล์ในเกม" ไม่ใช่ชื่อโฟลเดอร์
    # ต้องเป็นไฟล์ที่มีเฉพาะ Chimera Squad — XComGame.int มีใน XCOM 2 ด้วย
    $marker = 'XComGame\CookedPCConsole\DioShell_Main.upk'
    $roots = @()
    foreach ($d in (Get-PSDrive -PSProvider FileSystem)) {
        $roots += Join-Path $d.Root 'Program Files (x86)\Steam\steamapps\common'
        $roots += Join-Path $d.Root 'SteamLibrary\steamapps\common'
        $roots += Join-Path $d.Root 'Steam\steamapps\common'
        $roots += Join-Path $d.Root 'Games'
    }
    foreach ($r in $roots) {
        if (-not (Test-Path $r)) { continue }
        foreach ($dir in (Get-ChildItem -Path $r -Directory -ErrorAction SilentlyContinue)) {
            if (Test-Path (Join-Path $dir.FullName $marker)) { return $dir.FullName }
        }
    }
    return ''
}

$game = Find-Game
if ($game -eq '') {
    Write-Host 'หาโฟลเดอร์เกมไม่พบ' -ForegroundColor Red
    Write-Host 'ลองระบุเอง:  .\install.ps1 -GamePath "D:\...\XCOM-Chimera-Squad"'
    exit 1
}
Write-Host "พบเกมที่: $game" -ForegroundColor Cyan

# เก็บไฟล์สำรองไว้ในโฟลเดอร์เกม ไม่ใช่ข้าง ๆ สคริปต์
# ผู้เล่นจะลบโฟลเดอร์ที่แตก zip ทิ้งได้โดยไม่เสียทางกลับ
# และตัวติดตั้งแบบ .exe ก็ใช้ที่เดียวกันนี้ จึงถอนข้ามกันได้
$backup = Join-Path $game '_ThaiMod_Backup_Original'

$manifest = Get-Content (Join-Path $root 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$n_backup = 0
$n_copy = 0

foreach ($f in $manifest.files) {
    $rel = $f.path -replace '/', '\'
    $src = Join-Path $files $rel
    $dst = Join-Path $game $rel
    $bak = Join-Path $backup $rel

    if (-not (Test-Path $src)) { Write-Host "ไม่มีไฟล์ม็อด: $rel" -ForegroundColor Red; exit 1 }
    if (-not (Test-Path $dst)) { Write-Host "ไม่มีไฟล์เดิมในเกม: $rel" -ForegroundColor Red; exit 1 }

    # สำรองครั้งเดียว — ถ้ามีอยู่แล้วห้ามทับ (กันการสำรองทับไฟล์ที่ม็อดไว้แล้ว)
    if (-not (Test-Path $bak)) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $bak) | Out-Null
        Copy-Item $dst $bak
        $n_backup++
    }

    Copy-Item $src $dst -Force
    $n_copy++
    Write-Host ("  ติดตั้ง {0}" -f $rel)
}

Write-Host ''
Write-Host ("เสร็จสิ้น: คัดลอก {0} ไฟล์ / สำรองใหม่ {1} ไฟล์" -f $n_copy, $n_backup) -ForegroundColor Green
Write-Host ''
Write-Host 'ขั้นตอนสุดท้าย — ตั้งภาษาเกมเป็น "เกาหลี"' -ForegroundColor Yellow
Write-Host '  Steam > คลิกขวาที่ XCOM: Chimera Squad > Properties > Language > Korean'
Write-Host 'ม็อดวางข้อความไทยไว้ในช่องภาษาเกาหลี ภาษาอังกฤษต้นฉบับจึงยังอยู่ครบ'

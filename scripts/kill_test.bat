@echo off
REM Kill all PowerShell terminals started by launch_all.bat

where pwsh >nul 2>nul
if %errorlevel%==0 (
    set "PS_CMD=pwsh"
) else (
    set "PS_CMD=powershell"
)

call %PS_CMD% -NoProfile -Command ^
    "$keywords = @('Qdrant','Kolosal Server','Kolosal Test');" ^
    "Get-Process -Name powershell,pwsh -ErrorAction SilentlyContinue | ForEach-Object {" ^
    "  $proc = $_;" ^
    "  $title = $proc.MainWindowTitle;" ^
    "  $cmd = ($proc.Path + ' ' + ($proc.StartInfo.Arguments));" ^
    "  foreach ($kw in $keywords) {" ^
    "    if ($title -like ('*' + $kw + '*') -or $cmd -like ('*' + $kw + '*')) {" ^
    "      Write-Host \"Killing process $($proc.Id) with title '$title' and command '$cmd'\";" ^
    "      Stop-Process -Id $proc.Id -Force;" ^
    "      break;" ^
    "    }" ^
    "  }" ^
    "}"

echo All Kolosal-related PowerShell terminals have been terminated.
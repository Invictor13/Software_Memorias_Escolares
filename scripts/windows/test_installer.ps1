param(
    [Parameter(Mandatory)] [string] $Installer,
    [Parameter(Mandatory)] [string] $TestPython
)

$ErrorActionPreference = 'Stop'
$setupPath = (Resolve-Path -LiteralPath $Installer).Path
$pythonPath = (Resolve-Path -LiteralPath $TestPython).Path
$versionPattern = '^OKAMI-Memorias-([0-9]+\.[0-9]+\.[0-9]+)-Windows-x64\.exe$'
if ((Split-Path -Leaf $setupPath) -notmatch $versionPattern) {
    throw 'Nome do instalador incompatível com o teste.'
}
$appVersion = $Matches[1]
$registryKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\OkamiMemorias-$appVersion"
if (Test-Path -LiteralPath $registryKey) {
    throw 'Esta versão já está instalada para o usuário atual.'
}

$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$testPath = Join-Path $repo ("build/windows/test-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $testPath -Force | Out-Null
$installPath = Join-Path $testPath 'instalado'
$outputPath = Join-Path $testPath 'pdfs'
$sourcePath = Join-Path $testPath 'turma'

@'
import sys
from pathlib import Path
from PIL import Image

root = Path(sys.argv[1])
(root / "pdfs").mkdir()
for name, count in (("Ana", 1), ("Bruno", 4), ("Lusia", 5)):
    directory = root / "turma" / name
    directory.mkdir(parents=True)
    for number in range(count):
        with Image.new("RGB", (200, 300), (30 * number, 70, 140)) as image:
            image.save(directory / f"{number}.png")
'@ | & $pythonPath - $testPath
if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar as fotos sintéticas.' }

$setup = Start-Process -FilePath $setupPath -ArgumentList "/S /D=$installPath" -WindowStyle Hidden -Wait -PassThru
if ($setup.ExitCode -ne 0) { throw "Instalador retornou $($setup.ExitCode)." }
$uninstallPath = Join-Path $installPath 'Desinstalar.exe'
$shortcutName = "OKAMI Mem$([char]0x00F3)rias Escolares $appVersion.lnk"
$shortcut = Join-Path ([Environment]::GetFolderPath('Programs')) $shortcutName
try {
    if (-not (Test-Path -LiteralPath $shortcut)) { throw 'Atalho do menu Iniciar ausente.' }
    if (-not (Test-Path -LiteralPath $registryKey)) { throw 'Entrada de desinstalação ausente.' }
    $marker = Join-Path $installPath 'arquivo-pessoal.txt'
    Set-Content -LiteralPath $marker -Value 'preservar'

    $launch = [System.Diagnostics.ProcessStartInfo]::new()
    $launch.FileName = Join-Path $installPath 'OKAMI-Memorias.exe'
    $launch.Arguments = '--verificar-instalacao "{0}" "{1}"' -f $sourcePath, $outputPath
    $launch.WorkingDirectory = $testPath
    $launch.UseShellExecute = $false
    $launch.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $launch.EnvironmentVariables['PATH'] = "$env:WINDIR\System32;$env:WINDIR"
    foreach ($variable in @('PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM_PLUGIN_PATH')) {
        $launch.EnvironmentVariables.Remove($variable)
    }
    $app = [System.Diagnostics.Process]::Start($launch)
    if (-not $app.WaitForExit(45000)) {
        $app.Kill()
        throw 'Tempo de verificação do aplicativo excedido.'
    }
    if ($app.ExitCode -ne 0) {
        $diagnostic = Join-Path $outputPath 'diagnostico-okami.txt'
        if (Test-Path -LiteralPath $diagnostic) { Get-Content -LiteralPath $diagnostic }
        throw "Aplicativo instalado retornou $($app.ExitCode)."
    }

@'
import sys
from pathlib import Path
from pypdf import PdfReader

root = Path(sys.argv[1])
paths = sorted(root.glob("*.pdf"))
assert [path.stem for path in paths] == ["Ana", "Bruno", "Lusia"]
for path, photos in zip(paths, ([1], [4], [4, 1])):
    pdf = PdfReader(path)
    assert [len(page.images) for page in pdf.pages] == photos
    for page in pdf.pages:
        factor = 25.4 / 72
        assert round(float(page.mediabox.width) * factor, 3) == 210
        assert round(float(page.mediabox.height) * factor, 3) == 297
        assert page.extract_text().strip() == path.stem
        rects = [values for values, cmd in page.get_contents().operations if cmd == b"re"]
        assert round(float(rects[1][0]) * factor, 3) == 25
print("PDFs A4 conferidos: 1, 1 e 2 paginas.")
'@ | & $pythonPath - $outputPath
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao verificar os PDFs instalados.' }
}
finally {
    if (Test-Path -LiteralPath $uninstallPath) {
        $uninstall = Start-Process -FilePath $uninstallPath -ArgumentList '/S' -WindowStyle Hidden -Wait -PassThru
        if ($uninstall.ExitCode -ne 0) { throw "Desinstalador retornou $($uninstall.ExitCode)." }
    }
}
if ((Test-Path -LiteralPath $shortcut) -or (Test-Path -LiteralPath $registryKey) -or
    (Test-Path -LiteralPath $launch.FileName)) {
    throw 'A desinstalação deixou componentes registrados.'
}
if ((Get-Content -LiteralPath $marker) -ne 'preservar') {
    throw 'A desinstalação alterou o arquivo particular.'
}
Write-Output "Instalação, execução com PATH isolado e desinstalação verificadas em $testPath"

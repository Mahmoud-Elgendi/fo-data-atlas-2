#Requires -Version 5.1
<#
.SYNOPSIS
Install or update F&O Data Atlas from public release assets, without Git/npm/gh.
.DESCRIPTION
Requires an existing Python 3.10+. Uses normal HTTPS and checksum/manifest checks.
Runs the original setup wizard; preserves older versions and the shared cache.
It does not change execution policy, install runtimes or activate an IDE silently.
.EXAMPLE
& .\Install-Atlas.ps1
.EXAMPLE
& .\Install-Atlas.ps1 -Tag v0.5.2 -CheckOnly
#>
[CmdletBinding()]
param(
    [string]$Tag,
    [string]$PythonPath,
    [string]$Project = (Get-Location).Path,
    [ValidateSet('codex', 'claude', 'both')][string]$HostTool,
    [ValidateSet('global', 'project')][string]$Scope,
    [ValidateSet('core', 'full')][string]$MetadataProfile,
    [string]$DownloadDirectory,
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'
$repository = 'Mahmoud-Elgendi/fo-data-atlas-2'

function Find-AtlasPython {
    param([string]$ExplicitPath)
    $candidates = @()
    if ($ExplicitPath) {
        $candidates += @{ File = $ExplicitPath; Prefix = @() }
    } elseif ($env:FO_ATLAS_PYTHON) {
        $candidates += @{ File = $env:FO_ATLAS_PYTHON; Prefix = @() }
    } else {
        if ($env:CONDA_PREFIX) {
            $candidates += @{ File = (Join-Path $env:CONDA_PREFIX 'python.exe'); Prefix = @() }
        }
        $candidates += @{ File = (Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'); Prefix = @() }
        $candidates += @{ File = 'py'; Prefix = @('-3') }
        $candidates += @{ File = 'python'; Prefix = @() }
        $candidates += @{ File = 'python3'; Prefix = @() }
    }
    foreach ($candidate in $candidates) {
        $found = Get-Command $candidate.File -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $found -or $found.Source -match '\\Microsoft\\WindowsApps\\python(?:3)?\.exe$') { continue }
        $probeArgs = @($candidate.Prefix) + @('-c', 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)')
        & $found.Source @probeArgs 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { return @{ File = $found.Source; Prefix = @($candidate.Prefix) } }
    }
    throw 'Python 3.10+ was not found. Run this in your conda/base terminal, or pass -PythonPath with an existing Python executable. No runtime or administrator installation was attempted.'
}

function Save-AtlasAsset {
    param($Asset, [string]$ReleaseTag, [string]$Destination)
    if ($Asset.name -notmatch '^[A-Za-z0-9_.-]+$' -or $Asset.digest -notmatch '^sha256:[a-fA-F0-9]{64}$') {
        throw 'Release asset name or SHA256 digest is invalid.'
    }
    if ([long]$Asset.size -le 0 -or [long]$Asset.size -ge 2GB) { throw 'Unexpected release asset size.' }
    $expectedUrl = "https://github.com/$repository/releases/download/$ReleaseTag/$($Asset.name)"
    if ($Asset.browser_download_url -ne $expectedUrl) { throw 'Unexpected release download location.' }
    Write-Host "Downloading $($Asset.name)..."
    $savedProgress = $ProgressPreference
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -UseBasicParsing -Uri $expectedUrl -OutFile $Destination -TimeoutSec 600
    } finally { $ProgressPreference = $savedProgress }
    if ((Get-Item -LiteralPath $Destination).Length -ne [long]$Asset.size) { throw 'Downloaded asset size mismatch.' }
    $expectedHash = $Asset.digest.Substring(7)
    if ((Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash -ine $expectedHash) { throw 'Downloaded asset checksum mismatch.' }
}

try {
    Write-Host ''
    Write-Host 'F&O DATA ATLAS - Developed by Mahmoud Elgendi'
    Write-Host 'Building D365 F&O, Microsoft Fabric and AI-assisted SQL solutions.'
    Write-Host 'Mobile / WhatsApp: 00966542128150 | www.mahmoudelgendi.com'
    Write-Host 'Public installer: no npm, Git or GitHub CLI. No admin rights required.'
    if ($Tag -and $Tag -notmatch '^v\d+\.\d+\.\d+$') { throw 'Use a stable tag such as v0.5.2.' }
    $python = Find-AtlasPython $PythonPath
    # Enables TLS 1.2 for older Windows PowerShell without weakening certificate checks.
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $releasePath = 'latest'
    if ($Tag) { $releasePath = "tags/$Tag" }
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$repository/releases/$releasePath" -Headers @{
        'User-Agent' = 'fo-data-atlas-public-installer'; 'Accept' = 'application/vnd.github+json'
    } -TimeoutSec 30
    if ($release.draft -or $release.prerelease -or $release.tag_name -notmatch '^v\d+\.\d+\.\d+$') {
        throw 'Only published stable releases can be installed.'
    }
    if ($Tag -and $release.tag_name -ne $Tag) { throw 'Release tag mismatch.' }
    $Tag = $release.tag_name
    $version = $Tag.Substring(1)
    $zipName = "fo-data-atlas-$version.zip"
    $zipAssets = @($release.assets | Where-Object name -eq $zipName)
    $helperAssets = @($release.assets | Where-Object name -eq 'github_release.py')
    if ($zipAssets.Count -ne 1 -or $helperAssets.Count -ne 1) { throw 'Release is missing unique tools/helper assets.' }
    if (-not $DownloadDirectory) {
        $DownloadDirectory = Join-Path $env:LOCALAPPDATA 'fo-atlas\setup'
    }
    $work = Join-Path ([IO.Path]::GetFullPath($DownloadDirectory)) ([Guid]::NewGuid().ToString('N').Substring(0, 8))
    New-Item -ItemType Directory -Path $work -Force | Out-Null
    $zipPath = Join-Path $work $zipName
    $helperPath = Join-Path $work 'github_release.py'
    Write-Host "Release: $Tag | Python: $($python.File)"
    Write-Host "Project: $Project"
    Save-AtlasAsset $helperAssets[0] $Tag $helperPath
    Save-AtlasAsset $zipAssets[0] $Tag $zipPath

    # Public transport is confined to this setup process. Installed release files
    # and their hashes remain unchanged. The normal metadata verifier/cache is reused.
    $bootstrap = @'
import importlib.util
import json
from pathlib import Path
import sys
import urllib.parse
import urllib.request

REPOSITORY = 'Mahmoud-Elgendi/fo-data-atlas-2'

def download_public(repo, tag, asset, folder):
    if repo != REPOSITORY:
        raise ValueError('Unexpected metadata repository.')
    github.version_tuple(tag)
    if github.safe_relative(asset).as_posix() != asset or '/' in asset:
        raise ValueError('Metadata asset must be a single safe filename.')
    url = f'https://github.com/{repo}/releases/download/{tag}/{asset}'
    request = urllib.request.Request(url, headers={'User-Agent': 'fo-data-atlas-public-installer'})
    print('Downloading uncached metadata: ' + asset, flush=True)
    with urllib.request.urlopen(request, timeout=120) as source:
        final = urllib.parse.urlparse(source.geturl())
        if final.scheme != 'https' or final.hostname not in {
            'github.com', 'objects.githubusercontent.com', 'release-assets.githubusercontent.com',
            'github-releases.githubusercontent.com'
        }:
            raise ValueError('Unexpected metadata redirect.')
        with github.disk(Path(folder) / asset).open('xb') as output:
            downloaded = 0
            while True:
                block = source.read(1024 * 1024)
                if not block:
                    break
                downloaded += len(block)
                if downloaded >= 2 * 1024**3:
                    raise ValueError('Metadata download exceeds 2 GiB.')
                output.write(block)

def public_transport(arguments, timeout=30):
    # Only the exact metadata acquisition operation is supported by this adapter.
    if (len(arguments) != 9 or arguments[:2] != ['release', 'download']
            or arguments[3] != '--repo' or arguments[5] != '--pattern'
            or arguments[7] != '--dir'):
        raise ValueError('Unsupported public setup operation.')
    repo = arguments[4].removeprefix('github.com/')
    download_public(repo, arguments[2], arguments[6], arguments[8])
    return ''

def main(argv):
    global github
    helper, archive, work, version, project, host, scope, profile, check_only = argv
    spec = importlib.util.spec_from_file_location('github_release', helper)
    github = importlib.util.module_from_spec(spec)
    sys.modules['github_release'] = github
    spec.loader.exec_module(github)
    pack = github.extract_verified(Path(archive), Path(work) / 'verified', version)
    catalog = github.read_json(pack / 'metadata-catalog.json', {})
    if catalog.get('repository') != REPOSITORY:
        raise ValueError('Unexpected catalog repository.')
    print('Verified tools archive and all package files.', flush=True)
    if check_only == 'True':
        print(json.dumps({'version': version, 'archive_verified': True,
                          'installation_started': False, 'work': work}))
        return 0
    github.gh = public_transport
    sys.path.insert(0, str(pack / 'scripts'))
    import install
    options = ['--interactive', '--project', project]
    for name, value in (('--host', host), ('--scope', scope), ('--metadata-profile', profile)):
        if value != '-':
            options += [name, value]
    result = install.main(options)
    note = Path(work) / 'INSTALLATION.md'
    note.write_text(
        '# Atlas public setup run\n\n'
        f'Release: v{version}\nProject: {project}\n'
        f'Setup exit code: {result}\n'
        'Tools were acquired through public HTTPS and checked against release digests and package manifests. '
        'Metadata used the original hash-verified shared cache. Previous installed versions are preserved. '
        'Follow the activation instructions printed by setup; host loading and SQL access are separate checks.\n'
        'For future updates, rerun Install-Atlas.ps1. This transport adapter is setup-only; the old packaged '
        'github_release.py command still uses GitHub CLI. No GitHub credentials were collected.\n',
        encoding='utf-8')
    print('Setup run note: ' + str(note), flush=True)
    return result

if __name__ == '__main__':
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (OSError, ValueError, KeyError) as exc:
        print('Atlas public setup stopped: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
'@
    $checkText = $CheckOnly.IsPresent.ToString()
    $bootstrapPath = Join-Path $work 'bootstrap.py'
    Set-Content -LiteralPath $bootstrapPath -Value $bootstrap -Encoding UTF8
    # Nonempty placeholders survive Windows PowerShell 5.1 native argument passing.
    $hostValue = '-'; if ($HostTool) { $hostValue = $HostTool }
    $scopeValue = '-'; if ($Scope) { $scopeValue = $Scope }
    $profileValue = '-'; if ($MetadataProfile) { $profileValue = $MetadataProfile }
    $pythonArgs = @($python.Prefix) + @($bootstrapPath, $helperPath, $zipPath, $work, $version,
        $Project, $hostValue, $scopeValue, $profileValue, $checkText)
    & $python.File @pythonArgs
    if ($LASTEXITCODE -ne 0) { throw "Atlas setup returned code $LASTEXITCODE. Existing versions were retained; see the preceding error." }
    Write-Host "Downloads and setup evidence: $work"
} catch {
    Write-Error "Atlas setup stopped: $($_.Exception.Message)"
    exit 1
}

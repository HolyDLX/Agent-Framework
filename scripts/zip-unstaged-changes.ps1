$archiveName = "uncommitted-changes.zip"
$archive = Join-Path (Get-Location) $archiveName
$temp = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid())

$tracked = @(
    git diff HEAD `
        --name-only `
        --ignore-submodules=all `
        --diff-filter=ACMRTUXB `
        -- .
)

$untracked = @(
    git ls-files `
        --others `
        --exclude-standard `
        -- .
)

$files = @(
    $tracked + $untracked |
        Where-Object {
            $_ -and $_ -ne $archiveName
        } |
        Sort-Object -Unique
)

if ($files.Count -eq 0) {
    Write-Host "No uncommitted files found."
    return
}

try {
    New-Item -ItemType Directory -Path $temp | Out-Null

    foreach ($file in $files) {
        $target = Join-Path $temp $file
        $targetDirectory = Split-Path $target -Parent

        New-Item `
            -ItemType Directory `
            -Path $targetDirectory `
            -Force |
            Out-Null

        Copy-Item `
            -LiteralPath $file `
            -Destination $target
    }

    Compress-Archive `
        -Path (Join-Path $temp "*") `
        -DestinationPath $archive `
        -Force

    Write-Host "Created $archive with $($files.Count) files."
}
finally {
    if (Test-Path $temp) {
        Remove-Item -LiteralPath $temp -Recurse -Force
    }
}
# HamRadio-Pi Ultimate - Safe GitHub Sync
# Handles "fetch first" without force-pushing.

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=============================================="
Write-Host " HamRadio-Pi Ultimate - Safe GitHub Sync"
Write-Host "=============================================="
Write-Host ""

if (-not (Test-Path ".git")) {
    Write-Host "ERROR: This folder is not a Git repository."
    exit 1
}

$branch = git branch --show-current
if (-not $branch) {
    Write-Host "ERROR: Git is in detached HEAD mode."
    exit 1
}

Write-Host "Current branch: $branch"
Write-Host ""

$status = git status --porcelain
$stashCreated = $false

if ($status) {
    Write-Host "Local changes or untracked files were found."
    Write-Host "They will be stored temporarily before syncing."
    Write-Host ""

    git stash push -u -m "HamRadio-Pi automatic sync stash"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Git could not create the temporary stash."
        exit 1
    }

    $stashCreated = $true
}

Write-Host "Fetching GitHub..."
git fetch origin

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Git fetch failed."
    exit 1
}

Write-Host "Rebasing local commits onto origin/$branch..."
git pull --rebase origin $branch

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "The rebase stopped because a conflict needs attention."
    Write-Host "Run: git status"
    Write-Host "Do not use git push --force."
    exit 1
}

Write-Host "Pushing local commits..."
git push origin $branch

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Push failed. Run this script again after checking git status."
    exit 1
}

if ($stashCreated) {
    Write-Host "Restoring temporarily stored files..."
    git stash pop

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "The push succeeded, but the saved local files need manual attention."
        Write-Host "Run: git status"
        exit 1
    }
}

Write-Host ""
Write-Host "GitHub sync completed successfully."
Write-Host ""
git status

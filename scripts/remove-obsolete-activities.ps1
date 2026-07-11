# Remove obsolete duplicate activity files from the local project.
# These files are no longer launched by the dashboard.

$obsoleteFiles = @(
    "src/activity_browser.py",
    "src/data/activities.json"
)

foreach ($file in $obsoleteFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "Removed obsolete file: $file"
    }
}

Write-Host ""
Write-Host "Cleanup complete."
Write-Host "Run: git add -A"

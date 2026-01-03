# Install build tools if missing
py -3.13 -m pip install --upgrade build twine

# Remove old builds
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Build the package
py -3.13 -m build

# Upload to PyPI
if ($?) {
    Write-Host "Build successful. Uploading..." -ForegroundColor Green
    py -3.13 -m twine upload dist/*
} else {
    Write-Host "Build failed." -ForegroundColor Red
}

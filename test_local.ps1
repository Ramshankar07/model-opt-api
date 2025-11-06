# Test script for local setup
Write-Host "Testing Federated API Local Setup..." -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH
$env:PYTHONPATH = "src"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Test import
Write-Host "Step 1: Testing imports..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, 'src'); from federated_api.main import app; print('✅ Imports successful!')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Import failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Starting server in background..." -ForegroundColor Yellow
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Health: http://localhost:8000/health" -ForegroundColor Green
Write-Host "Sample tree: http://localhost:8000/api/v1/trees/sample" -ForegroundColor Green
Write-Host ""
Write-Host "To stop the server, press Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Start server
python run_local.py


# Start Real Estate Listings Web Application

$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

# Check if venv exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    Write-Host ""
    Write-Host "Installing dependencies..."
    & "venv\Scripts\Activate.ps1"
    python -m pip install --quiet --only-binary :all: fastapi uvicorn pydantic
} else {
    & "venv\Scripts\Activate.ps1"
}

Write-Host ""
Write-Host "Starting application..."
Write-Host ""
Write-Host "============================================"
Write-Host "Immobilien Suche - Real Estate Listings App"
Write-Host "============================================"
Write-Host ""
Write-Host "Opening application in browser..."
Write-Host "If browser doesn't open, visit: http://localhost:8000"
Write-Host "API Documentation: http://localhost:8000/docs"
Write-Host ""
Write-Host "Press Ctrl+C to stop the application"
Write-Host ""

Start-Sleep -Seconds 2
Start-Process "http://localhost:8000"

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

Read-Host "Press Enter to exit"

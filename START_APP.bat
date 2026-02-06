@echo off
REM Start Real Estate Listings Web Application

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    python -m pip install --quiet --only-binary :all: fastapi uvicorn pydantic
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Starting application...
echo.
echo ============================================
echo Immobilien Suche - Real Estate Listings App
echo ============================================
echo.
echo Opening application in browser...
echo If browser doesn't open, visit: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the application
echo.

timeout /t 2 /nobreak
start http://localhost:8000

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause

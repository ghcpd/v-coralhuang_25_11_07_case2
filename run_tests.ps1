# PowerShell test runner script for Flask SearchableMixin tests
# Usage: .\run_tests.ps1

param(
    [switch]$Coverage = $false,
    [switch]$Verbose = $false
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Flask SearchableMixin Test Runner" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommandPath
if (-not $scriptDir) { $scriptDir = '.' }

Push-Location $scriptDir

try {
    # Check if venv exists
    if (-not (Test-Path '.venv')) {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment"
            exit 1
        }
    }

    # Activate venv
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to activate virtual environment"
        exit 1
    }

    # Install dependencies
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install flask flask-sqlalchemy pytest -q
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies"
        exit 1
    }

    # Run tests
    Write-Host ""
    Write-Host "Running tests..." -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""

    if ($Coverage) {
        Write-Host "Installing coverage tools..." -ForegroundColor Yellow
        pip install pytest-cov -q
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install coverage tools"
            exit 1
        }
        
        Write-Host "Running tests with coverage..." -ForegroundColor Cyan
        pytest test_search_empty.py -v --cov=models --cov-report=term-missing
    } elseif ($Verbose) {
        pytest test_search_empty.py -v --tb=short
    } else {
        pytest test_search_empty.py -v --tb=line
    }

    $testExitCode = $LASTEXITCODE

    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    
    if ($testExitCode -eq 0) {
        Write-Host "✓ All tests passed!" -ForegroundColor Green
    } else {
        Write-Host "✗ Tests failed with exit code: $testExitCode" -ForegroundColor Red
    }
    
    Write-Host "================================================" -ForegroundColor Cyan

    exit $testExitCode

} finally {
    Pop-Location
}

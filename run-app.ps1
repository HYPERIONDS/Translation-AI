<#
.SYNOPSIS
    Single-command runner for Bhasha-AI (backend + frontend) on Windows PowerShell.

.DESCRIPTION
    This script will:
      - create a Python virtual environment (venv) if missing
      - install Python dependencies from requirements.txt (unless --NoInstall)
      - install frontend node_modules if missing
      - load environment variables from a `.env` file in project root
      - start the Flask backend using the venv Python
      - start the frontend (Vite) using npm
      - wait for both processes and perform a backend health check

.USAGE
    Open PowerShell, navigate to the project root and run:
        .\run-app.ps1

    Optional switches:
        -SkipFrontend   : only start backend
        -SkipBackend    : only start frontend
        -NoInstall      : don't create venv or run pip/npm install

    If .env does not exist, the script will create `.env` from `.env.template` and exit so
    you can fill in your API keys (ELEVENLABS_API_KEY, GEMINI_API_KEY, JWT_SECRET_KEY).
#>

param(
    [switch] $SkipFrontend,
    [switch] $SkipBackend,
    [switch] $NoInstall
)

# Ensure script runs from project root
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $ScriptPath

Write-Host "[run-app] Project root: $ScriptPath"

# Paths
$VenvDir = Join-Path $ScriptPath 'venv'
$PythonExe = Join-Path $VenvDir 'Scripts\python.exe'
$Requirements = Join-Path $ScriptPath 'requirements.txt'
$FrontendDir = Join-Path $ScriptPath 'frontend'
$EnvFile = Join-Path $ScriptPath '.env'
$EnvTemplate = Join-Path $ScriptPath '.env.template'

function Create-EnvFromTemplate {
    if (Test-Path $EnvTemplate) {
        Copy-Item -Path $EnvTemplate -Destination $EnvFile -Force
        Write-Host "[run-app] Created '.env' from '.env.template' at: $EnvFile"
    } else {
        "ELEVENLABS_API_KEY=your_elevenlabs_api_key_here" | Out-File -FilePath $EnvFile -Encoding utf8
        "GEMINI_API_KEY=your_gemini_api_key_here" | Out-File -FilePath $EnvFile -Append -Encoding utf8
        "JWT_SECRET_KEY=change_this_to_a_random_value" | Out-File -FilePath $EnvFile -Append -Encoding utf8
        Write-Host "[run-app] Created sample '.env' at: $EnvFile"
    }
    Write-Host "[run-app] Please open $EnvFile, add your real API keys, then re-run this script." -ForegroundColor Yellow
}

if (-not (Test-Path $EnvFile)) {
    Create-EnvFromTemplate
    exit 0
}

# Load .env into environment variables for the current process
Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith('#')) {
        $parts = $line -split '=',2
        if ($parts.Length -eq 2) {
            $name = $parts[0].Trim()
            $value = $parts[1].Trim().Trim("'", '"')
            Set-Item -Path Env:\$name -Value $value
        }
    }
}

if (-not $NoInstall) {
    # Create venv if missing and install Python deps
    if (-not (Test-Path $PythonExe)) {
        Write-Host "[run-app] Creating Python virtual environment..."
        python -m venv $VenvDir
        if (-not (Test-Path $PythonExe)) {
            Write-Error "[run-app] Failed to create venv. Ensure 'python' is on PATH and points to Python 3.11+."
            exit 1
        }
        & $PythonExe -m pip install --upgrade pip
        if (Test-Path $Requirements) {
            Write-Host "[run-app] Installing Python dependencies from requirements.txt (this may take a while)..."
            & $PythonExe -m pip install -r $Requirements
        }
    } else {
        Write-Host "[run-app] venv already exists. Skipping venv creation. Use -NoInstall to skip installs."
    }
}

# Ensure frontend dependencies
if (-not $SkipFrontend -and -not $NoInstall) {
    if (-not (Test-Path (Join-Path $FrontendDir 'node_modules'))) {
        if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
            Write-Error "[run-app] 'npm' not found on PATH. Install Node.js (v18+) and re-run."
            exit 1
        }
        Write-Host "[run-app] Installing frontend node modules..."
        Push-Location $FrontendDir
        npm install
        Pop-Location
    } else {
        Write-Host "[run-app] frontend node_modules exists. Skipping npm install."
    }
}

$processIds = @()

try {
    if (-not $SkipBackend) {
        if (-not (Test-Path $PythonExe)) {
            Write-Error "[run-app] Python executable not found at $PythonExe. Use -NoInstall to skip installation checks or create venv manually."
            exit 1
        }
        Write-Host "[run-app] Starting backend (Flask) using: $PythonExe backend.py"
        $backendProc = Start-Process -FilePath $PythonExe -ArgumentList 'backend.py' -WorkingDirectory $ScriptPath -PassThru
        $processIds += $backendProc.Id
    }

    if (-not $SkipFrontend) {
        if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
            Write-Error "[run-app] 'npm' not found on PATH. Install Node.js (v18+) and re-run."
            # do not exit here if backend was started
        } else {
            Write-Host "[run-app] Starting frontend (Vite) in: $FrontendDir"
            # Start npm as a process; pass args as array so quoting works robustly
            $npmArgs = @('run','dev','--','--host','0.0.0.0','--port','5000')
            $frontendProc = Start-Process -FilePath 'npm' -ArgumentList $npmArgs -WorkingDirectory $FrontendDir -PassThru
            $processIds += $frontendProc.Id
        }
    }

    # Wait for backend health endpoint (timeout ~60s)
    if (-not $SkipBackend) {
        $healthUrl = 'http://localhost:5001/api/health'
        Write-Host "[run-app] Waiting for backend health at $healthUrl"
        $ok = $false
        for ($i=0; $i -lt 60; $i++) {
            try {
                $resp = Invoke-RestMethod -Uri $healthUrl -Method GET -ErrorAction Stop
                Write-Host "[run-app] Backend healthy:" (ConvertTo-Json $resp -Depth 3)
                $ok = $true
                break
            } catch {
                Start-Sleep -Seconds 1
            }
        }
        if (-not $ok) {
            Write-Host "[run-app] Warning: backend did not report healthy within timeout. Check backend logs in its console window." -ForegroundColor Yellow
        }
    }

    Write-Host "[run-app] Application started. Frontend: http://localhost:5000  Backend: http://localhost:5001/api/health"
    Write-Host "[run-app] Press Ctrl+C in this console to stop both processes." -ForegroundColor Cyan

    if ($processIds.Count -gt 0) {
        Wait-Process -Id $processIds
    } else {
        Write-Host "[run-app] No processes were started. Exiting."
    }
} catch {
    Write-Error "[run-app] Error while launching: $_"
    if ($processIds.Count -gt 0) { Wait-Process -Id $processIds }
    exit 1
} finally {
    Write-Host "[run-app] Exited."
}

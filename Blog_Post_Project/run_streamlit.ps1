#!/usr/bin/env pwsh
# ============================================================================
# Research Paper Blog Post Generator - Quick Start Script (PowerShell)
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                        ║" -ForegroundColor Cyan
Write-Host "║     📰 Research Paper Blog Post Generator - Quick Start               ║" -ForegroundColor Cyan
Write-Host "║                                                                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if Streamlit is installed
$streamlitCheck = pip show streamlit 2>$null
if ($null -eq $streamlitCheck) {
    Write-Host "📦 Installing Streamlit..." -ForegroundColor Yellow
    pip install streamlit
    Write-Host ""
}

# Check if required packages are installed
$langgraphCheck = pip show langgraph 2>$null
if ($null -eq $langgraphCheck) {
    Write-Host "📦 Installing required packages from requirements.txt..." -ForegroundColor Yellow
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
    }
    Write-Host ""
}

Write-Host ""
Write-Host "✨ Starting Streamlit application..." -ForegroundColor Green
Write-Host ""
Write-Host "🌐 The app will open in your browser at: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   - Use ArXiv ID for faster processing (e.g., 2005.11401)" -ForegroundColor Gray
Write-Host "   - Start with 5-10 iterations for testing" -ForegroundColor Gray
Write-Host "   - Check your .env file for API keys" -ForegroundColor Gray
Write-Host "   - Press CTRL+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Launch Streamlit
try {
    streamlit run BlogStreamApp.py --logger.level=info
}
catch {
    Write-Host ""
    Write-Host "❌ Error running Streamlit" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try these troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Ensure you're in the Blog_Post_Project directory" -ForegroundColor Gray
    Write-Host "2. Check that .env file exists with API keys" -ForegroundColor Gray
    Write-Host "3. Run: pip install --upgrade streamlit" -ForegroundColor Gray
    Write-Host "4. Try a different port: streamlit run BlogStreamApp.py --server.port 8502" -ForegroundColor Gray
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

@echo off
REM ============================================================================
REM Research Paper Blog Post Generator - Quick Start Script
REM ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                                                                        ║
echo ║     📰 Research Paper Blog Post Generator - Quick Start               ║
echo ║                                                                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Check if Streamlit is installed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Streamlit...
    pip install streamlit
    echo.
)

REM Check if required packages are installed
pip show langgraph >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required packages...
    pip install -r requirements.txt
    echo.
)

echo.
echo ✨ Starting Streamlit application...
echo.
echo 🌐 The app will open in your browser at: http://localhost:8501
echo.
echo 💡 Tips:
echo    - Use ArXiv ID for faster processing (e.g., 2005.11401)
echo    - Start with 5-10 iterations for testing
echo    - Check your .env file for API keys
echo.
echo Press CTRL+C to stop the server
echo.

REM Launch Streamlit
streamlit run BlogStreamApp.py --logger.level=info

if errorlevel 1 (
    echo.
    echo ❌ Error running Streamlit
    echo.
    echo Try these troubleshooting steps:
    echo 1. Ensure you're in the Blog_Post_Project directory
    echo 2. Check that .env file exists with API keys
    echo 3. Run: pip install --upgrade streamlit
    echo 4. Try a different port: streamlit run BlogStreamApp.py --server.port 8502
    echo.
    pause
)

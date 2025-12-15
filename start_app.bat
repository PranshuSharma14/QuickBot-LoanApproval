@echo off
echo 🚀 Starting QuickLoan - Agentic AI Loan Sales Assistant
echo ================================================

echo.
echo 📦 Starting Backend Server...
start "Backend" cmd /c "cd /d C:\Users\PranshuSharma\Desktop\NBFC && .\.venv\Scripts\python.exe main.py"

echo.
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo 🎨 Starting Frontend Development Server...
start "Frontend" cmd /c "cd /d C:\Users\PranshuSharma\Desktop\NBFC\frontend && npm run dev"

echo.
echo ✅ Both servers are starting!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://127.0.0.1:8000
echo 📚 API Docs: http://127.0.0.1:8000/docs
echo.
echo Press any key to exit this window...
pause > nul
@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -m venv .venv
)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist "data\hyderabad_air_quality.csv" (
  python fetch_data.py
  if errorlevel 1 (
    echo.
    echo Data download did not complete. Check your OpenAQ API key and internet connection.
    pause
    exit /b 1
  )
)
streamlit run app.py
pause

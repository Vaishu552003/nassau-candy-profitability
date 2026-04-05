@echo off
cd /d "%~dp0"
echo Installing dependencies (if needed)...
py -3 -m pip install -r requirements.txt -q
echo Starting Streamlit at http://localhost:8501 ...
py -3 -m streamlit run app.py --server.headless false
pause

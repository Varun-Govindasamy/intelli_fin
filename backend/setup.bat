@echo off
echo Setting up IntelliFinance Backend...

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Creating data directories...
mkdir data\uploads 2>nul
mkdir data\vector_store 2>nul

echo.
echo Copying environment file...
copy .env.example .env

echo.
echo ========================================
echo Backend setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Install Ollama and pull a model (optional)
echo 3. Run: python main.py
echo ========================================
pause

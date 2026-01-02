@echo off
cd /d D:\marginplus_mvp

echo Starting MarginPlus MVP via python -m uvicorn...
echo.

python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload

echo.
echo (Press any key to close)
pause

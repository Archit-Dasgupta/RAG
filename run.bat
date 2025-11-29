@echo off
echo Starting Personal RAG Model...
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8080
pause

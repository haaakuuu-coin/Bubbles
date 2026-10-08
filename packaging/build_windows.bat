@echo off
REM 1) pip install -r requirements.txt pyinstaller   2) este script   3) compilar installer.iss con Inno Setup
cd /d "%~dp0.."
pyinstaller --noconfirm packaging\tts-chatbot.spec

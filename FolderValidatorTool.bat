@ECHO OFF
set CWD=%~dp0
::for /f "delims=" %%p in ('where python') do SET PYTHONPATH=%%p
set PYTHONPATH="C:\Program Files\Python310\python.exe"
set PYTHON_FILE=%CWD%ValidatorTool.py

set BASEDIR=%CWD%someFolder
set JSON_PATH=%CWD%Config.json
set PYTHON_FILE=%CWD%ValidatorTool.py
set VENDOR=Rad
echo %PYTHONPATH% %PYTHON_FILE%
%PYTHONPATH% %PYTHON_FILE%
::cmd /k
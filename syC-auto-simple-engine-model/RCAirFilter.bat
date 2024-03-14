REM
REM Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
REM
@ECHO OFF
SETLOCAL

REM Get SyC root from location of ScdtServer.bat
set SCDTSERVERBATROOT=%~dp0
if not defined SYSC_ROOT set SYSC_ROOT=%SCDTSERVERBATROOT%..\..

if "%SYSC_DEPENDENCIES%" == "" if exist "%SYSC_ROOT%\..\Core_Dependencies" set SYSC_DEPENDENCIES=%SYSC_ROOT%\..\Core_Dependencies

set PY3VER=3_10
if "%SYSC_PY_VERSION%"=="" (
   set SYSC_PY_VERSION=%PY3VER%
)

REM Get SyC python path
if exist "%SYSC_DEPENDENCIES%\CPython\%SYSC_PY_VERSION%\winx64\Release\python" (
  set SYSC_PYTHON=%SYSC_DEPENDENCIES%\CPython\%SYSC_PY_VERSION%\winx64\Release\python
) else if exist "%SYSC_ROOT%\CPython\%SYSC_PY_VERSION%\winx64\Release\python" (
  set SYSC_PYTHON=%SYSC_ROOT%\CPython\%SYSC_PY_VERSION%\winx64\Release\python
) else if exist "%SYSC_ROOT%\..\commonfiles\CPython\%SYSC_PY_VERSION%\winx64\Release\python" (
  set SYSC_PYTHON=%SYSC_ROOT%\..\commonfiles\CPython\%SYSC_PY_VERSION%\winx64\Release\python
) else (
  echo "Could not find CPython.."
  exit /B 1
)

if not defined SYSC_VERSION set SYSC_VERSION="2024 R1"

if "%SYSC_PARTLIB_BUILDNAME%" == "" (set BINDIRNAME=bin) else (set BINDIRNAME=bin_%SYSC_PARTLIB_BUILDNAME%)

set PYTHON_DLL_PATH=%SYSC_ROOT%\runTime\winx64\%BINDIRNAME%\compiler;%PYTHON_DLL_PATH%
set PYTHON_DLL_PATH=%SYSC_ROOT%\runTime\winx64\%BINDIRNAME%;%PYTHON_DLL_PATH%
set PYTHON_DLL_PATH=%SYSC_ROOT%\runTime\winx64\cnlauncher\fluent\fluent24.2.0\multiport\mpi_wrapper\win64\stub;%PYTHON_DLL_PATH%

set PYTHONPATH=%SYSC_ROOT%\runTime\winx64\%BINDIRNAME%;%PYTHONPATH%

"%SYSC_PYTHON%\python.exe" -B "RCAirFilter.py" %*
exit /B %errorlevel%
@ECHO OFF

pushd %~dp0

if "%1" == "" goto help
goto %1

:help
echo.Try one of the following targets as 'make ^<target^>':
echo.server clean
echo.'server' requires 'nuitka' to be installed in the active python environment.
goto end

:install
npm install
goto end

:server
python -m nuitka .\json_server.py --output-dir=.\build --standalone --follow-imports --show-progress
MOVE .\build\json_server.dist .\dist\json_server
goto end

:clean
DEL /F/Q/S .\build > NUL
RMDIR /Q/S .\build
MKDIR .\build
DEL /F/Q/S .\dist > NUL
RMDIR /Q/S .\dist
MKDIR .\dist
goto end

:debug
./dist/json_server/json_server --tcp --port=2087
goto end

:debug-py
python ./json_server.py --tcp --port=2087
goto end

:end
popd

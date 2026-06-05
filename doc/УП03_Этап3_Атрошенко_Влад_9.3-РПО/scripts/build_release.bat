@echo off
chcp 65001 > nul
cd /d "%~dp0\.."

echo ========================================
echo  СБОРКА RELEASE АРХИВА
echo ========================================

set RELEASE_DIR=release\project_release
set RELEASE_DATE=%date:~6,4%-%date:~3,2%-%date:~0,2%

echo Создание папки release...
if not exist "release" mkdir release
if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"

echo Копирование файлов...
mkdir "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%\backend"
mkdir "%RELEASE_DIR%\frontend"

xcopy /e /i backend\app "%RELEASE_DIR%\backend\app"
xcopy /e /i backend\tests "%RELEASE_DIR%\backend\tests"
copy backend\requirements.txt "%RELEASE_DIR%\backend\"
xcopy /e /i frontend\web "%RELEASE_DIR%\frontend\web"

echo Создание README для релиза...
copy README.md "%RELEASE_DIR%\"
echo Дата сборки: %RELEASE_DATE% > "%RELEASE_DIR%\build_info.txt"
echo Версия: 1.0.0 >> "%RELEASE_DIR%\build_info.txt"
echo Адрес сервера: http://80.78.247.163 >> "%RELEASE_DIR%\build_info.txt"

echo Создание ZIP архива...
cd release
powershell -Command "Compress-Archive -Path project_release -DestinationPath project_release.zip -Force"
cd ..

echo.
echo ========================================
echo  РЕЛИЗ СОБРАН!
echo  Архив: release\project_release.zip
echo ========================================
pause
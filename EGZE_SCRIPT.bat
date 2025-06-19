@echo off
REM Skrypt do budowania PianoTiles.exe przy użyciu PyInstaller

REM Opcjonalnie: Przejdź do folderu, w którym znajduje się ten skrypt .bat
REM cd /d "%~dp0"

echo Sprawdzanie i instalacja/aktualizacja PyInstaller...
pip install --upgrade pyinstaller

echo.
echo Rozpoczynanie budowania PianoTiles.exe...
echo Komenda: pyinstaller --name "PianoTiles" --onefile --windowed main.py

pyinstaller --name "PianoTiles" --onefile --windowed main.py

echo.

IF ERRORLEVEL 1 (
    echo Blad podczas budowania PianoTiles.exe!
    pause
    exit /b 1
)

echo Pomyslnie zbudowano PianoTiles.exe.
echo Plik wykonywalny znajduje sie w podfolderze 'dist'.

REM Opcjonalne czyszczenie:
REM echo.
REM echo Czyszczenie folderow tymczasowych...
REM IF EXIST "build" (
REM     echo Usuwanie folderu 'build'...
REM     rmdir /s /q build
REM )
REM IF EXIST "*.spec" (
REM     echo Usuwanie plikow .spec...
REM     del *.spec
REM )

echo.
echo Zakonczono.
pause

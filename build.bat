@echo off
echo ==========================================
echo      INICIANDO O BUILD DO PYPOS (COM ICONE)
echo ==========================================
echo.

echo 1. Ativando o Ambiente Virtual...
call .venv\Scripts\activate

echo.
echo 2. Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo.
echo 3. Gerando executavel...
:: AQUI ESTA A MUDANCA: --icon="icone.ico"
pyinstaller --name "PyPOS_Enterprise" --icon="icone.ico" --noconsole --onefile --recursive-copy-metadata=sqlalchemy src/views/main_view.py

echo.
echo ==========================================
echo      BUILD FINALIZADO COM SUCESSO!
echo ==========================================
echo O arquivo esta na pasta 'dist'
pause
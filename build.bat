@echo off
echo Packaging application...
pyinstaller index.spec
echo Packaging complete. Check the dist folder.
pause

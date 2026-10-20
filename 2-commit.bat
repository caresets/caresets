@echo off
rem 2-commit.bat - commit everything in this clone and push it to GitHub.
rem
rem   2-commit.bat                      asks for a commit message
rem   2-commit.bat glossary: new terms  uses the rest of the line as the message
rem
rem The push to main is built by GitHub and published as the development
rem version at https://caresets.github.io/caresets/dev/ . The published
rem version changes only with a release tag - see "When you cut a release"
rem in README.md.
setlocal EnableDelayedExpansion
cd /d "%~dp0"

git add -A
git diff --cached --quiet
if not errorlevel 1 (
  echo Nothing to commit - the working tree matches the last commit.
  goto push
)

set "MSG=%*"
if "%MSG%"=="" (
  echo.
  git status --short
  echo.
  set /p "MSG=Commit message: "
)
if "!MSG!"=="" (
  echo No message given - nothing committed.
  exit /b 1
)

git commit -m "!MSG!"
if errorlevel 1 (
  echo Commit FAILED.
  exit /b 1
)

:push
git push
if errorlevel 1 (
  echo.
  echo Push FAILED. If GitHub has newer commits, run:  git pull --rebase  then  git push
  exit /b 1
)
echo.
echo Pushed. In a few minutes it is at https://caresets.github.io/caresets/dev/
endlocal

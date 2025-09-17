@echo off
@REM git fetch
@REM git pull
git reset --mixed @{u}
git add *
git commit -m push
git push origin main
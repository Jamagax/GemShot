@echo off
title GemShot Launcher
color 0B
mode con: cols=50 lines=20

:: --- GEM ANIMATION START ---
for /l %%x in (1, 1, 5) do (
    cls
    echo.
    echo.
    echo.
    if %%x==1 (
        echo                     /\
        echo                    /  \
        echo                    \  /
        echo                     \/
        echo.
        echo                 [ O . . . ]
    )
    if %%x==2 (
        echo                     /\  *
        echo                    /  \
        echo                    \  /
        echo                     \/
        echo.
        echo                 [ . O . . ]
    )
    if %%x==3 (
        echo                     /\
        echo                    /  \
        echo                    \  /
        echo                     \/
        echo.
        echo                 [ . . O . ]
    )
    if %%x==4 (
        echo                  *  /\
        echo                    /  \
        echo                    \  /
        echo                     \/
        echo.
        echo                 [ . . . O ]
    )
    if %%x==5 (
        echo                     /\
        echo                    /  \  *
        echo                    \  /
        echo                     \/
        echo.
        echo                 [ OK! ]
    )
    echo.
    echo            Loading - GemShot - LifeOS
    echo.
    echo               Developed by Jamagax
    timeout /t 1 >nul
)
:: --- GEM ANIMATION END ---

cls
color 07
mode con: cols=80 lines=30
echo ===================================================
echo   GEMSHOT ULTIMATE - Starting...
echo ===================================================
echo.

:: Simple start using system Python (since it was working before)
python "main.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application crashed.
    echo If this persists, run 'Install Dependencies.bat'
    pause
)

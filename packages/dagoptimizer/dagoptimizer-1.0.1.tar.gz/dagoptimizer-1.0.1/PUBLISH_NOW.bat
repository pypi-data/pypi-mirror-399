@echo off
echo ================================================================================
echo   PUBLISHING DAGOPTIMIZER TO PYPI
echo ================================================================================
echo.
echo Your package is ready to publish!
echo.
echo When prompted, enter:
echo   Username: __token__
echo   Password: [Paste your PyPI API token]
echo.
echo The token you copied earlier starts with: pypi-AgEI...
echo.
echo ================================================================================
echo.
pause
echo.
echo Starting upload...
echo.

python -m twine upload dist/*

echo.
echo ================================================================================
if %ERRORLEVEL% EQU 0 (
    echo   SUCCESS! PACKAGE PUBLISHED!
    echo ================================================================================
    echo.
    echo Your package is now LIVE on PyPI!
    echo.
    echo Anyone can now install it with:
    echo   pip install dagoptimizer
    echo.
    echo View your package at:
    echo   https://pypi.org/project/dagoptimizer/
    echo.
    echo Tell your friends to try:
    echo   pip install dagoptimizer
    echo.
) else (
    echo   UPLOAD FAILED
    echo ================================================================================
    echo.
    echo Common issues:
    echo   - Wrong token format (must start with pypi-)
    echo   - Username must be exactly: __token__
    echo   - Network connection issue
    echo.
    echo Try again or check PUBLISHING_GUIDE.md
    echo.
)
pause


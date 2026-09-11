@echo off
echo ========================================
echo   KINESIS AI - Firewall Configuration
echo ========================================
echo.

echo Configuring Windows Firewall for team access...
echo.

REM Allow inbound traffic on port 5000
netsh advfirewall firewall add rule name="Kinesis AI Server" dir=in action=allow protocol=TCP localport=5000

if %errorlevel% equ 0 (
    echo [OK] Firewall rule added successfully
    echo [INFO] Port 5000 is now open for team access
) else (
    echo [ERROR] Failed to add firewall rule
    echo [INFO] You may need to run this as Administrator
)

echo.
echo ========================================
echo   Firewall Configuration Complete
echo ========================================
echo.
echo Team members can now access the application using:
echo http://172.16.182.227:5000
echo.
pause

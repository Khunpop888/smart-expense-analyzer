@echo off
chcp 65001 >nul
echo ============================================================
echo   Smart Expense Analyzer - Push to GitHub
echo   Repository: https://github.com/Khunpop888/smart-expense-analyzer
echo ============================================================
echo.

set GIT_EXE="C:\Users\napon.su\AppData\Local\GitHubDesktop\app-3.6.5\resources\app\git\cmd\git.exe"

cd /d "C:\Users\napon.su\Desktop\Smart_Expense_Analyzer"
%GIT_EXE% add .
%GIT_EXE% commit -m "update: mobile UX/UI, statements dataset and formatting"
%GIT_EXE% push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] อัปโหลดขึ้น GitHub เรียบร้อยแล้ว!
    echo เข้าชมผ่านเว็บมือถือได้ที่: https://Khunpop888.github.io/smart-expense-analyzer/
) else (
    echo.
    echo [NOTICE] หากยังไม่ได้สร้าง Repository บน GitHub
    echo ให้ไปที่ https://github.com/new แล้วตั้งชื่อ "smart-expense-analyzer"
    echo หรือเปิดโปรแกรม GitHub Desktop แล้วกด "Publish repository" ได้เลยครับ
)

echo.
pause

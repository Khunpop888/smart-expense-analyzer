@echo off
chcp 65001 >nul
title Smart Expense Analyzer - Shopee Screenshot Scanner
echo กำลังเริ่มต้นระบบสแกนภาพแคปหน้าจอ Shopee...
python "%~dp0scan_shopee_folder.py"

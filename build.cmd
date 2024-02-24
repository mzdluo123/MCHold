@echo off
python -m nuitka --follow-imports --windows-uac-admin --enable-plugin=tk-inter --standalone gui.py
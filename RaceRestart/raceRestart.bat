@echo off
set /p fileName="Enter file name (e.g. 201102_R.json): "
python raceRestart.py %fileName%
PAUSE
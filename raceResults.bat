@echo off
set /p fileName="Enter file name (e.g. results.json): "
python raceResults.py %fileName%
PAUSE
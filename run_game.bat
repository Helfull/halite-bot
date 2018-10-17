@ECHO off
rm -rf replays
mkdir replays
halite.exe --results-as-json -s 1539809485 --replay-directory replays/ -vvv --width 64 --height 64 "python MyBot.py" "python MyBot.py" "python MyBot.py" "python MyBot.py" > result.json
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"

set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%"
set "Min=%dt:~10,2%"
set "Sec=%dt:~12,2%"

set "fullstamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"
mv result.json "results/result-%fullstamp%.json"
mv replays/* "results/replays/"

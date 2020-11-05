# RaceRestart

This python script can force a starting grid based on the qualifying session or based on an aborted race. This is intendet to be used for red-flag situations in ACC

The script will force car and names of the previous session.


## Requirements
In the `settings.json` of the server, the property `"dumpLeaderboards": 1` must be set.
Furthermore the session must be ended before the logs can be accessed.
This can be achieved in two ways
* wait until the session is over
* join as admin and type `/next` in chat


## Usage
Run the script with your python interpreter (or execute the provided standalone `.exe`)
The script will try to search for the result file in the following order

1. `result` folder in current directory
2. `result` folder in default steam-folder
3. first `.json` files in current directory

If the file is in neither of those directory, or you want to use a specific file, you can specify the path as the 1st argument (relative or absolute) when starting the program.

---

When started and a `RaceResult.json` is used, the script asks you on which lap you want to base the starting grid. This is necessary as e.g. a timeout scenario would list an uncounted lap as the last lap of the race and therefore can't be used.


## Output

The output is saved into the file `entrylist.json` into the working directory. Any existing file will be overriden.

* Copy the file into your `cfg/` folder of the server
* remove the Qualifying session from the event (P->R)
* start the server

Skipping the qualifying instead of removing it is only possible if no car on the grid sets a valid lap.
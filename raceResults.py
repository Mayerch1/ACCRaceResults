import sys
import os
import json

from datetime import timedelta

point_scale = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]


class Driver:
    total_laps = 0
    finished_tm = 0
    place = -1
    name = ''
    fastest_lap = None


def millis_to_laptime(millis: int):

    td = timedelta(milliseconds=millis)

    secs = td.seconds
    mins = int(secs/60) # get full minutes
    secs -= (mins*60) # subtract the minutes from seconds
    secs += td.microseconds/1_000_000 # add ms

    
    output = '{:d}:{:06.3f}'.format(mins, secs)
    return output



def map_drivers(json_laps):
    drivers = {}

    # overwriting the 'old' laps of each driver with more recent ones
    for lap in json_laps:
        id = lap['carId']

        # create new driver and grab constants
        if not id in drivers:
            drivers[id] = Driver()
            drivers[id].name = lap['driver']

        # check for fastest lap
        new_fastest = lap['lapTime']
        if drivers[id].fastest_lap is None or new_fastest < drivers[id].fastest_lap:
            drivers[id].fastest_lap = new_fastest


        # update all values which should have the most recent state (of last lap)
        if drivers[id].total_laps < lap['lapNumber']:
            drivers[id].total_laps = lap['lapNumber']
            drivers[id].place = lap['position']
            drivers[id].finished_tm = lap['lapCompletedTimestamp']


    return drivers




def main(json_file):

    if not os.path.exists(json_file):
        print('Cannot find any file named ' + json_file)
        if not json_file.endswith('.json'):
            print('Did you perhaps forgot to specify the ending (.json)?')
        return

    # load the result file from the disc
    with open (json_file, 'r') as json_raw:
        json_str = ' '.join(json_raw.readlines())

    json_data = json.loads(json_str)



    # atm we only care about lap times
    laps = json_data.get('laps', None)



    if not laps:
        # this should never occur in a valid dataset
        return

    drivers = map_drivers(laps)

    driver_list = list(drivers.values())
    driver_list.sort(key=lambda d: d.place)


    race_over_time = driver_list[0].finished_tm


    fastest_lap = None
    fastest_driver = None


    print('Race results (driver must have completed at least 1 lap)')
    i = 0
    for d in driver_list:
        is_finished = d.finished_tm >= race_over_time

        if i < len(point_scale):
            points = point_scale[i]
        else:
            points = 0


        if is_finished:
            points += 1
            finished_str = '\t '
        else:
            finished_str = '(DNF)'


        # update fastest lap 
        if fastest_lap is None or d.fastest_lap < fastest_lap:
            fastest_lap = d.fastest_lap
            fastest_driver = d


        print('{:d}. {:s} - {:d} pts. - {:s}\t @ {:s}'.format(d.place, finished_str, points, d.name.ljust(30), millis_to_laptime(d.fastest_lap)))
        i += 1
        


    print('\nFastest lap')
    print('{:s} @ {:s}'.format(fastest_driver.name, millis_to_laptime(fastest_lap)))
    
    
    


if __name__ == '__main__':
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = 'result.json'

    main(json_file)
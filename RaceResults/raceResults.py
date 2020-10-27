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
    leading_laps = 0
    accident_cnt = 0
    pit_stop = 0

    is_finished = None


def millis_to_laptime(millis: int):

    td = timedelta(milliseconds=millis)

    secs = td.seconds
    mins = int(secs/60) # get full minutes
    secs -= (mins*60) # subtract the minutes from seconds
    secs += td.microseconds/1_000_000 # add ms

    output = '{:d}:{:06.3f}'.format(mins, secs)
    return output



def map_drivers(json_laps):
    # collecting data is easir with dict
    # as order is inconsistent over race
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

        if lap['position'] == 1:
            drivers[id].leading_laps += 1

        drivers[id].accident_cnt += lap['accidents']

        if lap['lapType'] == 1:
            drivers[id].pit_stop += 1
 

    # convert to list (as drivers are sorted by result, not by id)
    driver_list = list(drivers.values())
    driver_list.sort(key=lambda d: d.place)

    race_over_time = driver_list[0].finished_tm

    for d in driver_list:
        d.is_finished = d.finished_tm >= race_over_time

    # split up the drivers group, as finished drivers do not need further processing
    finished_drivers = list(filter(lambda d: d.is_finished, driver_list))
    dnf_drivers = list(filter(lambda d: not d.is_finished, driver_list))


    # all finished drivers are already sorted by position entry
    # 'position' field is invalid for dnf drivers
    # therefore sort dnf drivers by lapCount (and by finished_tm if lapCount is equal)

    # -total_laps achieves reversSort for first key and 'normal' sort for 2nd key
    dnf_drivers.sort(key=lambda d: (-d.total_laps, d.finished_tm))


    return finished_drivers + dnf_drivers




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

    fastest_lap = None
    fastest_driver = None


    print('\nRace results (driver must have completed at least 1 lap)')
    print('A leading lap is assigned to the driver who starts the next lap')
    print('Incidents are registered \'as reported by ACC\'')
    print('The Box field holds any registered drive through (DT, SG, Pitstop)\n')
    print('{: >15} | {:s} {:s} |  {:s} | {: <30} | {:s} | {:s} | {: >15}\n'.format('Position', '(Leading-)', 'Laps', 'Points', 'Driver', 'Incidents', 'Box', '@ Fastest Lap'))

    i = 0
    for d in drivers:

        if i < len(point_scale):
            points = point_scale[i]
        else:
            points = 0


        if d.is_finished:
            points += 1
            finished_str = ''
        else:
            finished_str = '(DNF)'


        # update fastest lap 
        if fastest_lap is None or d.fastest_lap < fastest_lap:
            fastest_lap = d.fastest_lap
            fastest_driver = d


        print('{:#7d}. {: >6} | {:#10d} /{:#3d} | {:#3d} pts | {: <30} | {:#9d} | {:#3d} | {: >15}'.format(i+1, finished_str, d.leading_laps, d.total_laps, points, d.name, d.accident_cnt, d.pit_stop, millis_to_laptime(d.fastest_lap)))
        i += 1
        


    print('\nFastest lap')
    print('{:s} @ {:s}'.format(fastest_driver.name, millis_to_laptime(fastest_lap)))

    print('\nClean Drivers (excludes DNFs)')
    print(', '.join([d.name for d in list(filter(lambda d: d.accident_cnt == 0 and d.is_finished, drivers))]))
    
    
    
    


if __name__ == '__main__':
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        print('Enter name of the result file (*.json): ')
        json_file = input()

    main(json_file)
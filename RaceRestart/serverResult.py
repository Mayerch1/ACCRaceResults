import json
from data import Event, Team, Driver


class Lap:
    def __init__(self):
        self.carId = 0
        self.driverIndex = 0
        self.lapTime = 0
        self.isValidForBest = False
        self.splits = []


class LapStanding:
    def __init__(self):
        self.drivers = []



def parse_race_abort(data, event: Event):
    """re-orders the starting grid in the event object based on the race standing
       function asks for user input to select the lap to use for standing

    Args:
        data ([type]): json dict of server dump
        event (Event): already parsed event

    Returns:
        [type]: corrected event object
    """

    laps = data['laps']

    if not laps:
        print('no complete lap registered, using starting grid')
        return event

    leading_car = event.teams[0]

    lap_list = []

    # make processing easier
    i = 0
    for lap in laps:
        l = Lap()
        l.carId = lap['carId']
        l.driverIndex = lap['driverIndex']
        l.lapTime = lap['laptime']
        l.isValidForBest = lap['isValidForBest']
        l.splits = lap['splits']

        lap_list.append(l)

    
    # count number of laps
    lap_cnt = len(list(filter(lambda l: l.carId == leading_car.carId, lap_list)))


    standing_list = []

    standing = LapStanding()
    for lap in lap_list:
        
        if lap.carId in standing.drivers:
            standing_list.append(standing)
            standing = LapStanding()
            
        standing.drivers.append(lap.carId)

    print('found {:d} completed laps'.format(lap_cnt))
    i = 1
    for l in standing_list:
        print('{:2d}. {:2d} drivers'.format(i, len(l.drivers)))
        i+=1


    print('\nselect the lap to base the grid on:')
    lap_select = input()

    if not lap_select.isdigit():
        print('enter an integer')
        return None

    lap_select = int(lap_select)
    if lap_select > lap_cnt or lap_select < 1:
        print('found only {:d} laps', lap_cnt)
        return None


    # take the selected lap and 
    lap_select -= 1 # 1 offset


    # resetting of all starting positions is required
    # as some drivers may quit before the selected lap
    for d in event.teams:
        d.defaultGridPosition = -1
    

    # set the starting position based on the selected lap
    grid_lap = standing_list[lap_select]

    i = 1
    for lap in grid_lap.drivers:
        # the first id in the list is the starter
        for d in event.teams:
            if d.carId == lap:
                d.defaultGridPosition = i
                i += 1
                break

    
    return event


def parse_data(json_data):
    """parse the json file into Event object
        * Qualy: starting grid is based on qualy
        * Race: starting grid is based on the selected lap

       the method may ask for user input

    Args:
        json_data ([type]): json dict of server dump

    Returns:
        [type]: Event Object
    """

    ev = Event()
    ev.name = json_data['trackName']

    leaders = json_data['sessionResult']['leaderBoardLines']

    i = 1
    for team_json in leaders:
        car = team_json['car']

        team = Team()
        team.defaultGridPosition = i
        team.forcedCarModel = car['carModel']
        team.raceNumber = car['raceNumber']
        team.carId = car['carId']
        
        for driver in car['drivers']:
            d = Driver()
            d.firstName = driver['firstName']
            d.lastName = driver['lastName']
            d.shortName = driver['shortName']
            d.playerID = driver['playerId']

            team.drivers.append(d)

        ev.teams.append(team)
        i += 1





    if json_data['sessionType'] == 'Q':
        print('detected Qualy session')
        return ev
    elif json_data['sessionType'] == 'R':
        print('detected Race session')
        return parse_race_abort(json_data, ev)
    else:
        print('unsupported session type, applying qualy procedure')
        return ev
        
        
    return ev

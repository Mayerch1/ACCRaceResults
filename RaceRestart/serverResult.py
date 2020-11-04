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



def set_lap_close_order(event, carId, place):
    for team in event.teams:
        if team.carId == carId:
            team.cross_line_order = place


def add_lap_to_team(event, carId: int):
    for team in event.teams:
        if team.carId == carId:
            team.lap_cnt += 1



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

    # hold 'raw' json data parsed to obj
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

    
 

   


    # hold one 'standing' for each lap in the race
    # each standing is a list of carId in order of crossing the finish line
    standing_list = []

    standing = LapStanding()
    for lap in lap_list:
        
        if lap.carId in standing.drivers:
            standing_list.append(standing)
            standing = LapStanding()
            
        standing.drivers.append(lap.carId)
        

    print('found {:d} completed laps'.format(len(standing_list)))
    i = 0
    for l in standing_list:
        print('{:2d}. {:2d} drivers'.format(i, len(l.drivers)))
        i+=1
    


    print('\nselect the lap to base the grid on:')
    lap_select = input()

    if not lap_select.isdigit():
        print('enter an integer')
        return None

    lap_select = int(lap_select)
    if lap_select > len(standing_list)-1 or lap_select < 0:
        print('found only {:d} laps. Be aware of 0-indexing'.format(len(standing_list)))
        return None


    # take the selected lap and 
    lap_select -= 1 # 1 offset


    # delete all 'deleted' data from event object aswell
    standing_list = standing_list[:lap_select+1]



    # add the lap counting for alldrivers
    # this is the primary sorting key
    for lap in standing_list:
        for carId in lap.drivers:
            add_lap_to_team(event, carId)



    # resetting of all starting positions is required
    # as some drivers may quit before the selected lap
    for d in event.teams:
        d.defaultGridPosition = -1
    

    # save order of crossing the finish line to team
    # this is the secondary sorting key
    i = 1
    grid_lap = standing_list[lap_select]
    for carId in grid_lap.drivers:
        set_lap_close_order(event, carId, i)
        i += 1


    event.teams.sort(key=lambda t: (-t.lap_cnt, t.cross_line_order))

    # iterate over all drivers to set the starting grid position
    i = 1
    for team in event.teams:
        if team.cross_line_order > 0:
            team.defaultGridPosition = i
            i += 1

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

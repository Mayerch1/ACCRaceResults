import json

class Driver:
    def __init__(self):
        self.firstName = ""
        self.lastName = ""
        self.shortName = ""
        self.driverCategory = 0
        self.playerID = ""


class Team:

    def __init__(self):
        self.drivers = []
        self.carId = 0 # used for internal processing
        self.raceNumber = -1
        self.defaultGridPosition = -1
        self.forcedCarModel = -1
        self.overrideDriverInfo = -1
        self.isServerAdmin = 0
        self.ballastKg = 0
        self.configVersion = 1
        self.lap_cnt = 0
        self.cross_line_order = -1


class Event(object):
    name = ""
    teams = []


def _driver_to_json(d: Driver):
    return dict({
        'firstName': d.firstName,
        'lastName': d.lastName,
        'shortName': d.shortName,
        'driverCategory': d.driverCategory,
        'playerID': d.playerID,
    })

def _json_to_driver(json):
    d = Driver()
    
    d.firstName = json['firstName']
    d.lastName = json['lastName']
    d.shortName = json['shortName']
    d.driverCategory = json['driverCategory']
    d.playerID = json['playerID']

    return d


def _team_to_json(t: Team):
    d =  dict({
        'raceNumber': t.raceNumber,
        'defaultGridPosition': t.defaultGridPosition,
        'forcedCarModel': t.forcedCarModel,
        'overrideDriverInfo': t.overrideDriverInfo,
        'isServerAdmin': t.isServerAdmin,
        'ballastKg': t.ballastKg,
        'configVersion': t.configVersion
    })

    # serialize list of drivers
    d['drivers'] = []
    for drv in t.drivers:
        d['drivers'].append(_driver_to_json(drv))

    return d



def _json_to_team(json):
    t = Team()

    t.raceNumber = int(json['raceNumber'])
    t.defaultGridPosition = int(json['defaultGridPosition'])
    t.forcedCarModel = int(json['forcedCarModel'])
    t.overrideDriverInfo = int(json['overrideDriverInfo'])
    t.isServerAdmin = int(json['isServerAdmin'])
    t.ballastKg = int(json['ballastKg'])
    t.configVersion = int(json['configVersion'])

    t.drivers = []
    for driver in json['drivers']:
        t.drivers.append(_json_to_driver(driver))

    return t



def _event_to_json(e: Event):
    d = dict({
        'name': e.name
    })

    # serialize the list of teams
    d['entries'] = []
    for t in e.teams:
        d['entries'].append(_team_to_json(t))

    return d



def _json_to_event(json):
    e = Event()

    e.name = json['name']

    e.teams = []
    for team in json['entries']:
        e.teams.append(_json_to_team(team))

    return e





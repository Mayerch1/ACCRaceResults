import os
import sys
import json
import codecs
import data
from data import Driver, Team, Event


def dump_entrylist(event: Event):
    ev_json = data._event_to_json(event)
    del ev_json['name']

    with open('entrylist.json', 'w') as out_file:
        out_file.writelines(json.dumps(ev_json, indent=4, sort_keys=True))


def parse_server_result(file):

    if file is None or not os.path.exists(file):
        print('couldn\'t locate file ' + file)
        return None


    ev = Event()
    
    with open(file, 'r', encoding='utf_16_le') as json_file:
        json_str = ' '.join(json_file.readlines())
        data = json.loads(json_str)

        ev.name = data['trackName']

        leaders = data['sessionResult']['leaderBoardLines']

        i = 1
        for team_json in leaders:
            car = team_json['car']

            team = Team()
            team.defaultGridPosition = i
            team.forcedCarModel = car['carModel']
            team.raceNumber = car['raceNumber']
            
            for driver in car['drivers']:
                d = Driver()
                d.firstName = driver['firstName']
                d.lastName = driver['lastName']
                d.shortName = driver['shortName']
                d.playerID = driver['playerId']

                team.drivers.append(d)

            ev.teams.append(team)
            i += 1

    return ev
        

def search_results():
    steam_dir = r'C:\Program Files (x86)\Steam\steamapps\common\Assetto Corsa Competizione Dedicated Server\server\results'
    # search oder:
    # 1. result folder in PWD
    # 2. result folder in default steam-folder
    # 3. json files in PWD
    if os.path.exists('./results'):
        files = os.listdir('./results')
    elif os.path.exists(steam_dir):
        files = os.listdir(steam_dir)
    else:
        files = os.listdir('./')


    files = list(filter(lambda x: x.endswith('.json'), files))
        
    if files:
        return files[0]
    else: 
        return None


def search_results_interactive():
    print('Couldn\'t auto-detect the result file\nPlease enter the path:')
    input_str = input()

    if os.path.exists(input_str):
        if os.path.isfile(input_str) and input_str.endswith('.json'):
            return input_str
        else:
            files = os.listdir(input_str)
            files = list(filter(lambda x: x.endswith('.json'), files))
            if files:
                return input_str + '/' + files[0]
            else: 
                return None

    return None



def main(file_path = None):

    if file_path is None:
        file_path = search_results()

        if file_path is None:
            file_path = search_results_interactive()

        if file_path is None:
            return



    print('using ' + file_path)
    event = parse_server_result(file_path)


    if event is None:
        print('failed to parse event')
        return


    dump_entrylist(event)
    print('dumped entrylist')



if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = None


    main(file_path)
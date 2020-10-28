import os
import sys
import json
import codecs
import data
from data import Driver, Team, Event
import serverResult


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

    try:
        with open(file, 'r') as json_utf8:
            json_lines = json_utf8.readlines()
            json_str = ' '.join(json_lines)
            data = json.loads(json_str)
    except json.JSONDecodeError:
         with open(file, 'r', encoding='utf_16_le') as json_utf16:
            json_lines = json_utf16.readlines()
            json_str = ' '.join(json_lines)
            data = json.loads(json_str)


    event = serverResult.parse_data(data)
        

    return event

    
    
        

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

        if file_path is None or file_path.endswith('entrylist.json'):
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
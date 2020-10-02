import sys
import os
import json



def get_race_over_timestamp(json_laps):
    """get the first player to reach the number of race laps
       => this is the winner

    Args:
        json_laps ([type]): [description]

    Returns:
        [int]: timestamp of race finish, could be None on incomplete dataset
    """

    # cannot use lapCount, as this is not guaranteed to be the leaders lapCount
    total_lap_cnt = json_laps[-1].get('lapNumber', None)

    # iterating backwards would save iterations
    # but who cares about performances when using python...
    for lap in json_laps:
        if int(lap.get('lapNumber', -1)) == total_lap_cnt:
            return lap.get('lapCompletedTimestamp', None)

    return None





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



    # get all the participants
    # (sorted by leader after 1st lap)
    starter_laps = list(filter(lambda l: int(l['lapNumber'])==1, laps))


    # determin all 'finished' players
    # this is done by fetching the finish time of the leader
    # everyone who completes a lap after the leader is classed as 'finisher'
    race_over_timestamp = get_race_over_timestamp(laps)

    if not race_over_timestamp:
        # the archives must be incomplete, no last lap existing
        return


    #  get all laps which are finished (including leaders laps)
    finished_laps = list(filter(lambda lap: int(lap.get('lapCompletedTimestamp', -1) >= race_over_timestamp), laps))


    # would give sorted by 'who saw the flag first'
    # finished_laps.sort(key=lambda lap: lap.get('lapCompletedTimestamp', -1))


    # this will sort by lapNumber, cars with equal lapNumber are sorted by finishTime
    # this functions, as the Companion outputs the data sorted by finishTime
    finished_laps.sort(key=lambda lap: lap['position'])


    print('Race participants (must have completed 1 or more laps)')
    # 1 offset for humans
    i = 1
    for starter in starter_laps:
        print(str(i) + '. ' + starter.get('driver', 'N/A'))
        i += 1


    print('\n')


    print('Race finishers')
    i = 1
    for finisher in finished_laps:
        print(str(i) + '. ' + finisher.get('driver', 'N/A'))
        i += 1






if __name__ == '__main__':
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = 'result.json'

    main(json_file)
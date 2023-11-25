from instat_to_wyscout_pandas import *
from reconstruct import *
import json

iter_list = [
    "type",
    "location",
    "team", 
    "opponentTeam",
    "player",
    "pass",
    "shot",
    "groundDuel",
    "aerialDuel",
    "infraction",
    "carry",
    "possession"
]

def row_transform(row):
    for category in iter_list:
        row[category]=reconstruct_cases(row,category)
    return row

def pands_to_json(dataframe, filename):
    df=dataframe.apply(row_transform, axis=1)

    dropping = ['type.', 'groundDuel.', 'aerialDuel.', 'shot.', 'location.', 'pass.', 'infraction.', 'player.', 'team.', 'possession.', 'opponentTeam.', 'carry.']
    columns_to_drop = [col for col in df.columns if any(sub in col for sub in dropping)]
    df = df.drop(columns=columns_to_drop)

    order= ['id','matchId',	'matchPeriod','minute',	'second','matchTimestamp','videoTimestamp','relatedEventId','type',	'location',	'team','opponentTeam','player', 'pass',	'shot',	'groundDuel', 'aerialDuel', 'infraction', 'carry', 'possession']
    df = df[order]

    jsondf=df.to_json(orient='records')

    with open("jsooon.json", 'w') as json_file:
        json_file.write(jsondf)

    midjson= df.to_json(orient='records')
    begin= '{"meta":[],"events":'
    end='}'
    finaljson = begin+midjson+end

    file_path = filename+'.json'

    # Save the JSON data to a file
    with open(file_path, 'w') as json_file:
        json_file.write(finaljson)
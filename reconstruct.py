import pandas as pd
import cmath
import numpy as np



def reconstruct_endloc(row):
    return {"x": row['pass.endLocation.x'], "y": row['pass.endLocation.y']}

def reconstruct_recipient(row):
    return {"id": row['pass.recipient.id'], "name": row['pass.recipient.name'], "position": row['pass.recipient.position']}

def reconstruct_poss_team(row):
    return {"id": row['possession.team.id'], "name": row['possession.team.name'], "formation": row['possession.team.formation']}

def reconstruct_poss_endloc(row):
    return {"x": row['possession.endLocation.x'], "y": row['possession.endLocation.y']}

def reconstruct_poss_startloc(row):
    return {"x": row['possession.startLocation.x'], "y": row['possession.startLocation.y']}

def reconstruct_attack(row): 
    if (pd.isna(row['possession.attack.withShot'])):
        return np.nan
    else:
        return {"withShot": row['possession.attack.withShot'], "withShotOnGoal": row['possession.attack.withShotOnGoal'], "withGoal": row['possession.attack.withGoal'], "flank": row['possession.attack.flank'], "withGoal": row['possession.attack.withGoal'], "xg": row['possession.attack.xg']}
    



def getgoalkeeper(row):
    return {"goalkeeperActionId": row['shot.goalkeeperActionId'], "id": row['shot.goalkeeper.id'], "name": row['shot.goalkeeper.name']}

def getopponent(row):
    return {"id": row['groundDuel.opponent.id'], "name": row['groundDuel.opponent.name'], "position": row['groundDuel.opponent.position']}

def getopponent_aerial(row):
    return {"id": row['aerialDuel.opponent.id'], "name": row['aerialDuel.opponent.name'], "position": row['aerialDuel.opponent.position'], "height": row['aerialDuel.opponent.height']}

def getopponent_infraction(row):
    return {"id": row['infraction.opponent.id'], "name": row['infraction.opponent.name'], "position": row['infraction.opponent.position']}

def reconstruct_carry_loc(row):
    return {"x": row['possession.endLocation.x'], "y": row['possession.endLocation.y']}

def reconstruct_cases(row, keyword): 
    match keyword:
        case "type":
            return {"primary": row['type.primary'], "secondary": row['type.secondary']}
        case "location":
            if (pd.isna(row['location.x'])):
                return np.nan
            return {"x": row['location.x'], "y": row['location.y']}
        case "team": 
            return {"id": row['team.id'], "name": row['team.name'], "formation": row['team.formation']}
        case "opponentTeam":
            return {"id": row['opponentTeam.id'], "name": row['opponentTeam.name'], "formation": row['opponentTeam.formation']}
        case "player": 
            return {"id": row['player.id'], "name": row['player.name'], "position": row['player.position']}
        case "pass":
            if (pd.isna(row['pass.accurate'])):
                return np.nan
            rec = reconstruct_recipient(row)
            endloc =reconstruct_endloc(row)
            return {"accurate": row['pass.accurate'], "angle": row['pass.angle'], "height": row['pass.height'], "length": row['pass.length'], "recipient": rec, "endLocation": endloc}
        case "possession": 
            if (pd.isna(row['possession.startLocation.x'])):
                return np.nan
            startloc = reconstruct_poss_startloc(row)
            endloc = reconstruct_poss_endloc(row)
            team = reconstruct_poss_team(row)
            attack = reconstruct_attack(row)
            return {"id": row['possession.id'], "duration": row['possession.duration'], "types": row['possession.types'], "eventsNumber": row['possession.types'], "eventIndex": row['possession.types'], "startLocation": startloc,"endLocation": endloc, "team": team, "attack": attack}
        case "shot": 
            if (pd.isna(row['shot.bodyPart'])):
                return np.nan
            keeper = getgoalkeeper(row)
            return {"bodyPart": row['shot.bodyPart'], "isGoal": row['shot.isGoal'], "onTarget": row['shot.onTarget'], "goalZone": row['shot.goalZone'], "xg": row['shot.xg'], "postShotXg": row['shot.postShotXg'], "goalkeeper": keeper}
        case "groundDuel": 
            if (pd.isna(row['groundDuel.duelType'])):
                return np.nan
            opponent = getopponent(row)
            return {"opponent": opponent, "duelType": row['groundDuel.duelType'], "keptPossession": row['groundDuel.keptPossession'], "progressedWithBall": row['groundDuel.progressedWithBall'], "stoppedProgress": row['groundDuel.stoppedProgress'], "recoveredPossession": row['groundDuel.recoveredPossession'], "takeOn": row['groundDuel.takeOn'], "side": row['groundDuel.side'], "relatedDuelId": row['groundDuel.relatedDuelId'] }
        case "aerialDuel":
            if (pd.isna(row['aerialDuel.opponent.name'])):
                return np.nan
            opponent = getopponent_aerial(row)
            return {"opponent": opponent, "firstTouch": row['aerialDuel.firstTouch'], "height": row['aerialDuel.height'], "relatedDuelId": row['aerialDuel.relatedDuelId']}
        case "infraction": 
            if (pd.isna(row['infraction.yellowCard'])):
                return np.nan
            opponent = getopponent_infraction(row)
            return {"yellowCard": row['infraction.yellowCard'], "redCard": row['infraction.redCard'], "type": row['infraction.type'], "opponent": opponent}
        case "carry":
            if (pd.isna(row['carry.progression'])):
                return np.nan
            return {"progression": row['carry.progression'], "endLocation": {"x": row['carry.endLocation.x'], "y": row['carry.endLocation.y']}}





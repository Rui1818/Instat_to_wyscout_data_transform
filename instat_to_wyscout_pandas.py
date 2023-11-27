import pandas as pd
import cmath
import numpy as np
from transformations import *

#set all unknown attributes
id=matchId=videoTimestamp=relatedEventId=teamId=opponentTeamId=playerId=passrecipientId=possessionId = 0
possessioneventIndex=possessionteamId=groundDuelopponentId=groundDuelrelatedDuelId=infractionopponentId=shotgoalkeeperActionId=shotgoalkeeperId=aerialDuelopponentId=aerialDuelrelatedDuelId = 0
passheight=groundduel_take_on=ground_side=None
postshotxg=shotxg=shotgoalzone=possessionattackxg=aerialduelheight=aerialFirsttouch=aerialdueloppheight=np.nan
carry_x=carry_y=carry_prog=possessioneventsNumber=np.nan

def create_event(instat, ind):
    global current_possession,poss_types, withshot,withshotongoal, withgoal, flank
    
    index_instat, typeprimary, typesecondary = get_event_type(instat, ind)
    action = instat['action_name'].iloc[ind]
    #setup every attribute
    period=get_period(instat,ind)
    minute, second, matchTimestamp = get_time(instat, ind, period)
    locx, locy = get_location(instat, ind)
    teamname = instat['team_name'].iloc[ind]
    teamformation = teamA[1] if (teamname==teamA[0]) else teamB[1]
    oppteamname = teamB[0] if (teamname==teamA[0]) else teamA[0]
    oppteamformation = teamB[1] if (teamname==teamA[0]) else teamA[1]
    playername = instat['player_name'].iloc[ind]  #have to change to player names
    playerposition = position_transform(instat['position_name'].iloc[ind], teamformation)
    passlength = instat['len'].iloc[ind]
    isnewposs,possindex = newposs(instat, ind, index_instat)
    possteamname = instat['possession_team_name'].iloc[ind]
    possteamformation = teamA[1] if (possteamname==teamA[0]) else teamB[1]
    possession = instat['possession_name'].iloc[ind]
    keptPoss=None if ('defensive_duel' in typesecondary) else (False if possession=='Transition of possession' else True)
    stopped_prog=None if ('offensive_duel' in typesecondary) else (True if possession=='Transition of possession' else False)
    keepercoord_x, keepercoord_y=get_goalkeeper_coordinates(instat, ind, index_instat, keeperA, keeperB)

    #passing
    if not (pd.isna(instat["pos_dest_x005F_x"].iloc[ind])) and typeprimary!='shot':
        passaccurate=isaccurate_pass(action)
        passangle=calculate_angle(instat["pos_x005F_x"].iloc[ind], instat["pos_y"].iloc[ind], instat["pos_dest_x005F_x"].iloc[ind], instat["pos_dest_y"].iloc[ind])
        passend_x, passend_y=get_dest_location(instat,ind)
        if(passaccurate):
            passrec, passrec_pos_instat = get_pass_recipient(instat, ind)
            passrec_pos = position_transform(passrec_pos_instat, teamformation) 
        else:passrec= passrec_pos_instat=passrec_pos=np.nan
    else:
        passaccurate=passangle=passend_x=passend_y=passrec=passrec_pos=np.nan
    
    #shot
    if (isshot(action)):
        goalkeeper = keeperA[0] if (teamname!=keeperA[1]) else keeperB[0]
        bodypart=bodypart_transform(instat['body_name'].iloc[ind])
        isgoal= True if 'goal' in typesecondary else False
        isontarget= True if (action=='Shot on target' or action == 'Goal') else False
    else:
        bodypart=isgoal=isontarget=goalkeeper=np.nan

    #infraction
    if(action=='infraction'):
        isyellow=True if ('yellow_card' in typesecondary) else False
        isred = True if ('red_card' in typesecondary) else False
        infraction_type = 'regular_foul' if action!='Deferred foul' else 'late_card_foul' #there are more types of fouls
        infractionopp = instat['opponent_name'].iloc[ind]
        infractionopp_pos = position_transform(instat['opponent_position_name'].iloc[ind], oppteamformation)
    else:
        isyellow=isred=infraction_type=infractionopp=infractionopp_pos=np.nan

    #duel
    if(typeprimary=='duel'):
        aerialopp=aerialopp_pos=groundopp=groundopp_pos =grounddueltype=np.nan 
        ground_stopped_prog=ground_recov_poss =ground_side=groundkeptposs=groundduel_progressed_with_ball=np.nan

        duelopp = instat['opponent_name'].iloc[ind]
        duelopp_pos = position_transform(instat['opponent_position_name'].iloc[ind], oppteamformation)

        #adjust loss tag
        if ('loss' in typesecondary):
            if(stopped_prog==True):
                typesecondary.remove('loss')

        if ('aerial_duel' in typesecondary):
            aerialopp=duelopp
            aerialopp_pos = duelopp_pos
            
        else:
            groundopp=duelopp
            groundopp_pos = duelopp_pos
            grounddueltype = 'dribble' if 'dribble' in typesecondary else ('defensive_duel' if 'defensive_duel' in typesecondary else 'offensive_duel')
            groundkeptposs = keptPoss
            groundduel_progressed_with_ball=groundkeptposs #not so clear what progressed with ball means exactly
            ground_stopped_prog=stopped_prog
            ground_recov_poss =ground_stopped_prog #not so clear
            

    else:
        aerialopp=aerialopp_pos=groundopp=groundopp_pos =grounddueltype=np.nan 
        ground_stopped_prog=ground_recov_poss =ground_side=groundkeptposs=groundduel_progressed_with_ball=np.nan

    #possession
    if (current_possession[5]>ind):
        poss_x=poss_y=endposs_x=endposs_y=possessionType=np.nan
    else:
        poss_x=current_possession[0]
        poss_y=current_possession[1]
        endposs_x=current_possession[2]
        endposs_y=current_possession[3]
        possessionType=poss_types
    
    if (isnewposs==True):
        current_possession,poss_types, withshot,withshotongoal, withgoal, flank = setnewpossession(instat, possindex+1) 

    new_event = {
        "id": id,
        "matchId": matchId,
        "matchPeriod":period,
        "minute":minute,
        "second":second,
        "matchTimestamp":matchTimestamp,
        "videoTimestamp":videoTimestamp,
        "relatedEventId":relatedEventId,
        "shot":np.nan,
        "groundDuel":np.nan,
        "aerialDuel":np.nan,
        "infraction":np.nan,
        "carry":np.nan,
        "type.primary":typeprimary,	
        "type.secondary":typesecondary,
        "location.x":locx,	
        "location.y":locy,	
        "team.id":teamId,	
        "team.name": teamname,	
        "team.formation":teamformation,	
        "opponentTeam.id":opponentTeamId,
        "opponentTeam.name":oppteamname,	
        "opponentTeam.formation":oppteamformation,	
        "player.id":playerId,	
        "player.name":playername,	
        "player.position":playerposition,	
        "pass.accurate":passaccurate,	
        "pass.angle":passangle,	
        "pass.height":passheight,	
        "pass.length":passlength,	
        "pass.recipient.id":passrecipientId,	
        "pass.recipient.name":passrec,	
        "pass.recipient.position":passrec_pos,
        "pass.endLocation.x":passend_x,	
        "pass.endLocation.y":passend_y,	
        "possession.id":possessionId,	
        "possession.duration":current_possession[4],	
        "possession.types":possessionType,	
        "possession.eventsNumber":possessioneventsNumber,	
        "possession.eventIndex":possessioneventIndex,	
        "possession.startLocation.x":poss_x,
        "possession.startLocation.y":poss_y,	
        "possession.endLocation.x":endposs_x,	
        "possession.endLocation.y":endposs_y,	
        "possession.team.id":possessionteamId,	
        "possession.team.name":possteamname,	
        "possession.team.formation":possteamformation,	
        "possession.attack":np.nan,	
        "pass":np.nan,
        "groundDuel.opponent.id":groundDuelopponentId,	
        "groundDuel.opponent.name":groundopp,	
        "groundDuel.opponent.position":groundopp_pos,	
        "groundDuel.duelType":grounddueltype,	
        "groundDuel.keptPossession":groundkeptposs,	
        "groundDuel.progressedWithBall":groundduel_progressed_with_ball,	
        "groundDuel.stoppedProgress":ground_stopped_prog,	
        "groundDuel.recoveredPossession":ground_recov_poss,	
        "groundDuel.takeOn":groundduel_take_on,	
        "groundDuel.side":ground_side,
        "groundDuel.relatedDuelId":groundDuelrelatedDuelId,	
        "infraction.yellowCard":isyellow,	
        "infraction.redCard":isred,	
        "infraction.type":infraction_type,	
        "infraction.opponent.id":infractionopponentId,	
        "infraction.opponent.name":infractionopp,	
        "infraction.opponent.position":infractionopp_pos,	
        "possession.attack.withShot":withshot,	
        "possession.attack.withShotOnGoal":withshotongoal,	
        "possession.attack.withGoal":withgoal,	
        "possession.attack.flank":flank,	
        "possession.attack.xg":possessionattackxg,	
        "carry.progression":carry_prog,	
        "carry.endLocation.x":carry_x,	
        "carry.endLocation.y":carry_y,	
        "shot.bodyPart":bodypart,	
        "shot.isGoal":isgoal,	
        "shot.onTarget":isontarget,	
        "shot.goalZone":shotgoalzone,	
        "shot.xg": shotxg,	
        "shot.postShotXg":postshotxg,	
        "shot.goalkeeperActionId":shotgoalkeeperActionId,	
        "shot.goalkeeper.id":shotgoalkeeperId,	
        "shot.goalkeeper.name":goalkeeper,	
        "possession":np.nan,	
        "aerialDuel.opponent.id":aerialDuelopponentId,	
        "aerialDuel.opponent.name":aerialopp,	
        "aerialDuel.opponent.position":aerialopp_pos,	
        "aerialDuel.opponent.height":aerialdueloppheight,	
        "aerialDuel.firstTouch":aerialFirsttouch,	
        "aerialDuel.height":aerialduelheight,	
        "aerialDuel.relatedDuelId":aerialDuelrelatedDuelId,	
        "shot.goalkeeper":np.nan,	
        "infraction.opponent":np.nan,	
        "location":np.nan
    }
    
    #check when second event has to be generated
    if (typeprimary=='duel'):
        new_event_2=create_second_duel_event(new_event, keptPoss, stopped_prog, current_possession,poss_types, withshot,withshotongoal, withgoal, flank, isnewposs,ind)
        return index_instat,[new_event, new_event_2]
    elif (action=='Shot on target' or action=='Goal'):
        new_event_2=create_second_shot_event(new_event, keeperA, keeperB, keepercoord_x, keepercoord_y)
        return index_instat,[new_event, new_event_2]
     
    return index_instat, [new_event]


def pandas_transform(path):
    global keeperA
    global keeperB
    global teamA
    global teamB
    global current_possession,poss_types, withshot,withshotongoal, withgoal, flank
    #instatiate empty dataframe with wyscout format
    template_path='template.csv'
    df=pd.read_csv(template_path)
    wyscoutdf=df

    #load instat file
    instat_path = path
    instatdf=pd.read_xml(instat_path)
    instatdf=instatdf.iloc[2:,:]
    instatdf.drop(columns=['column','number','dl', 'id', 'uid', 'action_id', 'player_id', 'team_id', 'standart_id', 'ts', 'position_id', 'opponent_id', 'opponent_team_id','opponent_position_id', 'zone_id', 'zone_dest_id', 'possession_id', 'possession_team_id', 'possession_team_id', 'attack_status_id', 'attack_type_id', 'attack_team_id', 'body_id' ], inplace=True)
    #get the goalkeepers
    keeperA,keeperB= get_keepers(instatdf)

    #remove unnecessairy rows
    mask = (instatdf['second']==0.00) & (~instatdf['player_name'].isna()) & (instatdf['action_name']!='Attacking pass accurate')
    instatdf = instatdf[~mask]
    todrop = ['line-up', 'Substitute player', '1st half','2nd half', 'Players, that created offside trap']
    mask = ~instatdf['action_name'].isin(todrop)
    instatdf = instatdf[mask]
    teamA,teamB=getformations(instatdf)

    mask = (instatdf['second']==0)&(instatdf['action_name']!='Attacking pass accurate')
    instatdf = instatdf[~mask] 
    #ready for wyscout transformation

    #instatiate first possession
    current_possession,poss_types, withshot,withshotongoal, withgoal, flank=setnewpossession(instatdf,0) #start x, y, end x, y, possession_duration, possessionstart index|possession types, attack variables

    index = 0   
    while (True):
        index, newevents = create_event(instatdf, index)
        for event in newevents:
            wyscoutdf = pd.concat([wyscoutdf, pd.DataFrame([event])], ignore_index=True)
        if(instatdf['action_name'].iloc[index]=='Match end'):
            break
        
    return wyscoutdf


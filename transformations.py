import json
import pandas as pd
import cmath
import xml.etree.ElementTree as et
import numpy as np
from datetime import timedelta
import math

#parameter lists

shotlist = ['Shot into the bar/post',
    'Blocked shot',
    'Shots blocked',
    'Shot on target',
    'Chance was not converted by',
    'Wide shot',
    'Shot blocked by field player',
    'Chance was converted by',
    'Accurate crossing from set piece with a shot',
    'Misplaced crossing from set piece with a shot',
    'Accurate crossing from set piece with a goal',
    'Set piece cross with goal',
    'Goal'
]

ontarget= [
    'Shot on target',
    'Goal'
]

primary_events=[
    'Match end', 
    'Clearance',
    'Offside',
    'Own goal',
    'Tackle',
    'Challenge',
    'Air challenge',
    'Successful dribbling',
    'Unsuccessful dribbling',
    'Ball out of the field',
    'Deferred foul',
    'Red card',
    'Foul',
    'Yellow card',
    'RC for two YC',
    'Pass interceptions',
    'Shots blocked',
    'Cross interception',
    'Attacking pass accurate',
    'Attacking pass inaccurate',
    'Accurate key pass',
    'Inaccurate key pass', 
    'Non attacking pass inaccurate',
    'Non attacking pass accurate', 
    'Blocked shot',
    'Shot on target',
    'Wide shot',
    'Shot blocked by field player',
    'Goal', 
    'Assist'
]
standart_events=[
    'Indirect free kick',
    'Goal kick',
    'Corner',
    'Throw-in',
    'Direct free kick',
    'Penalty'
]

duel_events= [
    'Tackle',
    'Challenge',
    'Air challenge',
    'Successful dribbling',
    'Unsuccessful dribbling'
]
gameinterruption_events=[
    'Ball out of the field'  #are there more events?
]

infraction_events = [
    'Deferred foul',
    'Red card',
    'Foul',
    'Yellow card',
    'RC for two YC'
]
interception_events = [
    'Pass interceptions',
    'Shots blocked',
    'Cross interception'
]

pass_events = [
    'Attacking pass accurate',
    'Attacking pass inaccurate',
    'Accurate key pass',
    'Inaccurate key pass', #'Extra attacking pass accurate',
    'Non attacking pass inaccurate',
    'Non attacking pass accurate',
    'Assist'
]
shot_events = [
    'Blocked shot',
    'Shot on target',
    'Wide shot',
    'Shot blocked by field player', #'Shot into the bar/post',
    'Goal'
]

losslist = [
    'Attacking pass inaccurate',
    'Inaccurate key pass',
    'Non attacking pass inaccurate',
    'Lost balls'
]

opplist=[
    'Chance was converted by',
    'Chance was not converted by'
]

shotassistlist=[
    'Misplaced crossing from set piece with a shot',
    'Accurate crossing from set piece with a shot',
    'Accurate crossing from set piece with a goal',
    'Misplaced crossing from set piece with a goal'
]

accurat_pass=[
    'Attacking pass accurate',
    'Accurate key pass', #'Extra attacking pass accurate',
    'Non attacking pass accurate',
    'Assist'
]
#subfunctions
def isshot (action):
    if action in shotlist:
        return True
    return False


def iswithin20meters(x, y):
    newx=105-x
    newy=34-y
    distance2= math.pow(newx,2)+math.pow(newy,2)
    d=math.sqrt(distance2)
    if(d<=20):
        return True
    return False



def standart_transform(standart):
    match standart:
        case 'Indirect free kick':
            return "free_kick"
        case 'Goal kick':
            return "goal_kick"
        case 'Corner':
            return "corner"
        case 'Throw-in':
            return "throw-in"
        case 'Direct free kick':
            return "free_kick"
        case 'Penalty':
            return "penalty"
        case _:
            raise Exception("something went wrong in standart transform")


def calculate_angle(x,y,destx,desty):
    dx=destx-x
    dy=desty-y
    angle = math.atan2(dy, dx)
    angle= math.degrees(angle)
    return round(angle,1)

def isinpenaltybox(x,y):
    newx,newy = location_transform(x,y)
    if (newx>=84 and newy>=19 and newy<=81):
        return True
    return False

def isinfinalthird(x):
    if(x>=70):
        return True
    return False

def isaccurate_pass(action):
    if (action in accurat_pass):
        return True
    return False

def position_transform(instat_position, formation):
    defenders=formation[0]
    midfielders = formation[2]
    match instat_position:
        case 'Goalkeeper':
            return "GK"
        case 'Defender - Central':
            return "CB"
        case 'Defender - Left central':
            if (defenders==4):
                return "LCB"
            return "LCB3"
        case 'Defender - Right central':
            if (defenders==4):
                return "RCB"
            return "RCB3"
        case 'Defender - Right':
            if (defenders==5):
                return "RB5"
            return "RB"
        case 'Defender - Left':
            if (defenders==5):
                return "LB5"
            return "LB"
        case 'Defensive midfielder - Right central':
            return "RDMF"
        case 'Defensive midfielder - Left central':
            return "LDMF"
        case 'Defensive midfielder - Central':
            return "DMF"
        case 'Midfielder - Right central':
            if(midfielders==3 or midfielders==5):
                return "RCMF3"
            return "RCMF"
        case 'Midfielder - Left central':
            if(midfielders==3 or midfielders==5):
                return "LCMF3"
            return "LCMF"
        case 'Midfielder - Right':
            return "RW"
        case 'Midfielder - Left':
            return "LW"
        case 'Attacking midfielder - Right central':
            return "RAMF"
        case 'Attacking midfielder - Left central':
            return "LAMF"
        case 'Attacking midfielder - Right':
            return "RWF"
        case 'Attacking midfielder - Left':
            return "LWF"
        case 'Attacking midfielder - Central':
            return "AMF"
        case 'Forward - Right central':
            return "SS"
        case 'Forward - Left central':
            return "CF"
        case 'Forward - Central':
            return "CF"
        case None:
            return None
        case _:
            print(instat_position)
            raise Exception("position could not be found")
        





def get_possession_type(df, ind, list):
    t = df['standart_name'].iloc[ind]
    t2 = df['attack_type_name'].iloc[ind]
    match t:
        case "Direct free kick":
            list+=["direct_free_kick"]
        case "Corner":
            list+=["corner"]
        case "Throw-in":
            list+=["throw-in"]
        case "Penalty":
            list+=["penalty"]
 
    match t2:
        case "Counter-attack":
            list+=["counterattack", "attack"]
        case None:
            return list
        case _:
            list+=["attack"]
    return list

def get_possession_attack(df, ind, withshot, withshotongoal, goal, flank):
    t2 = df['attack_type_name'].iloc[ind]
    action = df['action_name'].iloc[ind]
    flang = df['attack_flang_name'].iloc[ind]
    
    match t2:
        case None:
            return withshot, withshotongoal, goal, flank
        case _:
            if(np.isnan(withshot)):
                withshot=withshotongoal=goal=False
                flank = flang
                return withshot, withshotongoal, goal, flank
            else:
                if (action in shotlist):
                    withshot=True
                if(action in ontarget):
                    withshotongoal=True
                if(action=='Goal'):
                    goal=True
                flank = flang
                return withshot, withshotongoal, goal, flank
            
def getformations(dataframe): 
    df=dataframe['action_name']
    dft=dataframe['team_name']
    list=[]
    team=[]
    for i in range(4):
        x=df.iloc[i]
        teams = dft.iloc[i]
        if ('2'<x[0]<'6'):
            list+=[x]
            team+=[teams]

    team1 = [team[0], list[0]]
    team2 = [team[1], list[1]]
            
    return team1, team2

def time_transform(sec):
    t=timedelta(seconds=sec)
    if(t.microseconds>0):
       return str(t)[:-3] 
    return str(t)+'.000'



def get_formation(team, formationlist, teamlist):
    if (team==teamlist[0]):
        return formationlist[0]
    return formationlist[1]


def location_transform(x,y):
    new_x = x*100/105
    new_y = y*-100/68+100
    return round(new_x,1),round(new_y,1)
    

#attribute functions

def get_keepers(df):
    index=0
    counter=0
    lp=[]
    lt=[]
    while counter<2:
        if(df['action_name'].iloc[index]=='GK'):
            player=df['player_name'].iloc[index]
            team=df['team_name'].iloc[index]
            lp+=[player]
            lt+=[team]
            counter+=1
        index+=1
    return [lp[0],lt[0]],[lp[1],lt[1]]

def bodypart_transform(bodypart):
    if (bodypart=='Head' or bodypart=='Hand'):
        return "head_or_other"
    if (bodypart=='Right foot'):
        return "right_foot"
    if (bodypart=='Left foot'):
        return "left_foot"
    return np.nan


def get_period(df, index):
    per = df['half'].iloc[index]
    if (per==1):
        return "1H"
    return "2H"

def get_time(df, index, period):
    sec = df['second'].iloc[index]
    if(period=='2H'):
        sec=sec+2700   
    min = int(sec/60)
    second = int(sec%60)
    return min, second, time_transform(sec)

def get_location(df, index):
    locx = df["pos_x005F_x"].iloc[index]
    locy = df["pos_y"].iloc[index]
    return location_transform(locx, locy)

def get_dest_location(df, index):
    locx = df["pos_dest_x005F_x"].iloc[index]
    locy = df["pos_dest_y"].iloc[index]
    return location_transform(locx, locy)

def get_pass_recipient(df, ind):
    origin_team = df['team_name'].iloc[ind]
    origin_player = df['player_name'].iloc[ind]
    index=ind+1
    action=df['action_name'].iloc[index]
    rec = df['player_name'].iloc[index]
    rec_team = df['team_name'].iloc[index]
    while (origin_team!=rec_team or origin_player==rec):
        if(action=='Match End'):
            return np.nan, np.nan
        index+=1
        rec = df['player_name'].iloc[index]
        rec_team= df['team_name'].iloc[index]
    position = df['position_name'].iloc[index]
    return rec, position


def newposs(df, minindex, maxindex):
    ind=minindex
    if (df['possession_time'].iloc[ind]>0):
        return True, ind
    while(ind<maxindex):
        ind+=1
        if(df['possession_time'].iloc[ind]>0):
            return True, ind
        
    
    return False, ind


def setnewpossession(df, index):
    poss_types=[]
    withshot=withshotongoal= withgoal=flank=np.nan
    
    if(df['action_name'].iloc[index]=='Match end'):
        return [0,0,0,0,0,index], poss_types, withshot, withshotongoal, withgoal, flank
    
    length = df['possession_time'].iloc[index]
    while (np.isnan(length)):
        index+=1
        if(df['action_name'].iloc[index]=='Match end'):
            return [0,0,0,0,0,index], poss_types, withshot, withshotongoal, withgoal, flank
        length = df['possession_time'].iloc[index]

    
    i = index
    if (length==0):
        startx, starty = get_location(df, index)
        poss_types=get_possession_type(df, index, poss_types)
        withshot, withshotongoal, withgoal, flank = get_possession_attack(df, index, withshot, withshotongoal, withgoal, flank)
    else:
        startx,starty=get_location(df, index)
        poss_types=[]

    while (np.isnan(length) or length==0):
        index+=1
        if(df['action_name'].iloc[index]=='Match end'):
            return [0,0,0,0,0,index], poss_types, withshot,withshotongoal, withgoal, flank
        length = df['possession_time'].iloc[index]
        poss_types=get_possession_type(df, index, poss_types)
        withshot,withshotongoal, withgoal, flank = get_possession_attack(df, index, withshot, withshotongoal, withgoal, flank)

    endx, endy = get_location(df,index)
    return [startx, starty, endx, endy, length, i], list(set(poss_types)), withshot, withshotongoal, withgoal, flank




def get_primary_type (df, index):
    action = df['action_name'].iloc[index]
    standart = df['standart_name'].iloc[index]
    t=df['second'].iloc[index]
    if standart in standart_events:
        if (t>0):
            return standart_transform(standart)
    if action =='Clearance':
        return "clearance"
    if action in duel_events:
        return "duel"
    if action in gameinterruption_events:
        return "game_interruption"
    if action in infraction_events:
        return "infraction"
    if action in interception_events:
        return "interception"
    if action == 'Offside':
        return "offside"
    if action == 'Own goal':
        return "own_goal"
    if action in pass_events:
        return "pass"
    if action in shot_events:
        return "shot"
    if action == "Dribbling":
        "touch"
    else:
        print('index: '+index+', ')
        print(df['action_name'].iloc[index])
        raise Exception("no primary event was found")
    
def check_duel_secondaries(df, index, action, secondary):
    possessionteam = df['possession_team_name'].iloc[index]
    team = df['team_name'].iloc[index]
    if(action=='Unsuccessful dribbling' or 'Successful dribbling'):
        secondary+=["dribble"]
    if(action=='Air challenge'):
        secondary+=["aerial_duel"]
    else:
        secondary+=["ground_duel"]
    if (action=="Tackle"):
        secondary+=["sliding_tackle"]
    if (team==possessionteam):
        secondary+=["offensive_duel"]
    else:
        secondary+=["defensive_duel"]

    return secondary

def check_pass_secondaries(df, index, action, secondary):
    length= df['len'].iloc[index]
    posx=df['pos_x005F_x'].iloc[index]
    posy=df['pos_y'].iloc[index]
    destx=df['pos_dest_x005F_x'].iloc[index]
    desty=df['pos_dest_y'].iloc[index]
    bodypart = df['body_name'].iloc[index]

    if (bodypart=='Hand'):
        secondary+=["hand_pass"]
    if (action=='Assist'):
        secondary+=["assist"]
    if (action=='Crosses accurate' or action=='Crosses inaccurate' or action == 'Inaccurate blocked cross'):
        secondary+=["cross"]
    if (action=='Inaccurate blocked cross'):
        secondary+=["cross_blocked"]
    if (length>45):
        secondary+=["long_pass"]
    else:
        secondary+=["short_or_medium_pass"]
    
    if (action=='Inaccurate key pass' or action=='Accurate key pass'):
        secondary+=["key_pass"]
    if (not isinfinalthird(posx)) and isinfinalthird(destx):
        secondary+=["pass_to_final_third"]
    if (not isinpenaltybox(posx,posy)) and isinpenaltybox(destx,desty):
        secondary+=["pass_into_penalty_area"]

    if not (np.isnan(destx)):
        if (action=='Crosses accurate' and iswithin20meters(destx,desty)):
            secondary+=['deep_completed_cross']
            if('deep_completion' in secondary):
                secondary.remove('deep_completion')
        if (action=='Accurate key pass' or action=='Attacking pass accurate') and iswithin20meters(destx,desty):
            secondary+=["deep_completion"]
        #pass directions
        angle=calculate_angle(posx,posy,destx, desty)
        if (angle<45 and angle>-45):
            secondary+=["forward_pass"]
        elif (angle>135 or angle<-135):
            secondary+=["back_pass"]
        elif (length >12):
            secondary+=["lateral_pass"]

    return secondary


def check_free_kick_secondaries(df,index, action, secondary):
    freekickcrosslist=shotassistlist+['Accurate crossing from set piece']+['Inaccurate set-piece cross']
    if action in shot_events:
        secondary+=["free_kick_shot"]

    if action in freekickcrosslist:
        secondary+=["free_kick_cross"]
    return secondary 


def check_shot_secondaries(df,index, action, secondary):
    bodypart= df['action_name'].iloc[index]
    if (bodypart=='Header'):
        secondary+=["head_shot"]
    if (action=='Goal'):
        secondary+=["goal"]
    return secondary 


def check_infraction_secondaries(df,index, action, secondary):
    if (action=='Foul' or action=='Deferred foul'):
        secondary+=["foul"]
    if(action=='Yellow card'):
        secondary+=["yellow_card"]
    if(action=='Red card'):
        secondary+=["red_card"]
    return secondary 


def check_game_interruption_secondaries(df,index, action, secondary):
    if(action=='Ball out of the field'):
        secondary+=["ball_out"]
    return secondary 

def check_interception_secondaries(df,index, action, secondary):
    if action=='Shot blocked by field player' or action=='Shots blocked':
        secondary+=["shot_block"]
    return secondary 

def check_touch_secondaries(df,index, action, secondary):
    if (action=='Dribbling'):
        secondary+=['carry']

    return secondary



def get_secondary_type(df, index, primary, secondary):
    #general tags
    action = df['action_name'].iloc[index]
    possession_status= df['possession_name'].iloc[index]
    posx=df['pos_x005F_x'].iloc[index]
    posy=df['pos_y'].iloc[index]

    if action in shotassistlist:
        secondary+=["shot_assist"]

    if primary!='infraction' and primary!='game_interruption' and ((action in losslist) or possession_status=='End'):
        secondary+=["loss"]

    if action in opplist:
        secondary+=["opportunity"]

    if primary!='duel' and (isinpenaltybox(posx,posy)):
        secondary+=["touch_in_box"]
    #specialized tags
    match primary:
        case "pass":
            secondary=check_pass_secondaries(df,index, action, secondary)
        case "free_kick":
            secondary=check_free_kick_secondaries(df,index, action, secondary)
        case "shot":
            secondary=check_shot_secondaries(df,index, action, secondary)
        case "duel":
            secondary=check_duel_secondaries(df,index, action, secondary)
        case "infraction":
            secondary=check_infraction_secondaries(df,index, action, secondary)
        case "game_interruption":
            secondary=check_game_interruption_secondaries(df,index, action, secondary)
        case "interception":
            secondary=check_interception_secondaries(df,index, action, secondary)
        case "touch":
            secondary=check_touch_secondaries(df,index, action, secondary)
        case _:
            return secondary

    return secondary


def get_event_type(df, index):
    action = df['action_name'].iloc[index]
    if (action=='Match end'):
        raise Exception ("event match end should not been reached in this state")
    
    primary = get_primary_type(df, index)
    secondary = get_secondary_type(df, index, primary, [])
    
    index+=1
    action = df['action_name'].iloc[index]
    while(action not in primary_events):  #have to check penalties
        secondary = get_secondary_type(df, index,primary, secondary)
        index+=1
        action=df['action_name'].iloc[index]

    
    return index, primary, list(set(secondary))




def create_second_duel_event(new_event, keptPoss, stopped_prog, current_possession,poss_types, withshot,withshotongoal, withgoal, flank, newposs, ind):
    new_event_2=new_event.copy()
    opponent=new_event['player.name']
    opp_position=new_event['player.position']
    opp_team=new_event['team.name']
    opp_formation=new_event['team.formation']
    team=new_event['opponentTeam.name']
    formation=new_event['opponentTeam.formation']

    secondary=new_event['type.secondary']
    newsecondary = []
    #add secondary tags
    if ('defensive_duel' in secondary):
        newsecondary+=['offensive_duel']
    else:
        newsecondary+=['defensive_duel']

    if('aerial_duel' in secondary):
        newsecondary+=['aerial_duel']
    else:
        newsecondary+=['ground_duel']
    
    if(stopped_prog==True):
        newsecondary+=['recovery']
    if(keptPoss==False):
        newsecondary+=['loss']
    
    #set possession when it change
    if(newposs):
        if (current_possession[5]>ind):
            new_event_2['possession.startLocation.x']=np.nan
        else:
            new_event_2['possession.startLocation.x']=current_possession[0]
            new_event_2['possession.startLocation.y']=current_possession[1]
            new_event_2['possession.endLocation.x']=current_possession[2]
            new_event_2['possession.endLocation.y']=current_possession[3]
            new_event_2['possession.attack.withShot']=withshot
            new_event_2['possession.attack.withShotOnGoal']=withshotongoal
            new_event_2['possession.attack.withGoal']=withgoal
            new_event_2['possession.attack.flank']=flank
            new_event_2['possession.types']=poss_types

            
            if ('defensive_duel' in secondary):
                if (stopped_prog==True):
                    new_event_2['possession.team.name']=team
                    new_event_2['possession.team.formation']=formation
                else:
                    new_event_2['possession.team.name']=opp_team
                    new_event_2['possession.team.formation']=opp_formation
            else:
                if (keptPoss==False):
                    new_event_2['possession.team.name']=opp_team
                    new_event_2['possession.team.formation']=opp_formation
                else:
                    new_event_2['possession.team.name']=team
                    new_event_2['possession.team.formation']=formation




    #set the new event correctly

    if ('aerial_duel' in secondary):
        player=new_event['aerialDuel.opponent.name'] 
        player_pos=new_event['aerialDuel.opponent.position']
        new_event_2['aerialDuel.opponent.name'] = opponent
        new_event_2['aerialDuel.opponent.position'] = opp_position

    else:
        player=new_event['groundDuel.opponent.name']
        player_pos=new_event['groundDuel.opponent.position'] 
        new_event_2['groundDuel.opponent.name'] = opponent
        new_event_2['groundDuel.opponent.position'] = opp_position
        dueltype = new_event['groundDuel.duelType']
        new_event_2['groundDuel.duelType'] = 'defensive_duel' if (dueltype=='dribble') else ('offensive_duel' if dueltype=='defensive_duel' else 'defensive_duel')
        new_event_2['groundDuel.keptPossession'] = None if ('defensive_duel' in newsecondary) else (False if stopped_prog==True else True)
        new_event_2['groundDuel.stoppedProgress'] = None if ('offensive_duel' in newsecondary) else (False if keptPoss==True else True)
        new_event_2['groundDuel.recoveredPossession'] = new_event_2['groundDuel.stoppedProgress']
        new_event_2['groundDuel.progressedWithBall'] = new_event_2['groundDuel.keptPossession']

    new_event_2['type.secondary']=newsecondary
    new_event_2['team.name']=opp_team
    new_event_2['team.formation']=opp_formation
    new_event_2['opponentTeam.name']=team
    new_event_2['opponentTeam.formation']=formation
    new_event_2['team.formation']=opp_formation
    new_event_2['player.name']=player
    new_event_2['player.position']=player_pos
    
    return new_event_2

def get_goalkeeper_coordinates(df, minindex, maxindex, keeperA, keeperB):
    index=minindex
    keeper=keeperA[0] if (df['team_name'].iloc[index]==keeperB[1]) else keeperB[0]
    while(index<maxindex):
        if(keeper==df['player_name'].iloc[index]):
            return location_transform(df['pos_x005F_x'].iloc[index], df['pos_y'].iloc[index])
        index+=1

    return np.nan, np.nan

def create_second_shot_event(new_event, keeperA, keeperB, keepercoord_x, keepercoord_y):    
    #to do: correct timestamps

    new_event_2=new_event.copy()
    opp_team=new_event['team.name']
    opp_formation=new_event['team.formation']
    team=new_event['opponentTeam.name']
    formation=new_event['opponentTeam.formation']
    goalkeeper_name= keeperB[0] if opp_team==keeperA[1] else keeperA[0]

    
    newsecondary = []

    #set new secondary tags
    if ('goal' in new_event['type.secondary']):
        newsecondary+=['conceded_goal']
    else:
        newsecondary+=['save'] #no supersaves yet
    
    new_event_2['type.primary']='shot_against'
    new_event_2['type.secondary']=newsecondary
    new_event_2['location.x']=keepercoord_x
    new_event_2['location.y']=keepercoord_y
    new_event_2['type.secondary']=newsecondary
    new_event_2['team.name']=opp_team
    new_event_2['team.formation']=opp_formation
    new_event_2['opponentTeam.name']=team
    new_event_2['opponentTeam.formation']=formation
    new_event_2['team.formation']=opp_formation
    new_event_2['player.name']=goalkeeper_name
    new_event_2['player.position']='GK'

    #set the other categories to nan
    new_event_2['possession.startLocation.x']=np.nan
    new_event_2['shot.bodyPart']=np.nan


    return new_event_2

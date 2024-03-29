#this file has all the necessary transformation functions for the wyscout entries. 
import pandas as pd
import cmath
import numpy as np
from datetime import timedelta, datetime
import math

#action lists (no instat documentation->might be incomplete)
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
    'Dribbling',
    'Ball out of the field',
    'Deferred foul',
    'Foul',
    'Yellow card',
    'Red card',
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
    'Shot into the bar/post',
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
    'Ball out of the field'  
]

infraction_events = [
    'Deferred foul',
    'Foul',
    'Yellow card','Red card'
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
    'Shot blocked by field player', 
    'Shot into the bar/post',
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



#helper functions
def getmatchId(df):
    #function to extract the Instat match id of the current game. Takes a dataframe as input.
    ind=0
    id = df['id'].iloc[0]
    while(np.isnan(id)):
        ind+=1
        id = df['id'].iloc[ind]
    return id

def isshot (action):
    #check if a action is in the shot category. Takes a string as input.
    if action in shotlist:
        return True
    return False


def iswithin20meters(x, y):
    #checks if the location is within 20 meters in regard of the goal. Takes x and y coordinates in Instat format as input.
    newx=105-x
    newy=34-y
    distance2= math.pow(newx,2)+math.pow(newy,2)
    d=math.sqrt(distance2)
    if(d<=20):
        return True
    return False

def get_side(y):
    #checks on which side the current location is. takes the y coordinates in Wyscout format as input. 
    if (y<33.4):
        return 'left'
    if(y>66.6):
        return 'right'
    return None

def standart_transform(standart):
    #transforms a Instat to a wyscout standart word. Takes a string as input. 
    match standart:
        case 'Indirect free kick':
            return "free_kick"
        case 'Goal kick':
            return "goal_kick"
        case 'Corner':
            return "corner"
        case 'Throw-in':
            return "throw_in"
        case 'Direct free kick':
            return "free_kick"
        case 'Penalty':
            return "penalty"
        case _:
            raise Exception("something went wrong in standart transform")


def calculate_angle(x,y,destx,desty):
    #calculates the angle of a pass according to wyscout standards. Takes two location coordinate pairs as input. 
    dx=destx-x
    dy=desty-y
    angle = math.atan2(dy, dx)
    angle= math.degrees(angle)
    return int(round(angle,0))

def isinpenaltybox(x,y): 
    #check if the location is in the penalty box. takes a location pair as input. 
    newx,newy = location_transform(x,y)
    if (newx>=84 and newy>=19 and newy<=81):
        return True
    return False

def isinfinalthird(x):
    #checks if location is in the final third. Takes the x coordinate in Instat format as input. 
    if(x>=70):
        return True
    return False

def isaccurate_pass(action):
    #check if a action is a accurate pass. Takes a string as input. 
    if (action in accurat_pass):
        return True
    return False

def is_prog_pass(x,destx):
    #checks if a pass is progressive according to wyscout definition. Takes two x coordinates in instat format as input
    dx=destx-x
    if(x<=52.5):
        if(destx<=52.5):
            if(dx>=30):
                return True
            else:
                return False
        else:
            if(dx>=15):
                return True
            else:
                return False
    else:
        if(dx>=10):
            return True
        else:
            return False

def position_transform(instat_position, formation):
    #returns the wyscout position based on the instat position and formation. takes two strings as input. 
    defenders=int(formation[0]) if formation[0].isdigit() else 4
    midfielders = int(formation[2]) if formation[2].isdigit() else 4
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
            return None
            #print(instat_position)
            #raise Exception("position could not be found")

def adjustformation(formation):
    #matches the instat formation with a wyscout formation. Takes a string as input. 
    match formation:
        case '4-4-2 diamond':
            return '4-3-1-2'
        case '4-4-2 classic':
            return '4-4-2'
        case _:
            return formation
            
def getformations(dataframe): 
    #extracts both of the team formations. takes a dataframe as input
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
    if(len(list)<2):
        for j in range(100):
            teams=dft.iloc[j]
            if(teams not in team and teams!=None):
                team+=[teams]
            if(len(team)==2):
                if(len(list)<1):
                    return [team[0],'no formation'], [team[1], 'no formation']
                else:
                    return [team[0], list[0]], [team[1], 'no formation']
                    
    team1 = [team[0], adjustformation(list[0])]
    team2 = [team[1], adjustformation(list[1])]
            
    return team1, team2

def time_transform(sec):
    #transforms instat time to wyscout time format. takes an integer as input.
    t=timedelta(seconds=sec)
    if(t.microseconds>0):
       return str(t)[:-3] 
    return str(t)+'.000'


def get_formation(team, formationlist, teamlist):
    #returns a teams formation given a team, a list, and the data structure saving this information. 
    if (team==teamlist[0]):
        return formationlist[0]
    return formationlist[1]


def location_transform(x,y):
    #transforms instat to wyscout coordinates. Takes instat coordinates as input.
    new_x = x*100/105
    new_y = y*-100/68+100
    return round(new_x,1),round(new_y,1)
    
def get_keepers(df):
    #funtion to extract the goalkeepers for both teams and returns it in form of a pair. 
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
    #returns the body part in wyscout format. Takes a string as input
    if (bodypart=='Header' or bodypart=='Hand'):
        return "head_or_other"
    if (bodypart=='Right foot'):
        return "right_foot"
    if (bodypart=='Left foot'):
        return "left_foot"
    return np.nan

def isprogrun(x, destx):
    #function to check if the current action is a progressive run according to wyscout. takes two x coordinates as input
    dx=destx-x
    if(x<=50):
        if(destx<=50):
            if(dx>=28.5):
                return True
            else:
                return False
        else:
            if(dx>=14.2):
                return True
            else:
                return False
    else:
        if(dx>=9.5):
            return True
        else:
            return False

def get_period(df, index):
    #returns the current half or extra time. Takes a dataframe and a index as input. 
    per = df['half'].iloc[index]
    if (per==1):
        return "1H"
    elif (per==2):
        return "2H"
    elif(per==3):
        return "1E"
    elif(per==4):
        return "2E"
    else:
        return "P"

def get_time(df, index, period):
    #transforms instat time format to wyscout time format, given the dataframe, a index and the current period.
    sec = df['second'].iloc[index]
    if(period=='2H'):
        sec=sec+2700   
    elif(period=='1E'):
        sec=sec+5400
    elif(period=='2E'):
        sec=sec+6300
    elif(period=='P'):
        sec=sec+7200
    min = int(sec/60)
    second = int(sec%60)
    return min, second, time_transform(sec)

def get_location(df, index):
    #returns the current location in wyscout format, given a dataframe and the index.
    locx = df["pos_x005F_x"].iloc[index]
    locy = df["pos_y"].iloc[index]
    return location_transform(locx, locy)

def get_dest_location(df, index):
    #returns the destination location in wyscout format, given a dataframe and the index.
    locx = df["pos_dest_x005F_x"].iloc[index]
    locy = df["pos_dest_y"].iloc[index]
    return location_transform(locx, locy)

def get_pass_recipient(df, ind):
    #returns the recipient of a pass and his position. Takes a dataframe and index. 
    origin_team = df['team_name'].iloc[ind]
    origin_player = df['player_name'].iloc[ind]
    index=ind+1
    action=df['action_name'].iloc[index]
    rec = df['player_name'].iloc[index]
    rec_team = df['team_name'].iloc[index]
    while (origin_team!=rec_team or origin_player==rec):
        if(action=='Match end'):
            return np.nan, np.nan
        index+=1
        action=df['action_name'].iloc[index]
        rec = df['player_name'].iloc[index]
        rec_team= df['team_name'].iloc[index]
    position = df['position_name'].iloc[index]
    return rec, position

def isshotassist(df, ind):
    #check if a action is a shot assist..
    if(df['action_name'].iloc[ind]=='Match end'):
        return False
    if(get_primary_type(df, ind)=='shot'):
        return True
    return False


#function for possessions
def newposs(df, minindex, maxindex):
    ind=minindex
    if (df['possession_time'].iloc[ind]>0):
        return True, ind
    while(ind<maxindex):
        ind+=1
        if(df['possession_time'].iloc[ind]>0):
            return True, ind
        
    
    return False, ind

def get_possession_type(df, ind, list):
    t = df['standart_name'].iloc[ind]
    t2 = df['attack_type_name'].iloc[ind]
    match t:
        case "Direct free kick":
            list+=["direct_free_kick"]
        case "Corner":
            list+=["corner"]
        case "Throw-in":
            list+=["throw_in"]
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



#functions to get the primary/secondary tag
def get_primary_type (df, index):
    action = df['action_name'].iloc[index]
    standart = df['standart_name'].iloc[index]
    t=df['second'].iloc[index]
    if action in infraction_events:
        return "infraction"
    if standart in standart_events:
        if (t>0):
            return standart_transform(standart)
    if action =='Clearance':
        return "clearance"
    if action in duel_events:
        return "duel"
    if action in gameinterruption_events:
        return "game_interruption"
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
        return "touch"
    else:
        print(df['action_name'].iloc[index])
        print('index: ',index)
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
    if(bodypart=='Head'):
        secondary+=["head_pass"]
    if (action=='Assist'):
        secondary+=["assist"]
    if (action=='Crosses accurate' or action=='Crosses inaccurate' or action == 'Inaccurate blocked cross'):
        secondary+=["cross"]
    if (action=='Inaccurate blocked cross'):
        secondary+=["cross_blocked"]
    if (length>45):
        secondary+=["long_pass"]
    elif(length<=45):
        secondary+=["short_or_medium_pass"]
    
    if (action=='Inaccurate key pass' or action=='Accurate key pass'):
        secondary+=["key_pass"]
    if (not isinfinalthird(posx)) and isinfinalthird(destx):
        secondary+=["pass_to_final_third"]
    if (not isinpenaltybox(posx,posy)) and isinpenaltybox(destx,desty):
        secondary+=["pass_into_penalty_area"]

    if not (np.isnan(destx)):
        if(is_prog_pass(posx,destx)):
            secondary+=['progressive_pass']
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
    if (action=='Goal'):
        secondary+=["goal"]
    if action in freekickcrosslist:
        secondary+=["free_kick_cross"]
    return secondary 


def check_shot_secondaries(df,index, action, secondary):
    bodypart= df['body_name'].iloc[index]
    if (bodypart=='Header'):
        secondary+=["head_shot"]
    if (action=='Goal'):
        secondary+=["goal"]
    if(action=='Supersaves'):
        secondary+=['save_with_reflex']
    return secondary 

def check_penalty_secondaries(df,index, action, secondary):
    if(action=='Goal'):
        secondary+=['penalty_goal']
        secondary+=['goal']
    if(action=='Supersaves'):
        secondary+=['save_with_reflex']
    return secondary

def check_postmatchpenalty_secondaries(df, index, action, secondary):
    if(action=='Supersaves'):
        secondary+=['save_with_reflex']
    return secondary

def check_infraction_secondaries(df,index, action, secondary):
    ispen=df['standart_name'].iloc[index]
    if(ispen=='Penalty'):
        secondary+=['penalty_foul']
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

    if primary!='infraction' and primary!='game_interruption' and primary!='penalty' and ((action in losslist) or possession_status=='End'):
        secondary+=["loss"]

    if action in opplist:
        secondary+=["opportunity"]

    if (isinpenaltybox(posx,posy)) and (primary=='shot' or primary=='pass' or primary=='touch'):
        secondary+=["touch_in_box"]
    #specialized tags
    match primary:
        case "penalty":
            secondary=check_penalty_secondaries(df, index, action, secondary)
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
        case "postmatch_penalty":
            secondary=check_postmatchpenalty_secondaries(df, index, action, secondary)
        case _:
            return secondary

    return secondary


def updateinformations(df, index, teamA, teamB, keeperA, keeperB):
    #updates formations and goalkeepers in the case of a substitution
    if(df['action_name'].iloc[index]=='Substitution'):
            
        ind=index+1
        while (df['action_name'].iloc[ind]!='Match end' and ind<(index+23)):
            action=df['action_name'].iloc[ind]
            if(action=='GK'):
                team=df['team_name'].iloc[ind]
                if(keeperA[1]==team):
                    keeperA[0]=df['player_name'].iloc[ind]
                else:
                    keeperB[0]=df['player_name'].iloc[ind]
            if(action[0].isnumeric() and action[2].isnumeric()):
                team=df['team_name'].iloc[ind]
                if(team==teamA[0]):
                    teamA[1]=action
                else:
                    teamB[1]=action
            ind+=1

def get_event_type(df, index, teamA, teamB,keeperA, keeperB, period):
    #function to determine the current primary and secondaries. Also returns the index pointing to the next triggerword. 
    action = df['action_name'].iloc[index]
    if (action=='Match end'):
        raise Exception ("event match end should not been reached in this state")
    wasfoul=(action=='Foul')
    primary = get_primary_type(df, index) if (period!='P') else 'postmatch_penalty'
    secondary = get_secondary_type(df, index, primary, [])
    
    index+=1
    action = df['action_name'].iloc[index]
    if(wasfoul):
        while(action not in primary_events or action=='Yellow card' or action=='Red card'):  #skip over cards if it was a foul
            updateinformations(df, index, teamA, teamB, keeperA, keeperB)
            secondary = get_secondary_type(df, index,primary, secondary)
            index+=1
            action=df['action_name'].iloc[index]
    else:
        while(action not in primary_events):  #have to check penalties
            updateinformations(df, index, teamA, teamB, keeperA, keeperB)
            secondary = get_secondary_type(df, index,primary, secondary)
            index+=1
            action=df['action_name'].iloc[index]
    
    
    return index, primary, list(set(secondary))




#functions for coupled events (shot_against, duel)
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

def create_second_shot_event(new_event, keeperA, keeperB, keepercoord_x, keepercoord_y, reflexsave):    
    #to improve: timestamps interpolation

    new_event_2=new_event.copy()
    opp_team=new_event['team.name']
    opp_formation=new_event['team.formation']
    team=new_event['opponentTeam.name']
    formation=new_event['opponentTeam.formation']
    goalkeeper_name= keeperB[0] if opp_team==keeperA[1] else keeperA[0]

    
    newsecondary = []

    #set new secondary tags
    if(new_event['type.primary']!='postmatch_penalty'):
        new_event_2['type.primary']='shot_against'
        if ('goal' in new_event['type.secondary']):
            newsecondary+=['conceded_goal']
            if('penalty_goal' in new_event['type.secondary']):
                newsecondary+=['penalty_conceded_goal']
        else:
            if(reflexsave):
                newsecondary+=['save_with_reflex']
                if(new_event['type.primary']=='penalty'):
                    newsecondary+=['penalty_save']
            newsecondary+=['save']
    else:
        new_event_2['type.primary']='postmatch_penalty_faced'
        if(new_event['shot.isGoal']):
            newsecondary+=['conceded_postmatch_penalty']
        elif(reflexsave):
            newsecondary+=['postmatch_penalty_saved']
    
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

def isshotafter(timestamp, wyscout):
    #check if a action is after a shot. takes a timestamp and a wyscout dataframe as input.
    format_str = "%H:%M:%S.%f" 
    formattedtimestamp = datetime.strptime(timestamp, format_str)
    ind=wyscout.index[-1]
    time = datetime.strptime(wyscout['matchTimestamp'].iloc[ind], format_str)
    ty = wyscout['type.primary'].iloc[ind]
    delta=timedelta(seconds=14)
    while(ind>0 and formattedtimestamp-time<delta):
        if(ty=='corner'):
            return 1
        elif(ty=='free_kick'):
            return 2
        elif(ty=='throw_in'):
            return 3
        ind-=1
        time=datetime.strptime(wyscout['matchTimestamp'].iloc[ind], format_str)
    return 0

def isrecovery(possteam,wyscout,secondary, timestamp):
    #check if a action is a recovery. Takes a teamname, a wyscout dataframe, the current secondary list and a timestamp as input.
    ind=wyscout.index[-1]
    format_str = "%H:%M:%S.%f" 
    formattedtimestamp = datetime.strptime(timestamp, format_str)
    time = datetime.strptime(wyscout['matchTimestamp'].iloc[ind], format_str)
    wyposs = wyscout['possession.team.name'].iloc[ind]
    primary=wyscout['type.primary'].iloc[ind]
    delta=timedelta(seconds=5)
    if(wyposs!=None and possteam!=None):
        if (len(wyposs)>0) and (len(possteam)>0):
            if(possteam!=wyposs and primary!='game_interruption' and primary!='shot' and primary!='shot_against'):
                secondary+=['recovery']
                if(formattedtimestamp-time<delta):
                    secondary+=['counterpressing_recovery']
    

    return secondary

def foulsuffered(wyscout, name):
    #checks if the current player suffered a foul. Takes a wyscout dataframe and the current players name as input.
    ind=wyscout.index[-1]
    oppname=wyscout['player.name'].iloc[ind]
    primary=wyscout['type.primary'].iloc[ind]
    secondary=wyscout['type.secondary'].iloc[ind].copy()
    ind2=ind-1
    if(primary=='duel'):
        if(oppname!=name):
            secondary+=['foul_suffered']
            wyscout['type.secondary'].iloc[ind]=secondary
        elif(wyscout['player.name'].iloc[ind2]!=name):
            if(wyscout['player.name'].iloc[ind2]!=name):
                secondary+=['foul_suffered']
                wyscout['type.secondary'].iloc[ind2]=secondary



def create_goal_kick(wyscout, destx, desty, keeperA, keeperB, teamA, teamB, new_event):
    goalkickevent=new_event.copy()
    poss_team=new_event['possession.team.name']
    poss_formation=new_event['possession.team.formation']
    locx=0.0
    locy=50.0
    dx=destx-locx
    dy=desty-locy
    angle=calculate_angle(locx,locy,destx,desty)
    length=math.sqrt(dx*dx+dy*dy)
    goalkeeper_name= keeperA[0] if poss_team==keeperA[1] else keeperB[0]
    oppteam=teamB[0] if (poss_team==teamA[0]) else teamA[0]
    oppformation = teamB[1] if (poss_team==teamA[0]) else teamA[1]
    accurate=np.nan
    
    goalkickevent['type.primary']='goal_kick'
    goalkickevent['type.secondary']=['generated_goal_kick']
    goalkickevent['location.x']=locx
    goalkickevent['location.y']=locy
    goalkickevent['team.name']=poss_team
    goalkickevent['team.formation']=poss_formation
    goalkickevent['opponentTeam.name']=oppteam
    goalkickevent['opponentTeam.formation']=oppformation
    goalkickevent['player.name']=goalkeeper_name
    goalkickevent['player.position']='GK'
    goalkickevent['pass.accurate']=accurate
    goalkickevent['pass.angle']=angle
    goalkickevent['pass.length']=length
    goalkickevent['pass.endLocation.x']=destx
    goalkickevent['pass.endLocation.y']=desty

    #set other categories to nan
    goalkickevent['shot.bodyPart']=np.nan
    goalkickevent['groundDuel.duelType']=np.nan
    goalkickevent['aerialDuel.opponent.name']=np.nan
    goalkickevent['infraction.type']=np.nan
    goalkickevent['carry.progression']=np.nan


    return goalkickevent
   
def create_throw_in(lastloc,lastlocy,destx,desty, teamA, teamB, new_event):
    event=new_event.copy()
    poss_team=new_event['possession.team.name']
    poss_formation=new_event['possession.team.formation']
    oppteam=teamB[0] if (poss_team==teamA[0]) else teamA[0]
    oppformation = teamB[1] if (poss_team==teamA[0]) else teamA[1]
    angle=calculate_angle(lastloc,lastlocy,destx,desty)
    dx=destx-lastloc
    dy=desty-lastlocy
    length=math.sqrt(dx*dx+dy*dy)

    event['type.primary']='throw_in'
    event['type.secondary']=['generated_throw_in']
    event['location.x']=lastloc
    event['location.y']=lastlocy
    event['team.name']=poss_team
    event['team.formation']=poss_formation
    event['opponentTeam.name']=oppteam
    event['opponentTeam.formation']=oppformation
    event['player.name']=np.nan
    event['player.position']=np.nan
    event['pass.accurate']=np.nan
    event['pass.angle']=angle
    event['pass.length']=length
    event['pass.endLocation.x']=destx
    event['pass.endLocation.y']=desty

    #set other categories to nan
    event['shot.bodyPart']=np.nan
    event['groundDuel.duelType']=np.nan
    event['aerialDuel.opponent.name']=np.nan
    event['infraction.type']=np.nan
    event['carry.progression']=np.nan

    return event


def create_touch(touchlocx, touchlocy, locx,locy, oldevent):
    event=oldevent.copy()
    event['location.x']=touchlocx
    event['location.y']=touchlocy
    event['type.primary']='touch'
    secondary=['carry']
    if(isprogrun(touchlocx, locx)):
        secondary+=['progressive_run']
    event['type.secondary']=secondary
    event['carry.progression']=locx-touchlocx
    event['carry.endLocation.x']=locx
    event['carry.endLocation.y']=locy
    event['pass.angle']=np.nan
    return event
# -*- coding: utf-8 -*-

IDS = {
       "Steve": "59fe35591ba8cc0001170517",
       "Adam":"59fe3555fa82bd0001122d57",
       "Chris":"59fe3c5e2eaf9c0001b18eea",
       "John":"59fe357e2506cb00017d24de",
       "JC":"59fe35497c5c290001ac139c",
       "Justin":"59fe35868ad76f0001dd4daa"
       }
LATEST_URL = "https://pubg.op.gg/api/users/{}/matches/recent?server=na&queue_size=&mode=fpp"
NEXT_TOKEN = "&after={}" # multiples of "20" (0-19) e.g. &after=19
PARAMS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Accept": "application/json"
          }
GET_OLD = False
N_PAGES = 100 #Assuming that there are at least 2000 matches here, might be 404

from datetime import datetime
from utils import my_print
from model import User, Match
import requests
from random import random
import time

def fillOutUser(SESSION, id, name):
    if not SESSION.query(User).filter(User.name==name).filter(User.id==id).all():
        u = User()
        u.id = id
        u.name = name
        SESSION.add(u)

def fillOutMatch(SESSION, match,name,id):
    user = SESSION.query(User).filter(User.id==id).filter(User.name==name).one()
    
    d =  datetime.strptime(match['started_at'], "%Y-%m-%dT%H:%M:%S%z" )
    
    _m = SESSION.query(Match).filter(Match.user_id==user.id).\
                            filter(Match.user_name==user.name).\
                            filter(Match.date==d).\
                            filter(Match.id==match['match_id']).all()
                            
    #Don't add duplicate data
    if len(_m) > 0:
        #my_print("duplicate data!")
        return True
    
    participant = match['participant']
    stats = participant['stats']
    combat = stats['combat']
    
    m = Match()
    
    m.pubg_id = participant['_id']
    
    # 2018-01-24T03:10:17+0000
    
    m.date = d
    m.id = match['match_id']
    m.mode = match['mode']
    m.queue_size = match['queue_size']
    
    m.rank = stats['rank']
    m.rating_delta = stats['rating_delta']
    
    m.boosts  = combat['boosts']
    m.damage  = combat['damage']['damage_dealt']
    m.knocks = combat['dbno']['knock_downs']
    m.revives = combat['dbno']['revives']
    m.death_type = combat['death_type']
    
    m.ride_distance = combat['distance_traveled']['ride_distance']
    m.walk_distance = combat['distance_traveled']['walk_distance']
    m.distance_traveled = m.ride_distance + m.walk_distance
    
    m.heals = combat['heals']
    
    m.assists = combat['kda']['assists']
    m.headshot_kills = combat['kda']['headshot_kills']
    m.kill_steaks = combat['kda']['kill_steaks']
    m.kills = combat['kda']['kills']
    m.longest_kill = combat['kda']['longest_kill']
    m.road_kills = combat['kda']['road_kills']
    m.team_kills = combat['kda']['team_kills']
    m.kda = m.kills + m.assists
    
    m.kill_place = combat['kill_place']
    m.most_damage = combat['most_damage']
    m.time_survived = combat['time_survived']
    m.vehicle_destroys = combat['vehicle_destroys']
    m.weapon_acquired = combat['weapon_acquired']
    m.win_place = combat['win_place']
    
    m.user_id = user.id
    m.user_name = user.name
    
    m.user.append(user)
    
    user.matches.append(m)
    
    SESSION.add(m)
    return False

def getData(SESSION):
    for n, _id in IDS.items():
        try:
            fillOutUser(SESSION, _id, n)
        except Exception as e:
            my_print("{} already in users!".format(n))
        my_print("Adding {} to database".format(n))
        dupe = False;
        for p in range(0, N_PAGES):
            time.sleep(random()*3+1)  # sleep from 1-4seconds between requests
            if dupe:
                if not GET_OLD:
                    break
            try:
                url = LATEST_URL.format(_id)
                if p > 0:
                    #need to get the hash of the last request's id
                    try: 
                        #get the last match in the list
                        token = j["matches"]["items"][-1]["offset"]
                    except Exception:
                        token=""
                        my_print("Couldn't get the token")
                        break; # no point continuing
                    url += NEXT_TOKEN.format(token)
                #my_print(url)
                r = requests.get(url,params=PARAMS)
                j = r.json()
                matches = j['matches']['items']
                if len(matches) > 0:
                    for m in matches:
                        dupe = fillOutMatch(SESSION, m, n, _id)
                        if dupe:
                            break
                        
                else:
                    # If there were no matches we've gone too far
                    break
                
            except Exception as e:
                print(e)
                continue
        SESSION.commit() # commit after each user
    SESSION.commit()
    SESSION.close()
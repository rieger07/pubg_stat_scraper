# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 21:55:20 2018

@author: Steve
"""
IDS = {
       "Steve": "59fe35591ba8cc0001170517",
       "Adam":"59fe3555fa82bd0001122d57",
       "Chris":"59fe3c5e2eaf9c0001b18eea",
       "John":"59fe357e2506cb00017d24de",
       "JC":"59fe35497c5c290001ac139c",
       "Justin":"59fe35868ad76f0001dd4daa"
       }
LATEST_URL = "https://pubg.op.gg/api/users/{}/matches/recent?server=na&queue_size={}&mode=fpp"
NEXT_TOKEN = "&after={}" # multiples of "20" (0-19) e.g. &after=19
PARAMS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Accept": "application/json"
          }

#GET /api/users/59fe35591ba8cc0001170517/matches/recent?server=na&queue_size=4&mode=fpp&after=19 HTTP/1.1
#Host: pubg.op.gg
#User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0
#Accept: application/json, text/plain, */*
#Accept-Language: en-US,en;q=0.5
#Accept-Encoding: gzip, deflate, br
#Referer: https://pubg.op.gg/user/Asralis?server=na
#X-XSRF-TOKEN: eyJpdiI6ImFQTWZkXC80c0tHb3c5TU9XZjdBTVFBPT0iLCJ2YWx1ZSI6IjA4aW9IOVZhS3VNWnN0amRLRjdXT09BZHZBXC9aNmtoOCtNNmkya3ZpM0Iwa2J2OVdZWWduRnBZMEQ5NkE4ZVVrZHM5T2tyTTlTMmpcLzJFRnI1bE5LdVE9PSIsIm1hYyI6IjEzNGM5ZjRmMWQ4ZmRkODhlZWNlMDYzNWQ1YmRiNzEzYTVjOTE1ODFkZWI0YjdhNTdkZmIxMjkyYzgzYjFhZTUifQ==
#Cookie: recent-searches=Shaderton,Hyde13,chocoTaco,NarayanJr,Asralis; favorites=Asralis,Hyde13,Shaderton,NarayanJr; XSRF-TOKEN=eyJpdiI6ImFQTWZkXC80c0tHb3c5TU9XZjdBTVFBPT0iLCJ2YWx1ZSI6IjA4aW9IOVZhS3VNWnN0amRLRjdXT09BZHZBXC9aNmtoOCtNNmkya3ZpM0Iwa2J2OVdZWWduRnBZMEQ5NkE4ZVVrZHM5T2tyTTlTMmpcLzJFRnI1bE5LdVE9PSIsIm1hYyI6IjEzNGM5ZjRmMWQ4ZmRkODhlZWNlMDYzNWQ1YmRiNzEzYTVjOTE1ODFkZWI0YjdhNTdkZmIxMjkyYzgzYjFhZTUifQ%3D%3D; pubg_session=eyJpdiI6IlRpNStcL1pidXBxeXMwZEk3Z2ZhR2VBPT0iLCJ2YWx1ZSI6IkJnVWxva2JGT1hTT2hnam1HTUtKSG0zVlhCT3Z3VHk5a3NNXC9sZGJ4VHdoblR3WDE1MmowdHFBa1pvd2xBejJGV25KUGpVZXlYRlFRbEM0NHpWTGN2UT09IiwibWFjIjoiNmJhOWQ0MWU3MzQxNmM0OTQ2YTYwZTE2NGFhZWEzYWEwYmY0YThkMzQ0Nzc0ZGMzYjFkNTQ0MTc5NDhhNWEzMiJ9; _referrer=user,
#Connection: keep-alive

GET_OLD = 1
N_PAGES = 100 #Assuming that there are at least 200 matches here, might be 404


import requests
from model import User, Match, SESSION
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt



def fillOutUser(id, name):
    if not SESSION.query(User).filter(User.name==name).filter(User.id==id).all():
        u = User()
        u.id = id
        u.name = name
        SESSION.add(u)

def fillOutMatch(match,name,id):
    user = SESSION.query(User).filter(User.id==id).filter(User.name==name).one()
    
    d =  datetime.strptime(match['started_at'], "%Y-%m-%dT%H:%M:%S%z" )
    
    _m = SESSION.query(Match).filter(Match.user_id==user.id).\
                            filter(Match.user_name==user.name).\
                            filter(Match.date==d).\
                            filter(Match.id==match['match_id']).all()
                            
    #Don't add duplicate data
    if len(_m) > 0:
        return
    
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

def getData():
    for n, _id in IDS.items():
        try:
            fillOutUser(_id, n)
        except Exception as e:
            print("{} already in users!".format(n))
        print("Adding {} to database".format(n))
        for queue in range(1,5):
            for p in range(0, N_PAGES):
                url = LATEST_URL.format(_id,queue)
                if p > 0:
                    url += NEXT_TOKEN.format(20*p-1)
                
                r = requests.get(url,params=PARAMS)
                j = r.json()
                matches = j['matches']['items']
                if len(matches) > 0:
                    for m in matches:
                        fillOutMatch(m, n, _id)
                        
                else:
                    # If there were no matches we've gone too far
                    break
        
    SESSION.commit()
    SESSION.close()

def getDistances(name):
    
    temp = SESSION.query(Match.date, Match.user_name, Match.ride_distance, Match.walk_distance).filter(Match.user_name==name).order_by(Match.date.desc()).all()
    df = pd.DataFrame(temp)
    df.plot.hist(alpha=.5, title="{} Travel Samples".format(name))
    

def extractStuff():
    for u in SESSION.query(User).all():
        print(u.name)
        print("\t{} Matches Played".format(len(u.matches)))
        getDistances(u.name)
    

def main():
    getData()
    extractStuff()
    
            
if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 21:55:20 2018

@author: Steve
"""


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



import os
import argparse as ap
from model import User, Match, Base
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from data import getData
import pickle
from utils import my_print

pkl = os.path.realpath(os.path.join(__file__,"..","config.pkl"))

with open(pkl, "rb") as f:
    cfg = pickle.load(f)
    
py.sign_in(cfg["user"],cfg["key"])



def getDistances(SESSION, name):
    
    temp = SESSION.query(Match.date, Match.user_name, Match.ride_distance, Match.walk_distance).filter(Match.user_name==name).order_by(Match.date.desc()).all()
    df = pd.DataFrame(temp).set_index('date')
    ax = df.plot.hist(alpha=.5, title="{} Travel Samples".format(name), stacked=True)
    ax.set_xlabel('Distance (m)')    
    df.plot.box()

def getWalkBoxPlot(SESSION):
    df = pd.DataFrame()
    for u in SESSION.query(User).all():
        temp = SESSION.query(Match.date, Match.walk_distance).filter(Match.user_name==u.name).order_by(Match.date.desc()).all()
        temp_df = pd.DataFrame(temp,columns=['date',u.name]).set_index('date')
        df = pd.concat([df, temp_df])
    ax = df.plot.box()
    ax.set_ylabel('Distance Walked (m)')
    fname = os.path.realpath('walk.png')
    plt.savefig(fname)
    my_print(fname)
    
def getDriveBoxPlot(SESSION) :
    df = pd.DataFrame()
    for u in SESSION.query(User).all():
        temp = SESSION.query(Match.date, Match.ride_distance).filter(Match.user_name==u.name).order_by(Match.date.desc()).all()
        temp_df = pd.DataFrame(temp,columns=['date',u.name]).set_index('date')
        df = pd.concat([df, temp_df])
    ax = df.plot.box()
    ax.set_ylabel('Distance Driven (m)')
    
def getTravelBoxPlot(SESSION):
    df = pd.DataFrame()
    for u in SESSION.query(User).all():
        temp = SESSION.query(Match.date, Match.distance_traveled).filter(Match.user_name==u.name).order_by(Match.date.desc()).all()
        temp_df = pd.DataFrame(temp,columns=['date',u.name]).set_index('date')
        df = pd.concat([df, temp_df])
    ax = df.plot.box()
    ax.set_ylabel('Total Distance Traveled (m)')

def getDamageStats(SESSION):
    df = pd.DataFrame()
    for u in SESSION.query(User).all():
        temp = SESSION.query(Match.date, Match.damage).filter(Match.user_name==u.name).order_by(Match.date.desc()).all()
        temp_df = pd.DataFrame(temp,columns=['date',u.name]).set_index('date')
        df = pd.concat([df, temp_df])
    ax = df.plot.box()
    ax.set_ylabel('Damage')
    
def getHeadShotStats(SESSION):
    df = pd.DataFrame()
    for u in SESSION.query(User).all():
        temp = SESSION.query(Match.date, Match.user_name, Match.headshot_kills).filter(Match.user_name==u.name).order_by(Match.date.desc()).all()
        temp_df = pd.DataFrame(temp,columns=['date','name','headshots']).set_index('date')
        df = pd.concat([df, temp_df])
    _max = df['headshots'].max()
    df.hist(by=df['name'], bins=range(1,_max+1), sharey=True)

def getKillsStats(SESSION):
    df = pd.DataFrame()
    for u in SESSION.query(User).all():
        temp = SESSION.query(Match.date, Match.kills).filter(Match.user_name==u.name).order_by(Match.date.desc()).all()
        temp_df = pd.DataFrame(temp,columns=['date',u.name]).set_index('date')
        df = pd.concat([df, temp_df])
    ax = df.plot.box()
    ax.set_ylabel('Kills')
    
def getVehicleDestroys(SESSION):
    for u in SESSION.query(User).all():
        df = pd.DataFrame()
        for rank in SESSION.query(Match.rank).filter(Match.user_name==u.name).all():
            rank = rank[0]
            temp = SESSION.query(Match.date, Match.vehicle_destroys).filter(Match.user_name==u.name).filter(Match.rank==rank).order_by(Match.date.desc()).all()
            temp_df = pd.DataFrame(temp, columns=['date', rank]).set_index('date')
            df = pd.concat([df, temp_df])
        ax = df.plot.bar()
        ax.set_title("{} Vehicle Destruction".format(u.name))
        ax.set_ylabel('Destroys')

def extractStuff(SESSION):
    for u in SESSION.query(User).all():
        my_print(u.name)
        my_print("\t{} Matches Played".format(len(u.matches)))
        getDistances(u.name)

def makeTable(SESSION, user, columns=("date", "name", "rank", "kills"), limit=10):
    _cols = [getattr(Match,col) for col in columns]
    q = SESSION.query(*_cols).filter(Match.user_name.like(user)).order_by(Match.date.desc()).limit(limit)
    results = []
    for r in q:
        results.append(r)
    
    df = pd.DataFrame(results, columns=columns)
    table = ff.create_table(df)
    file_path = os.path.realpath('table.png')
    py.image.save_as(table, filename=file_path)
    my_print(file_path)

def getConnection(path=os.path.join(os.getcwd(),'pubg.sql')):
    ENGINE = create_engine(r"sqlite:///{}".format(path))
    S = sessionmaker(bind=ENGINE)
    Base.metadata.create_all(ENGINE)
    SESSION = S()
    return SESSION

def parseArgs(inargs=None):
    columns = [m.key for m in Match.__table__.columns]
    pimp = ap.ArgumentParser()
    pimp.add_argument("command", help="The command you want to run, ex: getData")
    pimp.add_argument("--path","-p", default=os.path.join(os.getcwd(),'pubg.sql'), help="The path to the database file")
    pimp.add_argument("--user","-u", default="Steve", help="The username for your query")
    pimp.add_argument("--columns",nargs="+", choices=columns, default=("date", "user_name", "rank", "kills"),help="The columns you want in the query")
    pimp.add_argument("--limit", default=10, help="The max number of rows you want returned")
    return pimp.parse_known_args(inargs)


def main(inargs=None):
    args, unk = parseArgs(inargs)
    command = args.command.lower();
    #my_print(args.path)
    SESSION=getConnection(args.path)
    
    if command=='getdata':
        try:
            getData(SESSION)
            my_print("Updated the Database!")
        except Exception as e:
            SESSION.rollback()
            my_print(e)
            my_print("Rolled the database back")
    elif command=='extractstuff':
        extractStuff(SESSION)
    elif command=='getWalkBoxPlot'.lower():
        getWalkBoxPlot(SESSION)
    elif command=='getDriveBoxPlot'.lower():
        getDriveBoxPlot(SESSION)
    elif command=='getTravelBoxPlot'.lower():
        getTravelBoxPlot(SESSION)
    elif command=='getDamageStats'.lower():
        getDamageStats(SESSION)
    elif command=='getHeadShotStats'.lower():
        getHeadShotStats(SESSION)
    elif command=='getKillsStats'.lower():
        getKillsStats(SESSION)
    elif command=='makeTable'.lower():
        makeTable(SESSION, args.user, args.columns, args.limit)
    else:
        my_print("invalid command {}".format(command))
    
if __name__ == "__main__":
    main()
    

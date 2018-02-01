# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 23:12:58 2018

@author: Steve
"""
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, DateTime, Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True, nullable=True)
    name = Column(String, primary_key=True, nullable=True)
    matches = relationship("Match", backref='user', foreign_keys=[id, name], 
                           primaryjoin="and_(User.id==Match.user_id, User.name==Match.user_name)",
                           uselist=True)
    
    def __repr__(self):
        return "<User(name={}, id={}, matches={})>".format(self.name, self.id, len(self.matches))
    
    
class Match(Base):
    __tablename__ = "match"
    id = Column(String, primary_key=True)
    date = Column(DateTime, primary_key=True)  # started_at
    user_id = Column(String, ForeignKey('user.id'), primary_key=True, nullable=True)
    user_name = Column(String, ForeignKey('user.name'), primary_key=True, nullable=True)
    pubg_id = Column(String)
    mode = Column(String)
    queue_size = Column(Integer)
    rank = Column(Integer)
    rating_delta = Column(Float)
    boosts = Column(Integer)
    damage = Column(Float)
    knocks = Column(Integer)
    revives = Column(Integer)
    death_type = Column(String)
    distance_traveled = Column(Float)
    ride_distance = Column(Float)
    walk_distance = Column(Float)
    heals = Column(Integer)
    kda = Column(Float)
    assists = Column(Integer)
    headshot_kills = Column(Integer)
    kill_steaks = Column(Integer)
    kills = Column(Integer)
    longest_kill = Column(Float)
    road_kills = Column(Integer)
    team_kills = Column(Integer)
    kill_place = Column(Integer)
    most_damage = Column(Float)
    time_survived = Column(Float)
    vehicle_destroys = Column(Integer)
    weapon_acquired = Column(Integer)
    win_place = Column(Integer)
    
    #user = relationship("User", back_populates="match", primaryjoin='and_(User.id==Match.user_id, User.name==Match.user_name)')
    
    def __repr__(self):
        return "<Match(match_id={}, date={}, user_id={}, user_name={}, mode={})>".format(self.id, self.date, self.user_id, self.user_name, self.mode)


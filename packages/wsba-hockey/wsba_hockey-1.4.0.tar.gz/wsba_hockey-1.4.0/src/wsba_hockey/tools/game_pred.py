import joblib
import os
import pandas as pd
import numpy as np
import xgboost as xgb
import scipy.sparse as sp
import wsba_hockey.wsba_main as wsba
import wsba_hockey.tools.scraping as scraping
import matplotlib.pyplot as plt
import requests as rs
from datetime import datetime, date, timedelta
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve, auc

### GAME PREDICTION MODEL FUNCTIONS ###
# Provided in this file are functions vital to the game prediction model in the WSBA Hockey Python package. #

## GLOBAL VARIABLES ##
target = "home_win"
continuous = [
    'fenwick_for_per_sixty',
    'expected_goals_for_per_fenwick_for',
    'goals_for_per_expected_goals_for',
    'fenwick_against_per_sixty',
    'expected_goals_against_per_fenwick_against',
    'goals_against_per_expected_goals_against',
    'giveaways_per_sixty',
    'takeaways_per_sixty',
    'power_play_percentage',
    'penalty_kill_percentage',
    'penalties_per_sixty',
    'penalties_drawn_per_sixty'
]
boolean = [
    'is_home',
    'back_to_back'
]

dir = os.path.dirname(os.path.realpath(__file__))
roster_path = os.path.join(dir,'rosters\\nhl_rosters.csv')
schedule_path = os.path.join(dir,'schedule\\schedule.csv')

def add_features(stats, playing):    
    #0 is away team win, 1 is home team win (we are predicting the probability the home team wins a given game)
    schedule['home_win'] = (schedule['home_score']>schedule['away_score']).astype(int)

    stats['back_to_back'] = (stats['team_abbr'].isin(playing)).astype(int)

    #Merge and filter down 
    for venue in ['away','home']:
        stats = pd.merge(schedule,stats,how='left',left_on=f'{venue}_team_abbr',right_on=)

    stats['is_home'] = (stats['team_abbr']==stats['home_team_abbr']).astype(int)

    return stats

def prep_game_data(pbp, season = None):
    #Prepare schedule data for model development given full-season pbp

    schedule = pd.read_csv(schedule_path)

    #Initialize schedule with stats 

    #Calculate necessary team stats (by game) for the prediction model
    #The model will evaluate based on three different qualities for valid EV, PP, and SH strength 
    dfs = []

    if not season:
        season = pbp['season'].iloc[0]

    season_data = rs.get('https://api.nhle.com/stats/rest/en/season').json()['data']
    season_data = [s for s in season_data if s['id'] == season][0]
    start = season_data['startDate'][0:10]
    end = season_data['endDate'][0:10]

    form = '%Y-%m-%d'
    start = datetime.strptime(start,form)
    end = datetime.strptime(end,form)
    day = 0

    current = start
    playing = []
    while day < 3:
        current = start + timedelta(days=day)
        print(f'{current.date()}')


        data = wsba.nhl_calculate_stats(pbp.loc[pd.to_datetime(pbp['game_date'])<=current],'team',['5v5','4v4','3v3'],[2,3])
        
        data = add_features(data, playing)

        dfs.append(data)

        playing = pbp.loc[pbp['game_date']==current, 'event_team_abbr'].drop_duplicates().to_list()

        day += 1

    #Place the games in order and create sums for 
    return pd.concat(dfs)

prep_game_data(pd.read_parquet('C:/Users/owenb/OneDrive/Desktop/Owen/WSBA/data/pbp/nhl_pbp_20242025.parquet')).to_csv('test.csv',index=False)
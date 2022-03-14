#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 21:34:55 2021

@author: jak
"""

import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import pickle

test_mode = False

#initialise la date
now = pd.to_datetime("today")
today = now.normalize()
origin = pd.to_datetime("2021-12-04")

# ouvre l'agenda de sommeil sauvegardé 

def log_sleep(df):
    print(df)
    if test_mode == False:
        #demande a quel heure tu t'es levé
        answer = input("when did you wake up:")
        if answer == 'q':
            return df
        else:
            if today not in df.index:
                df = df.append(pd.Series(name = today, dtype = object))
            if answer == '':
                df.loc[today,"time up"] = now.hour
            elif answer != 't':
                df.loc[today,"time up"] = int(answer)
        
        #demande a quel heure tu t'es endormis
        if answer == 'q':
            return df
        else:
            down_time = input("when did you fall asleep ?:")
            if down_time != 't':
                df.loc[today,"time down"] = down_time
                       
        #demande si tu étais fatigué en te reveillant
        if answer == "q":
            return df
        else:
            ans = input("did you wake up tired ? [y/n]")
            if ans != 't':
                if ans == 'y':
                    df.loc[today,"up tired"] = True
                elif ans == 'n':
                    df.loc[today,"up tired"] = False
        #ajoute un commentaire
        comment = input("any comment ? :")
        df.loc[today,"comment"] = comment
        return df
        
def plot_sleep(df, interval = (10,10), goal_time = (4,9)):
    """
    Parameters
    ----------
    df : pd.dataframe
        source of data for the plot
    interval : tuple if centered around today, optional
        days you want to plot before and after today. The default is (8,2).

    Returns
    -------
    None.
    """
    #choisis l'interval et collècte les données pour
    shown_timeframe = pd.date_range((today - pd.DateOffset(interval[0])),(today + pd.DateOffset(interval[1])))
    shown_hours = [df.loc[date,"time up"] if date in df.index else None for date in shown_timeframe]
    
    #plot l'agenda pour l'interval choisis
    day_labels = [ f"{date.day}/{date.month}" for date in shown_timeframe ]
    plt.figure(figsize = (10,6))
    plt.plot( day_labels, shown_hours, "ro")
    plt.plot( day_labels, shown_hours )
    plt.fill_between(day_labels,[goal_time[1]]*len(day_labels),[goal_time[0]]*len(day_labels),alpha = 0.3)
    plt.xlim(0,len(day_labels)-1)
    plt.ylim((0,24))
    plt.yticks(range(25))
    plt.xticks(rotation = 45)
    plt.show()


if __name__ == "__main__":
    try:
        df = pd.read_csv("../../data/agenda_sommeil.csv", index_col = 0)
    except FileNotFoundError:
        df = pd.DataFrame(columns = ["time up","time down","up tired","comment"])
        
    df.index = pd.to_datetime(df.index)
        
    df = df.groupby(df.index).last()
    
    df = log_sleep(df)
            
    plot_sleep(df)
    
    df.to_csv("../../data/agenda_sommeil.csv")


#pour ajouter une ligne manuellement si besoins
"""
line = pd.DataFrame({"time up": 7, "up tired": True,"comment": "","time down" : 4}, index=[pd.to_datetime("2021-12-7")])
df = df.append(line, ignore_index=False)
df = df.sort_index()
pd.to_csv("../../data/agenda_sommeil.csv")
"""






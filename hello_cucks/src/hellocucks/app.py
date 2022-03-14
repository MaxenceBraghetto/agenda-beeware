"""
it prints a nice hello to cucks across the globe
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.images import Image
import pandas as pd
from toga_chart import Chart
import matplotlib.pyplot as plt
import os
import toga_chart
from functools import partial

#from src.hellocucks.supp import plot_supp

today = pd.to_datetime("today").normalize()
def setup_files():
    try:
        df_supp = pd.read_csv("data/supp.csv",index_col = 0)
        df_supp.index = [pd.Timestamp(x) for x in df_supp.index]
    except FileNotFoundError:
        df_supp = pd.DataFrame()
    df_supp = df_supp.fillna(0)
        
    try:
        df_som = pd.read_csv("data/agenda_sommeil.csv")
    except FileNotFoundError:
        df_som = pd.DataFrame(columns = ["time up","time down","up tired","comment"])
        
    try:
        supp_info = pd.read_csv("data/supp_info.csv", index_col = 0)
    except FileNotFoundError:
        supp_info = pd.DataFrame(columns = ["dose","unit"])
        
    try:
        df_sleep = pd.read_csv("data/agenda_sommeil.csv", index_col = 0)
        df_sleep.index = [pd.Timestamp(x) for x in df_sleep.index]
    except FileNotFoundError:
        df_sleep = pd.DataFrame(columns = ['time up', 'up tired', 'comment', 'time down'])
    
    try:
        sleep_info = pd.read_csv("data/sleep_info.csv", index_col = 0)
    except FileNotFoundError:
        sleep_info = pd.DataFrame(columns = ["title"])
        sleep_info["title"] = ['time up', 'up tired', 'comment', 'time down']
        
    return df_supp, df_som, supp_info, df_sleep, sleep_info

df_supp, df_som, supp_info, df_sleep, sleep_info = setup_files()



class hellocucks(toga.App):
    
    def startup(self):
        
        
        global app
        app = self
        
        self.op = toga.OptionContainer()
        
        
        self.op.add("sommeil",sleep_box())
        
        for supp in supp_info.index:            
            self.op.add(supp,panel(supp).main_box)
                               
        self.main_window = toga.MainWindow(title=self.name)
        self.main_window.content = self.op
        self.main_window.show()
        
        
    def add_supp_startup(self, widget):
        main_box = toga.Box(style = Pack(direction = COLUMN))
        
        name_field = toga.Box(children = [toga.Label("Name")])
        self.name_input = toga.TextInput()
        name_field.add(self.name_input)
        
        dose_field = toga.Box( children = [toga.Label("Dose")])
        self.dose_input = toga.NumberInput(default = 0)
        dose_field.add(self.dose_input)        
        
        unit_field = toga.Box(children = [toga.Label("unit")])
        self.unit_input = toga.TextInput(initial = "mg")
        unit_field.add(self.unit_input)
        
        self.save_button = toga.Button("Entrer", style = Pack(flex = 1, height = 100),
            on_press = partial(new_supp,app = self))
        
        #ajoute a la df info et la df supp
        main_box.add(name_field,dose_field,unit_field)
        main_box.add(self.save_button)
        
        self.add_supp_window = toga.Window(title='add supplement', size = (200,150))
        self.add_supp_window.content = main_box
        self.windows.add(self.add_supp_window)
        self.add_supp_window.show()
        
        

        
class panel():
    def __init__(self,supp):
        self.supp = supp
        self.main_box = toga.Box(style = Pack(direction = COLUMN))  
        
        log_bar = toga.Box(style = Pack(flex=0.2,padding_right = 100)) 
        log_bar.add(toga.Label("log:",style = Pack(padding = (0,10))))
        self.log_field = toga.TextInput(style = Pack(flex = 0.1),initial = self.get_today_dose())
        log_bar.add(self.log_field)
        log_bar.add(toga.Label("mg",style = Pack(padding = (0,10))))
        log_bar.add(toga.Button("ok",style = Pack(padding = (0,3)),
                                on_press = self.log_dose ))
        
        
        top_bar = toga.Box(style = Pack(), children = [
            log_bar,
            toga.Button("+ new", style = Pack(flex = 0.1,width = 90),on_press=app.add_supp_startup)] )
        
        self.main_box.add(top_bar)
       
        self.chart = toga_chart.Chart(style=Pack(), on_draw=partial(plot_supp,supp=supp))
        self.main_box.add(self.chart)
        
    def log_dose(self,widget):
        if today not in df_supp.index:
            df_supp.loc[today] = None
        
        #save new values
        df_supp.loc[today,self.supp] = int(self.log_field.value)
        df_supp.to_csv("data/supp.csv")
        
        #update chart
        self.chart._resize()
        
    def get_today_dose(self):
        try:
            x = df_supp.loc[today][self.supp]
        except KeyError:
            x = 0
        return int(x)
        
        
        
def new_supp(widget,app):

    name,dose,unit = app.name_input.value, app.dose_input.value, app.unit_input.value
    if name != '':
        if name not in supp_info.index :
            supp_info.loc[name] = {"dose": dose, "unit" : unit}
        if name not in df_supp.columns:
            df_supp[name] = 0   
    supp_info.to_csv("data/supp_info.csv")
    df_supp.to_csv("data/supp.csv")
    app.op.add(name, panel(name).main_box)
    app.add_supp_window.close()

    


def plot_supp(chart, figure,supp,timeframe = None):
    
    print(f"===plt_supp===: supp = {supp}")
    if timeframe == None: #la timeframe est le mois en cours par défaut
        timeframe = pd.date_range(today.replace(day=1),today.replace(day = today.days_in_month))
    day_labels = [ f"{date.day}/{date.month}" for date in timeframe ] 
    tf_supp = df_supp.loc[timeframe[0] : timeframe[-1]].copy()
    
    #fill values for missing days
    for date in timeframe:
        if date not in tf_supp.index:
            tf_supp.loc[date] = 0
    tf_supp.sort_index(inplace = True)
    
    supp_sums = [sum(tf_supp[supp][:i]) for i in range(1,len(tf_supp[supp])+1)]
    
    
    ax = figure.add_subplot(1,1,1)
    #dose dans la timeframe
    ax.fill_between(day_labels[:today.day],supp_sums[:today.day], color = "grey", alpha = 0.4)
    
    #ligne d'objectif
    daily_objective = supp_info.loc[supp,"dose"]
    ax.plot(day_labels,[x*daily_objective for x in range(1,len(day_labels)+1)], color="grey",label = "zinc")
    
    ax.set_xlim(0,len(day_labels)-1)
    ax.set_xticklabels(day_labels,rotation = 45, ha = "right")
    ax.set_ylim(0)
    ax.set_title(supp)
    
    figure.tight_layout()
    
class input_field(toga.Box):
    def __init__(self, title, style = Pack(direction = COLUMN,padding = (10,0,10,2),flex = 1)):
        super().__init__(self,style = Pack(direction = COLUMN, padding = (10,0,10,2),flex = 1))
        self.title = toga.Label(title)
        self.add(self.title)
        self.entry = toga.TextInput()
        self.add(self.entry)
        

#/////////sleep/////////#

class sleep_box(toga.Box):
    print(sleep_info)
    fields = [input_field(**dict(args)) for _,args in sleep_info.iterrows()]
    def __init__(self, style = Pack(direction = ROW)):       
        super().__init__(self,style = Pack(direction = ROW))
        self.sleep_chart = toga_chart.Chart(style=Pack(flex = 1), on_draw=self.plot_sleep)
        self.add(self.sleep_chart)
        
        info_col = toga.Box(style = Pack(direction = COLUMN,width = 100), children = [
            toga.Button("save" ,style = Pack(),on_press=self.log_sleep)])
        
        print(self.fields,sleep_info,"<===========")
        
        for field in self.fields:
            info_col.add(field)
        
        self.add(info_col)
    

    def log_sleep(self,caller):
        if today not in df_sleep.index:
            df_sleep.loc[today] = None
            
        for field in self.fields:
            df_sleep.loc[today,field.title.text] = field.entry.value

        df_sleep.to_csv("data/agenda_sommeil.csv")
        self.sleep_chart._resize()
    
    def plot_sleep(self, Chart, figure, interval = (10,10), goal_time = (4,9)):
        print(locals())

        #choisis l'interval et collècte les données pour
        shown_timeframe = pd.date_range((today - pd.DateOffset(interval[0])),(today + pd.DateOffset(interval[1])))
        shown_up_hours = [df_sleep.loc[date,"time up"] if date in df_sleep.index else None for date in shown_timeframe]
        shown_down_hours = [df_sleep.loc[date,"time down"] if date in df_sleep.index else None for date in shown_timeframe]
        
        #plot l'agenda pour l'interval 
        ax = figure.add_subplot(1,1,1)
        day_labels = [ f"{date.day}/{date.month}" for date in shown_timeframe ]
        #levé
        ax.plot( day_labels, shown_up_hours, "ro")
        ax.plot( day_labels, shown_up_hours )
        #couché
        ax.plot( day_labels, shown_down_hours, "ro",color = "Blue")
        ax.plot( day_labels, shown_down_hours )
        
        ax.fill_between(day_labels,[goal_time[1]]*len(day_labels),[goal_time[0]]*len(day_labels),alpha = 0.3)
        ax.set_xlim(0,len(day_labels)-1)
        ax.set_ylim((0,24))
        ax.set_yticks(range(25))
        ax.set_xticklabels(day_labels,rotation = 45)
        print(df_sleep)
        
    


def main():
    return hellocucks('Chart', 'org.pybee.widgets.chart')

if __name__ == '__main__':
    main().main_loop()


import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd

from Model import TeamData

from functools import partial

font1 = {'font': ('Monospace', 20)}
font2 = {'font': ('Monospace', 15)}


class Home(tk.Tk):

    def __init__(self, data: TeamData):
        super().__init__()
        self.data = data
        self.all_pages = [StatisticPage,
                          TeamPage,
                          RelationshipPage,
                          StoryPage]
        self.all_pages_name = [x(data).name for x in self.all_pages]
        self.current_page = RelationshipPage
        self.init_components()

    def init_components(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        unit_menu = tk.Menu(menubar)

        unit_menu.add_separator()

        for index, name in enumerate(self.all_pages_name):
            unit_menu.add_command(
                label=name,
                command=partial(self.change_page, self.all_pages[index])
            )

        unit_menu.add_command(
            label='Exit',
            command=self.destroy,
        )

        menubar.add_cascade(
            label="Units",
            menu=unit_menu,
            underline=0
        )

        self.display_page = self.current_page(self.data)
        self.display_page.pack(side=tk.TOP)

    def change_page(self, page):
        self.current_page = page
        plt.close()
        self.display_page.destroy()
        self.display_page = self.current_page(self.data)
        self.display_page.pack(side=tk.TOP)

    def run(self):
        self.mainloop()


class StatisticPage(tk.Frame):

    def __init__(self, data: TeamData):
        super().__init__()
        self.name = "Stats"
        self.data = data
        self.init_components()

    def init_components(self):
        self.label = tk.Label(self, text="Top 10 " + self.name, **font1,
                              pady=10)
        self.label.pack(side=tk.TOP, anchor=tk.CENTER)
        self.selected_stat = tk.StringVar()
        self.cbb_frame = tk.Frame(self, pady=10)
        self.cbb_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        self.stat_chooser = self.create_stats_cbb(self.cbb_frame)
        self.stat_chooser.pack(side=tk.TOP, anchor=tk.CENTER)
        self.load_units()

        self.canvas = None
        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        self.mean = tk.StringVar()
        self.SD = tk.StringVar()
        self.mean_label = tk.Label(self, textvariable=self.mean, **font2,
                                   pady=10)
        self.mean_label.pack(side=tk.TOP, anchor=tk.CENTER)
        self.SD_label = tk.Label(self, textvariable=self.SD, **font2,
                                 pady=10)
        self.SD_label.pack(side=tk.TOP, anchor=tk.CENTER)
        self.cbb_handler(None)

    def create_stats_cbb(self, frame):
        stat_chooser = ttk.Combobox(frame,
                                    textvariable=self.selected_stat,
                                    width=15,
                                    **font1)
        stat_chooser.bind("<<ComboboxSelected>>", self.cbb_handler)
        return stat_chooser

    def cbb_handler(self, event):
        stat = self.selected_stat.get()

        fig, ax = plt.subplots(2, figsize=(10, 7))
        fig.subplots_adjust(hspace=0.5)

        new_df = self.data.sort_df(stat)
        sns.barplot(new_df, x='team', y=stat, ax=ax[0])
        ax[0].set_title("Team " + stat)
        sns.histplot(new_df, x=stat, ax=ax[1])
        ax[1].set_title(stat.capitalize() + " Histogram")

        self.mean.set("Mean: " + str(f"{new_df[stat].mean():.2f}"))
        self.SD.set("SD: " + str(f"{new_df[stat].std():.2f}"))

        if self.canvas:
            plt.close()
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.CENTER)

    def load_units(self):
        """Load stats into the comboboxes and set default value"""
        units = self.data.option_column
        self.stat_chooser['values'] = units
        self.stat_chooser.current(newindex=0)


class TeamPage(tk.Frame):
    def __init__(self, data: TeamData):
        super().__init__()
        self.name = "Team"
        self.data = data
        self.init_components()

    def init_components(self):
        self.label = tk.Label(self, text=self.name, **font1,
                              pady=10)
        self.label.pack(side=tk.TOP, anchor=tk.CENTER)

        self.selected_team = tk.StringVar()
        self.cbb_frame = tk.Frame(self, pady=10)
        self.cbb_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        self.team_chooser = self.create_cbb(self.cbb_frame)
        self.team_chooser.pack(side=tk.TOP, anchor=tk.CENTER)
        self.load_units()

        self.canvas = None
        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        self.cbb_handler(None)

    def create_cbb(self, frame):
        team_chooser = ttk.Combobox(frame,
                                    textvariable=self.selected_team,
                                    width=15,
                                    **font1)
        team_chooser.bind("<<ComboboxSelected>>", self.cbb_handler)
        return team_chooser

    def load_units(self):
        unit = list(self.data.df['team'])
        self.team_chooser['values'] = unit
        self.team_chooser.current(newindex=0)

    def cbb_handler(self, event):
        fig, ax = plt.subplots(figsize=(15, 7))
        df = self.data.df.copy()
        df = df[df['team'] == self.selected_team.get()]
        df.drop(columns=['team'], inplace=True)
        df = df.loc[:, self.data.team_column]

        x = self.data.team_column
        y = df.iloc[0].tolist()

        ax.barh(x, y)

        if self.canvas:
            plt.close()
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.CENTER)


class RelationshipPage(tk.Frame):
    def __init__(self, data: TeamData):
        super().__init__()
        self.name = "Relationship"
        self.data = data
        self.init_components()

    def init_components(self):
        self.label = tk.Label(self, text=self.name, **font1,
                              pady=10)
        self.label.pack(side=tk.TOP, anchor=tk.CENTER)

        self.stat1 = tk.StringVar()
        self.stat2 = tk.StringVar()
        self.cbb_frame = tk.Frame(self, pady=10)
        self.cbb_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        self.stat_chooser1, self.stat_chooser2 = self.create_cbb(self.cbb_frame
                                                                 )

        self.label1 = tk.Label(self.cbb_frame, text='Between', **font1)
        self.label2 = tk.Label(self.cbb_frame, text='and', **font1)
        self.label1.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.stat_chooser1.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.label2.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.stat_chooser2.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.load_units()

        self.canvas = None
        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(side=tk.TOP, anchor=tk.CENTER)

        self.corr = tk.StringVar()
        self.corr_label = tk.Label(self, textvariable=self.corr, **font2,
                                   pady=10)
        self.corr_label.pack(side=tk.TOP, anchor=tk.CENTER)

        self.cbb_handler(None)

    def create_cbb(self, frame):
        stat_chooser1 = ttk.Combobox(frame,
                                     textvariable=self.stat1,
                                     width=15,
                                     **font1)
        stat_chooser1.bind("<<ComboboxSelected>>", self.cbb_handler)
        stat_chooser2 = ttk.Combobox(frame,
                                     textvariable=self.stat2,
                                     width=15,
                                     **font1)
        stat_chooser2.bind("<<ComboboxSelected>>", self.cbb_handler)

        return stat_chooser1, stat_chooser2

    def load_units(self):
        unit = self.data.option_column
        self.stat_chooser1['values'] = unit
        self.stat_chooser1.current(newindex=0)
        self.stat_chooser2['values'] = unit
        self.stat_chooser2.current(newindex=2)

    def cbb_handler(self, event):
        fig, ax = plt.subplots(figsize=(15, 7))
        df = self.data.df.copy()
        stat1 = self.stat1.get()
        stat2 = self.stat2.get()

        sns.scatterplot(df, x=stat1, y=stat2)

        corr = f"{df[stat1].corr(df[stat2]):.2f}"
        self.corr.set("Correlation Coefficient: " + corr)

        if self.canvas:
            plt.close()
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.CENTER)


class StoryPage(tk.Frame):
    def __init__(self, data: TeamData):
        super().__init__()
        self.name = "Story"
        self.data = data
        self.init_components()

    def init_components(self):
        self.label = tk.Label(self, text=self.name, **font1,
                              pady=10)
        self.label.pack(side=tk.TOP, anchor=tk.CENTER)
        self.label1 = tk.Label(self, text="More shots lead to more goals",
                               **font1)
        self.label1.pack(side=tk.TOP, anchor=tk.CENTER)

        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        self.canvas = None

        self.corr = tk.StringVar()
        self.corr_label = tk.Label(self, textvariable=self.corr, **font2,
                                   pady=10)
        self.corr_label.pack(side=tk.TOP, anchor=tk.CENTER)

        self.create_graph()

    def create_graph(self):
        fig, ax = plt.subplots(figsize=(15, 7))
        df = self.data.df.copy()

        sns.scatterplot(df, x='shots', y='goals')

        corr = f"{df['shots'].corr(df['goals']):.2f}"
        self.corr.set("Correlation Coefficient: " + corr)

        if self.canvas:
            plt.close()
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.CENTER)

import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sys
import os

directory = "Data/team_data.csv"


class TeamData:
    df = pd.read_csv(directory)
    df = df.copy()

    used_column = ['team',
                   'possession',
                   'minutes_90s',
                   'goals',
                   'assists',
                   'goals_per90',
                   'assists_per90',
                   'cards_yellow',
                   'cards_red',
                   'gk_saves',
                   'gk_save_pct',
                   'shots',
                   'shots_per90',
                   ]

    option_column = used_column.copy()
    option_column.remove('team')

    team_column = option_column.copy()
    for name in ['shots', 'gk_save_pct', 'possession']:
        team_column.remove(name)

    df = df[used_column]

    @classmethod
    def sort_df(cls, stat):
        """
        :param stat: the statistic you want to sort
        :return: return the top 10, or you can change it.
        """
        new_df = cls.df.copy()
        new_df = new_df[['team', stat]].sort_values(by=stat,
                                                    ascending=False)  # sort from biggest
        return new_df.head(10)

    @classmethod
    def get_goal_data(cls):
        new_df = cls.df.copy()
        new_df['goals'] = new_df['goals'].astype(str)
        grange = ['low', 'moderate', 'high']
        goals = [0, 0, 0]
        for index, goal in enumerate(new_df['goals']):
            goal = int(goal)
            if goal < 5:
                goals[0] += 1
            elif goal < 10:
                goals[1] += 1
            elif goal >= 10:
                goals[2] += 1

        return grange, goals


if __name__ == "__main__":
    T1 = TeamData()
    T1.sort_df('possession')
    T1.get_goal_pie_graph()

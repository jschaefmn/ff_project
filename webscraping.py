from sys import argv
import requests
from requests import get
import pandas as pd
from bs4 import BeautifulSoup

year = input("Enter the year you want to import between 1999 and 2023: ")
week = input("Enter the week you want to import between 1 and 18: ".format(year))

year, week = int(year), int(week)

passingURL = "https://stathead.com/football/player-game-finder.cgi?request=1&match=player_game&order_by=pass_rating&year_min={year}&year_max={year}&week_num_season_min={week}&week_num_season_max={week}&ccomp%5B2%5D=gt&cval%5B2%5D=1&cstat%5B2%5D=pass_att&__hstc=223721476.7e1f8937de3348a263d945b543ec4621.1723505930753.1723520451313.1723564611358.3&__hssc=223721476.9.1723564611358&__hsfp=3149345536&_gl=1*5fzxlt*_ga*NTM4NTI1ODQxLjE3MjM1MDU5MzE.*_ga_80FRT7VJ60*MTcyMzU2NDQ0NC4zLjEuMTcyMzU2NTQzNS4wLjAuMA..".format(year=year, week=week)

receivingURL = "https://stathead.com/football/player-game-finder.cgi?request=1&match=player_game&order_by=rec_yds&year_min={year}&year_max={year}&week_num_season_min={week}&week_num_season_max={year}&ccomp%5B2%5D=gt&cval%5B2%5D=1&cstat%5B2%5D=targets&__hstc=223721476.7e1f8937de3348a263d945b543ec4621.1723505930753.1723520451313.1723564611358.3&__hssc=223721476.12.1723564611358&__hsfp=3149345536&_gl=1*1399x67*_ga*NTM4NTI1ODQxLjE3MjM1MDU5MzE.*_ga_80FRT7VJ60*MTcyMzU2NDQ0NC4zLjEuMTcyMzU2NTcxOS4wLjAuMA.."

rushingURL = "https://stathead.com/football/player-game-finder.cgi?request=1&match=player_game&order_by=rush_yds&year_min={year}&year_max={year}&week_num_season_min={week}&week_num_season_max={week}&ccomp%5B2%5D=gt&cval%5B2%5D=1&cstat%5B2%5D=rush_att&__hstc=223721476.7e1f8937de3348a263d945b543ec4621.1723505930753.1723520451313.1723564611358.3&__hssc=223721476.12.1723564611358&__hsfp=3149345536&_gl=1*1ol2bb7*_ga*NTM4NTI1ODQxLjE3MjM1MDU5MzE.*_ga_80FRT7VJ60*MTcyMzU2NDQ0NC4zLjEuMTcyMzU2NTcyMi4wLjAuMA.."

urls = {
  'Passing': passingURL,
  'Receiving': receivingURL,
  'Rushing': rushingURL
}

dfs = []

defColumnSettings = {
  'axis': 1,
  'inplace': True
}

for key, url in urls.items():
    response = get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # tables = pd.read_html(str('table'))
    # df = tables[0]
    table = soup.find('table', {'id': 'stats'})
    df = pd.read_html(str(table))[0]
    print(df)

    df.columns = df.columns.droplevel(level = 0)

    df.drop(['Result', 'Week', 'G#', 'Opp', 'Unnamed: 10_level_1', 'Age', 'Rk', 'Lg', 'Date', 'Day'], **defColumnSettings)

    df = df[df['Pos.'] != 'Pos.']

    df.set_index(['Player', 'Pos.', 'Team'], inplace=True)

    if key == 'Passing':
        df = df[['Yds', 'TD', 'Int', 'Att', 'Cmp']]
        df.rename({'Yds': 'PassingYds', 'Att': 'PassingAtt', 'Y/A': 'Y/PassingAtt', 'TD': 'PassingTD'}, **defColumnSettings)
    elif key =='Receiving':
        df = df[['Rec', 'Tgt', 'Yds', 'TD']]
        df.rename({'Yds': 'ReceivingYds', 'TD': 'ReceivingTD'}, **defColumnSettings)
    elif key == 'Rushing':
        df.drop('Y/A', **defColumnSettings)
        df.rename({'Att': 'RushingAtt', 'Yds': 'RushingYds', 'TD': 'RushingTD'}, **defColumnSettings)
    dfs.append(df)


df = dfs[0].join(dfs[1:], how='outer')
df.fillna(0, inplace=True)
df = df.astype('int64')

df['FantPoints'] = df['PassYds']/25 + df['PassTD']*4 - df['Int']*2 + df['Rec'] + df['RecYds']/10 + df['RecTD']*6 + df['RushYds']/10 + df['RushTD']*6

df.reset_index(inplace=True)

try:
    if argv[1] == '--save':
        df.to_csv('datasets/season{}week{}.csv'.format(year, week))
except IndexError:
    pass
from sys import argv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from requests import get
import pandas as pd
from bs4 import BeautifulSoup
from functools import reduce

# set up webdriver & go to website's login page
driver = webdriver.Chrome()
driver.get("https://stathead.com/users/login.cgi")

try:
  # enter email & password
  
  username = driver.find_element(By.XPATH, '//*[@id="username"]')
  password = driver.find_element(By.XPATH, '//*[@id="password"]')
  username.send_keys('')
  password.send_keys('')
  
  # submit login form
  login_button = driver.find_element(By.XPATH, '//*[@id="sh-login-button"]')
  login_button.click()
  
  print('Log in successful')

except:
  print("Log in failed")

time.sleep(2) # wait for page transition

year = input("Enter the year you want to import between 1999 and 2023: ")
week = input("Enter the week you want to import between 1 and 18: ".format(year))

year, week = int(year), int(week)

passingURL = "https://stathead.com/football/player-game-finder.cgi?request=1&match=player_game&order_by=pass_rating&year_min={year}&year_max={year}&week_num_season_min={week}&week_num_season_max={week}&ccomp%5B2%5D=gt&cval%5B2%5D=1&cstat%5B2%5D=pass_att&__hstc=223721476.7e1f8937de3348a263d945b543ec4621.1723505930753.1723520451313.1723564611358.3&__hssc=223721476.9.1723564611358&__hsfp=3149345536&_gl=1*5fzxlt*_ga*NTM4NTI1ODQxLjE3MjM1MDU5MzE.*_ga_80FRT7VJ60*MTcyMzU2NDQ0NC4zLjEuMTcyMzU2NTQzNS4wLjAuMA..".format(year=year, week=week)

receivingURL = "https://stathead.com/football/player-game-finder.cgi?request=1&match=player_game&order_by=rec_yds&year_min={year}&year_max={year}&week_num_season_min={week}&week_num_season_max={week}&ccomp%5B2%5D=gt&cval%5B2%5D=1&cstat%5B2%5D=targets&__hstc=223721476.7e1f8937de3348a263d945b543ec4621.1723505930753.1723520451313.1723564611358.3&__hssc=223721476.12.1723564611358&__hsfp=3149345536&_gl=1*1399x67*_ga*NTM4NTI1ODQxLjE3MjM1MDU5MzE.*_ga_80FRT7VJ60*MTcyMzU2NDQ0NC4zLjEuMTcyMzU2NTcxOS4wLjAuMA..".format(year=year, week=week)

rushingURL = "https://stathead.com/football/player-game-finder.cgi?request=1&match=player_game&order_by=rush_yds&year_min={year}&year_max={year}&week_num_season_min={week}&week_num_season_max={week}&ccomp%5B2%5D=gt&cval%5B2%5D=1&cstat%5B2%5D=rush_att&__hstc=223721476.7e1f8937de3348a263d945b543ec4621.1723505930753.1723520451313.1723564611358.3&__hssc=223721476.12.1723564611358&__hsfp=3149345536&_gl=1*1ol2bb7*_ga*NTM4NTI1ODQxLjE3MjM1MDU5MzE.*_ga_80FRT7VJ60*MTcyMzU2NDQ0NC4zLjEuMTcyMzU2NTcyMi4wLjAuMA..".format(year=year, week=week)

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
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # tables = pd.read_html(str('table'))
    # df = tables[0]
    table = soup.find('table', {'id': 'stats'})
    df = pd.read_html(str(table))[0]
    df.columns = df.columns.droplevel(level = 0)
    
    df.drop(['Result', 'Week', 'G#', 'Opp', 'Unnamed: 10_level_1', 'Age', 'Rk', 'Date', 'Day'], **defColumnSettings)

    df = df[df['Pos.'] != 'Pos.']
    df = df[df != key]
    print(df)
    df.set_index(['Player', 'Pos.', 'Team'], inplace=True)
    print(df)
    if key == 'Passing':
        df = df[['Yds', 'TD', 'Int', 'Att', 'Cmp']]
        df.rename({'Yds': 'PassYds', 'Att': 'PassAtt', 'Y/A': 'Y/PassAtt', 'TD': 'PassTD'}, **defColumnSettings)
    elif key =='Receiving':
        df = df[['Rec', 'Tgt', 'Yds', 'TD']]
        df.rename({'Yds': 'RecYds', 'TD': 'RecTD'}, **defColumnSettings)
    elif key == 'Rushing':
        df.drop(['Att.1', 'Yds.1', '1D', 'Succ%', 'Y/A'], **defColumnSettings)
        df.rename({'Att': 'RushAtt', 'Yds': 'RushYds', 'TD': 'RushTD'}, **defColumnSettings)
    df.to_csv('datasets/{key}.csv'.format(key=key))
    dfs.append(df)


df = dfs[0].join(dfs[1:], how='outer')
# merged_df = dfs[0]

# for df in dfs[1:]:
#     merged_df = merged_df.merge(df, on=['Player', 'Team'], how='outer')

# Remove duplicates if necessary
# merged_df.drop_duplicates(subset=['Player', 'Team'], keep='first', inplace=True)
#df = reduce(lambda left, right: pd.merge(left, right, left_index= True, right_index = True, how='outer'), dfs)
df.fillna(0, inplace=True)
df.to_csv('datasets/season{}week{}.csv'.format(year, week))
df = df.astype('int64')

df['FantPoints'] = df['PassYds']/25 + df['PassTD']*4 - df['Int']*2 + df['Rec'] + df['RecYds']/10 + df['RecTD']*6 + df['RushYds']/10 + df['RushTD']*6

df.reset_index(inplace=True)

try:
    if argv[1] == '--save':
        df.to_csv('datasets/season{}week{}.csv'.format(year, week))
except IndexError:
    pass
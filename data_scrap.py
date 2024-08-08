import requests
from bs4 import BeautifulSoup
import pandas as pd

# scrape data from nextgenstats
url = "https://nextgenstats.nfl.com/stats/passing"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# parse HTML to find passing data
data = []
for row in soup.find_all('tr'):
  cols = row.find_all('td')
  data.append([col.text for col in cols])
  
# convert to DataFrame
df = pd.DataFrame(data, columns=['PLAYER NAME', 'TEAM', 'TT', 'CAY', 'IAY', 'AYD', 'AGG%', 'LCAD', 'AYTS', 'ATT', 'YDS', 'TD', 'INT', 'RATE', 'COMP%', 'xCOMP%'])
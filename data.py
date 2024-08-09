import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
  
def main():
  positions = ['QB', 'RB', 'WR', 'TE']
  merged_data = {}
  
  for position in positions:
    merged_data[position] = load_and_merge_data(position)
    
    
  print(merged_data)

# have advanced stats, but didn't include the points,TDs, and INTs, so had to download the points separately and merge them
def load_and_merge_data(position):
  # Load data from CSV files
  df1 = pd.read_csv(f'data/{position}_Stats.csv')
  df2 = pd.read_csv(f'data/{position}_Points.csv')
  
  # keep relevant data from df2
  if position == 'QB':
    df2_relevant = df2[['Player', 'TD', 'INT', 'FPTS', 'FPTS/G']]
  else:
    df2_relevant = df2[['Player', 'Y/R', 'TD', 'FPTS', 'FPTS/G']]
  
  # Merge the two DataFrames
  merged_data = pd.merge(df1, df2_relevant, on='Player', how='left')
  
  return merged_data



if __name__ == "__main__":
  main()

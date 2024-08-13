import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import glob
  
data_files = glob.glob('data/*.csv')
df = pd.concat([pd.read_csv(f) for f in data_files])





# if __name__ == "__main__":
#   main()

import pandas as pd
from datetime import datetime, timedelta



goldenCross = pd.read_csv("Data/golden_cross_results.csv")
dropCross = pd.read_csv("Data/drop_cross_results.csv")


def combine_values(column):
    return column if len(set(column)) == 1 else list(set(column))

goldenCross = goldenCross.groupby(goldenCross.columns[0]).agg(lambda x: combine_values(x)).reset_index()
dropCross = dropCross.groupby(dropCross.columns[0]).agg(lambda x: combine_values(x)).reset_index()
crossDates = pd.merge(goldenCross, dropCross, on='Company Name', how='outer')

date = datetime.now().date()
date_string = date.strftime("%Y_%m_%d")

crossDates.to_csv('Data/MA Cross results on '+date_string+'.csv', index=False)



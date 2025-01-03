import pandas as pd
from datetime import datetime, timedelta



goldenCross = pd.read_csv("Data/golden_cross_results.csv")
dropCross = pd.read_csv("Data/drop_cross_results.csv")


def combine_values(column):
    return column if len(set(column)) == 1 else list(set(column))

goldenCross = goldenCross.groupby(goldenCross.columns[0]).agg(lambda x: combine_values(x)).reset_index()
dropCross = dropCross.groupby(dropCross.columns[0]).agg(lambda x: combine_values(x)).reset_index()
crossDates = pd.merge(goldenCross, dropCross, on='Company Name', how='outer')

duplicate_columns = crossDates.columns[crossDates.columns.duplicated(keep=False)].unique()

for col in duplicate_columns:
    same_cols = crossDates.loc[:, crossDates.columns == col]
    crossDates[col] = same_cols.bfill(axis=1).iloc[:, 0]

    crossDates = crossDates.drop(columns=same_cols.columns.difference([col]))

date = datetime.now().date()
date_string = date.strftime("%Y_%m_%d")

crossDates.to_csv('Data/MA Cross results on '+date_string+'.csv', index=False)



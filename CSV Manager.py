import pandas as pd
from datetime import datetime

def safe_read_csv(path, columns=None):
    try:
        df = pd.read_csv(path)
        # If file exists but has 0 bytes or no header, pandas raises EmptyDataError before here.
        # If it has header but no rows, df.empty is True – that’s OK.
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=columns or [])

def combine_values(column):
    unique_vals = column.dropna().unique()
    if len(unique_vals) == 0:
        return None
    elif len(unique_vals) == 1:
        return unique_vals[0]
    else:
        return ', '.join(map(str, unique_vals))

# Expected columns (adjust if your upstream scripts differ)
golden_cols = ['Ticker', 'Company Name', 'Market Cap (crores)', 'Share Price (rupees)', 'Golden Cross Date']
drop_cols   = ['Ticker', 'Company Name', 'Market Cap (crores)', 'Share Price (rupees)', 'Drop Cross Date']

goldenCross = safe_read_csv("Data/golden_cross_results.csv", columns=golden_cols)
dropCross   = safe_read_csv("Data/drop_cross_results.csv", columns=drop_cols)

# If both empty, write an empty output with headers and exit gracefully
if goldenCross.empty and dropCross.empty:
    date_string = pd.Timestamp.now().strftime("%Y_%m_%d")
    pd.DataFrame(columns=['Company Name', 'Ticker', 'Market Cap (crores)', 'Share Price (rupees)', 'Golden Cross Date', 'Drop Cross Date']) \
      .to_csv(f'Data/Results/MA Cross results on {date_string}.csv', index=False)
    print("No crosses today. Wrote empty results CSV with headers.")
    raise SystemExit(0)

# Group by first column (Company Name field) after ensuring it exists
for df in (goldenCross, dropCross):
    # Backfill missing Company Name if needed
    if 'Company Name' not in df.columns and len(df.columns) > 0:
        df.rename(columns={df.columns[0]: 'Company Name'}, inplace=True)

goldenCross = goldenCross.groupby('Company Name', as_index=False).agg(lambda x: combine_values(x))
dropCross   = dropCross.groupby('Company Name', as_index=False).agg(lambda x: combine_values(x))

crossDates = pd.merge(goldenCross, dropCross, on='Company Name', how='outer')

# Resolve duplicate columns (same header coming from both sides)
duplicate_columns = crossDates.columns[crossDates.columns.duplicated(keep=False)].unique()
for col in duplicate_columns:
    same_cols = crossDates.loc[:, crossDates.columns == col]
    crossDates[col] = same_cols.bfill(axis=1).iloc[:, 0]
    crossDates = crossDates.drop(columns=same_cols.columns.difference([col]))

date_string = pd.Timestamp.now().strftime("%Y_%m_%d")
crossDates.to_csv(f'Data/Results/MA Cross results on {date_string}.csv', index=False)
print("Wrote merged results:", crossDates.shape)
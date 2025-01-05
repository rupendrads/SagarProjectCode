import pandas as pd
fut = pd.read_csv('nfo.csv', low_memory=False)
index_futures = fut[(fut.Series == 'FUTIDX')]
index_futures = fut[(fut.Series == 'FUTIDX') & (fut["Name"].isin(["NIFTY", "BANKNIFTY"]))]
index_futures = index_futures.sort_values(by='ContractExpiration')


index_futures = index_futures.head(2)
print(index_futures)
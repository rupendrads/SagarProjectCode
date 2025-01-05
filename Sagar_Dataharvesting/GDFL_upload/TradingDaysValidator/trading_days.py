import datetime
from holidays import holidays

def generate_trading_days(holidays):
    trading_days_by_year = {}
    
    holidays = {datetime.datetime.strptime(date, "%d-%m-%Y").date(): reason for date, reason in holidays.items()}
    
    years = set(date.year for date in holidays.keys())
    
    for year in sorted(years):
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        all_days = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        trading_days = [day for day in all_days if day.weekday() < 5 and day not in holidays]
        trading_days_by_year[year] = trading_days
    
    return trading_days_by_year

trading_days_by_year = generate_trading_days(holidays)

for year, trading_days in trading_days_by_year.items():
    filename = f"trading_days_{year}.py"
    with open(filename, "w") as file:
        file.write(f"trading_days_{year} = [\n")
        for day in trading_days:
            file.write(f"    '{day}',\n")
        file.write("]\n")
    print(f"Trading days have been saved to files trading_days_{year}.py.")

import pandas_market_calendars as mcal

from datetime import date

# Create the NSE calendar
nse_calendar = mcal.get_calendar('XNSE')

# Define the day you want to check (e.g., today)
today = date.today()

def marketCheck() -> bool:
    schedule = nse_calendar.schedule(start_date=today, end_date=today, tz='Asia/Kolkata')
    return nse_calendar.is_open_now(schedule)

def mTodayCheck() -> bool:

    # Check if today is a valid trading day
    is_trading_day = nse_calendar.valid_days(start_date=today, end_date=today, tz='Asia/Kolkata')

    mflag = False

    if not is_trading_day.empty:
        mflag = True

    return mflag

def mliveduration() -> int:

    mflag = mTodayCheck()
    diff_time = 0

    if mflag:
        schedule = nse_calendar.schedule(start_date=today, end_date=today, tz='Asia/Kolkata')
        open_time = schedule.iloc[0]['market_open']
        close_time = schedule.iloc[0]['market_close']
        diff_time = int((close_time - open_time).total_seconds())

    return diff_time
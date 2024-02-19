from datetime import datetime, timedelta
import pytz
import holidays

def generate_dates(
    num_days: int,
    exclude_weekends: bool,
    timezone: str,
    country_code: str
    ) -> list:
    """
    Generates a list of dates from the current date.

    :param num_days: Number of dates to generate.
    :param exclude_weekends: Exclude weekends if True.
    :param timezone: Time zone for date generation.
    :param country_code: Country code for public holidays (Optional).
    :return: List of formatted date strings.
    """
    dates: list = []
    
    current_date = datetime.now(pytz.timezone(timezone))

    while len(dates) < int(num_days):
        if exclude_weekends and current_date.weekday() >= 5:  # Skip weekends (5 and 6 corresponds to Saturday-Sunday)
            current_date += timedelta(days=1) # Add one day to the current date
            continue

        # Check for public holidays (optional)
        if country_code and current_date in holidays.CountryHoliday(country_code):  # Skip public holidays
            current_date += timedelta(days=1)
            continue
        
        formatted_date = current_date.strftime('%Y-%m-%d (%a)') # Format the date as 'YYYY-MM-DD (Day)'

        dates.append(formatted_date) # Add the formatted date to the list of dates

        current_date += timedelta(days=1) # Add one day to the current date

        # Output the list of dates: ['2022-10-10 (Mon)', '2022-10-11 (Tue)', '2022-10-12 (Wed)', '2022-10-13 (Thu)', '2022-10-14 (Fri)']

    return dates
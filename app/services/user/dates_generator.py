from datetime import datetime, timedelta
import pytz
import holidays

async def generate_dates(
    num_days: int | None = 5,
    exclude_weekends: bool | None = True,
    timezone: str | None = 'Europe/Moscow',
    country_code: str | None = 'RU',
    date_format: str | None = '%d.%m.%Y (%a)'
    ) -> list:
    """
    Generates a list of dates from the current date.

    :param num_days: Number of dates to generate.
    :param exclude_weekends: Exclude weekends if True.
    :param timezone: Time zone for date generation.
    :param country_code: Country code for public holidays (Optional).
    :param date_format: Date format for the generated dates.
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
        
        formatted_date = current_date.strftime(date_format) # Format the date as 'YYYY-MM-DD (Day)'

        dates.append(formatted_date) # Add the formatted date to the list of dates

        current_date += timedelta(days=1) # Add one day to the current date

    return dates
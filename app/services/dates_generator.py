



def generate_dates(num_days=config.NUM_DAYS, exclude_weekends=config.EXCLUDE_WEEKENDS, timezone=config.LOG_TIMEZONE, country_code=config.COUNTRY_CODE):
    """
    Generates a list of dates from the current date.

    :param num_days: Number of dates to generate.
    :param exclude_weekends: Exclude weekends if True.
    :param timezone: Time zone for date generation.
    :param country_code: Country code for public holidays (Optional).
    :return: List of formatted date strings.
    """
    dates = []
    current_date = datetime.now(pytz.timezone(timezone))

    while len(dates) < num_days:
        if exclude_weekends and current_date.weekday() >= 5:  # Skip weekends (5 and 6 corresponds to Saturday-Sunday)
            current_date += timedelta(days=1) # Add one day to the current date
            continue

        # Check for public holidays (optional)
        if country_code and current_date in holidays.CountryHoliday(country_code):  # Skip public holidays
            current_date += timedelta(days=1)
            continue
        
        formatted_date = current_date.strftime('%d.%m.%Y (%a)') # Format the date as DD.MM.YYYY (Day)

        dates.append(formatted_date) # Add the formatted date to the list of dates

        current_date += timedelta(days=1) # Add one day to the current date

        # Output the list of dates: ['DD.MM.YYYY (Day)', 'DD.MM.YYYY (Day)', ...]

    return dates
# project portofolio/junior projects/daily-expense-tracker/utils/date_utils.py

"""
Date Utilities
Provides utility functions for date manipulation and formatting.
"""

import calendar
from datetime import date, datetime, timedelta


def get_current_date():
    """Get today's date."""
    return date.today()


def get_current_month_year():
    """Get current month and year."""
    now = datetime.now()
    return now.month, now.year


def get_month_name(month, language="id"):
    """
    Get month name in specified language.
    
    Args:
        month: Month number (1-12)
        language: 'id' for Indonesian, 'en' for English
        
    Returns:
        Month name as string
    """
    if language == "id":
        month_names = [
            "Januari",
            "Maret",
            "April",
            "Mei",
            "Juni",
            "Juli",
            "Agustus",
            "September",
            "Oktober",
            "November",
            "Desember",
        ]
    else:
        month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

    if 1 <= month <= 12:
        return month_names[month - 1]
    return ""


def get_month_range(year, month):
    """
    Get first and last day of a month.
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    start_date = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)
    return start_date, end_date


def get_previous_month(year, month):
    """
    Get previous month and year.
    
    Args:
        year: Current year
        month: Current month (1-12)
        
    Returns:
        Tuple of (previous_year, previous_month)
    """
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1


def get_next_month(year, month):
    """
    Get next month and year.
    
    Args:
        year: Current year
        month: Current month (1-12)
        
    Returns:
        Tuple of (next_year, next_month)
    """
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1


def get_previous_month_year(month: int, year: int) -> tuple:
    """
    Get previous month and year.
    Alternative function with parameter order (month, year).
    
    Args:
        month: Current month (1-12)
        year: Current year
        
    Returns:
        Tuple of (previous_month, previous_year)
    """
    if month == 1:
        return 12, year - 1
    return month - 1, year


def get_next_month_year(month: int, year: int) -> tuple:
    """
    Get next month and year.
    Alternative function with parameter order (month, year).
    
    Args:
        month: Current month (1-12)
        year: Current year
        
    Returns:
        Tuple of (next_month, next_year)
    """
    if month == 12:
        return 1, year + 1
    return month + 1, year


def format_date(date_obj, format_str="%d %b %Y"):
    """
    Format a date object with custom format string.
    
    Args:
        date_obj: Date object
        format_str: Format string (default: "%d %b %Y")
        
    Returns:
        Formatted date string
    """
    return date_obj.strftime(format_str)


def parse_date_string(date_str, format_str="%Y-%m-%d"):
    """
    Parse a date string into a date object.
    
    Args:
        date_str: Date string
        format_str: Format string (default: "%Y-%m-%d")
        
    Returns:
        Date object or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, format_str).date()
    except ValueError:
        return None


def get_days_in_month(year, month):
    """
    Get number of days in a month.
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        Number of days
    """
    return calendar.monthrange(year, month)[1]


def is_leap_year(year):
    """Check if a year is a leap year."""
    return calendar.isleap(year)


def get_weekday_name(date_obj, language="id"):
    """
    Get weekday name in specified language.
    
    Args:
        date_obj: Date object
        language: 'id' for Indonesian, 'en' for English
        
    Returns:
        Weekday name as string
    """
    if language == "id":
        weekday_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    else:
        weekday_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

    weekday_index = date_obj.weekday()
    return weekday_names[weekday_index]


def get_last_n_months(n=6, include_current=True):
    """
    Get list of last n months as (year, month) tuples.
    
    Args:
        n: Number of months to get
        include_current: Whether to include current month
        
    Returns:
        List of (year, month) tuples
    """
    months = []
    current_year, current_month = get_current_month_year()

    if include_current:
        months.append((current_year, current_month))
        n -= 1

    year, month = current_year, current_month
    for _ in range(n):
        year, month = get_previous_month(year, month)
        months.insert(0, (year, month))

    return months


def get_date_range(start_date, end_date):
    """
    Get list of all dates between start_date and end_date (inclusive).
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of date objects
    """
    if start_date > end_date:
        return []

    date_list = []
    current_date = start_date

    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    return date_list


def get_monthly_dates(year, month):
    """
    Get all dates in a month.
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        List of date objects
    """
    start_date, end_date = get_month_range(year, month)
    return get_date_range(start_date, end_date)


def format_date_id(date_obj):
    """
    Format date in Indonesian format (e.g., "15 Januari 2024").
    
    Args:
        date_obj: Date object
        
    Returns:
        Formatted date string
    """
    day = date_obj.day
    month_name = get_month_name(date_obj.month, "id")
    year = date_obj.year
    return f"{day} {month_name} {year}"


def format_date_short(date_obj):
    """
    Format date in short format (e.g., "15/01/2024").
    
    Args:
        date_obj: Date object
        
    Returns:
        Formatted date string
    """
    return date_obj.strftime("%d/%m/%Y")


def is_valid_date(year, month, day):
    """
    Check if a date is valid.
    
    Args:
        year: Year
        month: Month (1-12)
        day: Day
        
    Returns:
        True if valid, False otherwise
    """
    try:
        date(year, month, day)
        return True
    except ValueError:
        return False


def get_quarter(month):
    """
    Get quarter of a month.
    
    Args:
        month: Month (1-12)
        
    Returns:
        Quarter number (1-4)
    """
    return (month - 1) // 3 + 1


def test_date_utils():
    """Test all date utility functions."""
    print("Testing Date Utilities...")

    today = get_current_date()
    current_month, current_year = get_current_month_year()
    print(f"1. Today: {today}")
    print(f"Current month/year: {current_month}/{current_year}")
    print(f"Month name: {get_month_name(current_month)}")

    start_date, end_date = get_month_range(current_year, current_month)
    print("\n2. Month range:")
    print(f"Start: {start_date}")
    print(f"End: {end_date}")
    print(f"Days in month: {get_days_in_month(current_year, current_month)}")

    prev_year, prev_month = get_previous_month(current_year, current_month)
    next_year, next_month = get_next_month(current_year, current_month)
    print("\n3. Navigation:")
    print(f"Previous: {get_month_name(prev_month)} {prev_year}")
    print(f"Next: {get_month_name(next_month)} {next_year}")
    
    # Test alternative navigation functions
    prev_month_year = get_previous_month_year(current_month, current_year)
    next_month_year = get_next_month_year(current_month, current_year)
    print(f"Previous (alt): {get_month_name(prev_month_year[0])} {prev_month_year[1]}")
    print(f"Next (alt): {get_month_name(next_month_year[0])} {next_month_year[1]}")

    print("\n4. Date formatting:")
    print(f"Indonesian: {format_date_id(today)}")
    print(f"Short: {format_date_short(today)}")
    print(f"Weekday: {get_weekday_name(today)}")

    last_6_months = get_last_n_months(6)
    print("\n5. Last 6 months:")
    for y, m in last_6_months:
        print(f"{get_month_name(m)} {y}")

    print("\n6. Date validation:")
    test_dates = [
        (2024, 2, 29, True),
        (2023, 2, 29, False),
        (2024, 13, 1, False),
        (2024, 12, 31, True),
    ]

    for year, month, day, expected in test_dates:
        result = is_valid_date(year, month, day)
        status = "OK" if result == expected else "FAIL"
        print(f"{status} {year}-{month:02d}-{day:02d}: {result}")

    print("\n7. Quarters:")
    for month in [1, 4, 7, 10]:
        print(f"Month {month} ({get_month_name(month)}): Quarter {get_quarter(month)}")

    date_str = "2024-01-15"
    parsed_date = parse_date_string(date_str)
    if parsed_date:
        print("\n8. Date parsing:")
        print(f"Parsed '{date_str}': {parsed_date}")
        print(f"Formatted: {format_date_id(parsed_date)}")

    print("\nDate utilities test completed!")


if __name__ == "__main__":
    test_date_utils()
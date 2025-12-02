# project portofolio\junior projects\daily-expense-tracker\utils\date_utils.py

""""
Date Utilities
Provides utility functions for date manipulation and formatting.
"""

from datetime import datetime, date, timedelta
import calendar

def get_current_date():
    return date.today()

def get_current_month_year():
    now = datetime.now()
    return now.month, now.year

def get_month_name(month, language='id'):
    if language == 'id':
        month_names = [
            'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ]
    else:
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
    
    if 1 <= month <= 12:
        return month_names[month - 1]
    return ''

def get_month_range(year, month):
    start_date = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)
    return start_date, end_date

def get_previous_month(year, month):
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1

def get_next_month(year, month):
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1

def format_date(date_obj, format_str='%d %b %Y'):
    return date_obj.strftime(format_str)

def parse_date_string(date_str, format_str='%Y-%m-%d'):
    try:
        return datetime.strptime(date_str, format_str).date()
    except ValueError:
        return None

def get_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]

def is_leap_year(year):
    return calendar.isleap(year)

def get_weekday_name(date_obj, language='id'):
    if language == 'id':
        weekday_names = [
            'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'
        ]
    else:
        weekday_names = [
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ]
    
    weekday_index = date_obj.weekday()
    return weekday_names[weekday_index]

def get_last_n_months(n=6, include_current=True):
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
    if start_date > end_date:
        return []
    
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    
    return date_list

def get_monthly_dates(year, month):
    start_date, end_date = get_month_range(year, month)
    return get_date_range(start_date, end_date)

def format_date_id(date_obj):
    day = date_obj.day
    month_name = get_month_name(date_obj.month, 'id')
    year = date_obj.year
    return f"{day} {month_name} {year}"

def format_date_short(date_obj):
    return date_obj.strftime('%d/%m/%Y')

def is_valid_date(year, month, day):
    try:
        date(year, month, day)
        return True
    except ValueError:
        return False

def get_quarter(month):
    return (month - 1) // 3 + 1

def test_date_utils():
    print("Testing Date Utilities...")
    
    today = get_current_date()
    current_month, current_year = get_current_month_year()
    print(f"1. Today: {today}")
    print(f"Current month/year: {current_month}/{current_year}")
    print(f"Month name: {get_month_name(current_month)}")
    
    start_date, end_date = get_month_range(current_year, current_month)
    print(f"\n2. Month range:")
    print(f"Start: {start_date}")
    print(f"End: {end_date}")
    print(f"Days in month: {get_days_in_month(current_year, current_month)}")
    
    prev_year, prev_month = get_previous_month(current_year, current_month)
    next_year, next_month = get_next_month(current_year, current_month)
    print(f"\n3. Navigation:")
    print(f"Previous: {get_month_name(prev_month)} {prev_year}")
    print(f"Next: {get_month_name(next_month)} {next_year}")
    
    print(f"\n4. Date formatting:")
    print(f"Indonesian: {format_date_id(today)}")
    print(f"Short: {format_date_short(today)}")
    print(f"Weekday: {get_weekday_name(today)}")
    
    last_6_months = get_last_n_months(6)
    print(f"\n5. Last 6 months:")
    for y, m in last_6_months:
        print(f"{get_month_name(m)} {y}")
    
    print(f"\n6. Date validation:")
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
    
    print(f"\n7. Quarters:")
    for month in [1, 4, 7, 10]:
        print(f"Month {month} ({get_month_name(month)}): Quarter {get_quarter(month)}")
    
    date_str = "2024-01-15"
    parsed_date = parse_date_string(date_str)
    if parsed_date:
        print(f"\n8. Date parsing:")
        print(f"Parsed '{date_str}': {parsed_date}")
        print(f"Formatted: {format_date_id(parsed_date)}")
    
    print("\nDate utilities test completed!")

if __name__ == "__main__":
    test_date_utils()

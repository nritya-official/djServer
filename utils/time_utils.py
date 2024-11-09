from datetime import datetime
import pytz

class TimezoneConstants:
    IST = 'Asia/Kolkata'          # Indian Standard Time
    UTC = 'UTC'                   # Coordinated Universal Time
    EST = 'America/New_York'      # Eastern Standard Time (New York)
    CST = 'America/Chicago'       # Central Standard Time (Chicago)
    MST = 'America/Denver'        # Mountain Standard Time (Denver)
    PST = 'America/Los_Angeles'   # Pacific Standard Time (Los Angeles)
    GMT = 'Europe/London'         # Greenwich Mean Time (London)
    CET = 'Europe/Berlin'         # Central European Time (Berlin)
    JST = 'Asia/Tokyo'            # Japan Standard Time (Tokyo)
    AEST = 'Australia/Sydney'      # Australian Eastern Standard Time (Sydney)
    NZST = 'Pacific/Auckland'      # New Zealand Standard Time (Auckland)
    MSK = 'Europe/Moscow'          # Moscow Standard Time
    SAST = 'Africa/Johannesburg'   # South Africa Standard Time
    WAT = 'Africa/Lagos'           # West Africa Time (Lagos)


class TimeNow:
    def __init__(self, timezone=TimezoneConstants.IST, date=None, time=None):
        self.timezone = timezone
        tz = pytz.timezone(timezone)
        
        # Default to current date and time in the specified timezone if none provided
        if date and time:
            # Attempt to parse various acceptable formats for the provided time
            time_formats = ['%I:%M %p', '%I:%M%p', '%I %p', '%I%p']
            for fmt in time_formats:
                try:
                    # Combine date and time for complete datetime parsing
                    date_time_str = f"{date} {time}"
                    self.datetime_obj = tz.localize(datetime.strptime(date_time_str, f"%Y-%m-%d {fmt}"))
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Time format is not recognized. Use formats like '08:30 PM', '8:30PM', etc.")
        else:
            # Use the current time if no date or time is provided
            self.datetime_obj = datetime.now(tz)
        
        # Store date and time separately in specified format
        self.date = self.datetime_obj.strftime('%Y-%m-%d')
        self.time = self.datetime_obj.strftime('%I:%M %p')  # 12-hour format with AM/PM

    def __str__(self):
        return f"{self.date} {self.time} ({self.timezone})"
    
    def __eq__(self, other):
        return self.datetime_obj == other.datetime_obj
    
    def __lt__(self, other):
        return self.datetime_obj < other.datetime_obj
    
    def __gt__(self, other):
        return self.datetime_obj > other.datetime_obj
    
    def compare_with_now(self, compare_timezone=TimezoneConstants.IST):
        """Compares instance datetime with the current time in a specified timezone."""
        compare_tz = pytz.timezone(compare_timezone)
        current_time_in_tz = datetime.now(compare_tz)  # This is already timezone-aware

        # Compare datetime objects
        if self.datetime_obj < current_time_in_tz:
            return -1  # Instance datetime is in the past
        elif self.datetime_obj > current_time_in_tz:
            return +1  # Instance datetime is in the future
        else:
            return 0  # Instance datetime is equal to current time

'''
time_now_utc = TimeNow(TimezoneConstants.UTC, '2024-10-31', '08:30 PM')
print("Specified UTC Time:", time_now_utc)

time_test_1 = TimeNow(TimezoneConstants.IST, '2024-10-31', '08:30PM')
time_test_2 = TimeNow(TimezoneConstants.IST, '2024-10-31', '8:30 PM')
time_test_3 = TimeNow(TimezoneConstants.IST, '2024-10-31', '8:30PM')
time_test_4 = TimeNow(TimezoneConstants.IST, '2024-10-30', '8:30PM')

print("Comparison with current IST time:", time_now_utc.compare_with_now(TimezoneConstants.IST))
print("Comparison with current UTC time:", time_now_utc.compare_with_now(TimezoneConstants.UTC))
'''

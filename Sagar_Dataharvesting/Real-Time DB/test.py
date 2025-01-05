from datetime import datetime

# Assuming config and current_time are already defined
config = {
    'end_time': '15:30'  # Example time in HH:MM format
}

# Get the current time
current_time = datetime.now()

# Extract hour and minute from the end_time string
end_time_str = config['end_time']
end_hour, end_minute = map(int, end_time_str.split(':'))

# Replace hour and minute in the current datetime object
end_time = current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)

# Now end_time is a datetime object representing today's date with the specified time
print(f"Current Time: {current_time}")
print(f"End Time: {end_time}")

# Check if current_time is greater than end_time
if current_time > end_time:
    print("hello")
else:
    print("Current time is not greater than end_time")

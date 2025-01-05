from datetime import datetime, timedelta

# Example item dictionary
item = {
    "LastUpdateTime": 1403354580  # Example timestamp
}

# Calculate the adjusted datetime
adjusted_datetime = (
    datetime.fromtimestamp(item.get("LastUpdateTime", None) + 315532800) - timedelta(minutes=60)
    if item.get("LastUpdateTime", None) is not None
    else None
)

# Convert the final datetime to milliseconds since epoch
if adjusted_datetime is not None:
    milliseconds_since_epoch = int(adjusted_datetime.timestamp() * 1000)
    formatted_datetime = adjusted_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Format to "yyyy-MM-dd HH:mm:ss.SSS"
else:
    milliseconds_since_epoch = None
    formatted_datetime = None

# Print the results
print("Adjusted datetime:", formatted_datetime)
print("Milliseconds since epoch:", milliseconds_since_epoch)

function generateTimeList(params) {
    const startTime = params["default_value"] || "00:00";
    const minTime = params["min_time"] || startTime;
    const maxTime = params["max_time"] || "23:59";
    const difference = params["difference"] || 15;

    const timeList = [startTime];
    let currentTime = startTime;

    while (currentTime < maxTime) {
        const [hour, minute] = currentTime.split(":").map(Number);
        const nextHour = Math.floor((hour * 60 + minute + difference) / 60) % 24;
        const nextMinute = (hour * 60 + minute + difference) % 60;
        const nextTime = `${String(nextHour).padStart(2, "0")}:${String(nextMinute).padStart(2, "0")}`;
        
        currentTime = nextTime;
        if (currentTime <= maxTime) {
            timeList.push(currentTime);
        }
    }

    console.log(timeList);
    return timeList;
}

const paramsJson = `{
    "start_time": {"default_value": "09:30", "min_time": "09:30", "max_time": "15:00", "difference": 5}
}`;

const params = JSON.parse(paramsJson);
generateTimeList(params['start_time']);

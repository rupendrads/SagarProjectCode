class Optimizer {
    constructor(paramsJson, calculateCombinations = true) {
        this.params = JSON.parse(paramsJson);
        this.calculateCombinations = calculateCombinations;
    }

    generateFinalCombinationList() {
        if (!this.calculateCombinations) {
            const defaultParameters = {};
            console.log("\nDefault Parameter Values:");
            for (const [paramName, paramValue] of Object.entries(this.params)) {
                if (!paramName.startsWith("rule")) {
                    const defaultValue = paramValue["default_value"] || "";
                    defaultParameters[paramName] = defaultValue;
                }
            }
            console.log([defaultParameters]);

            return [defaultParameters];
        } else {
            return this.generateParameterCombinations();
        }
    }

    applyRule(combination, rule) {
        if (rule) {
            const parameterList = rule["parameter_list"];
            const relation = rule["relation"];
    
            if (parameterList && relation) {
                const paramValues = {};
                for (const paramName of parameterList) {
                    paramValues[paramName] = combination[paramName];
                }
    
                try {
                    const { long_ma, short_ma } = paramValues; // Destructure long_ma and short_ma from paramValues
                    return eval(relation); // Evaluate the relation expression in the context of paramValues
                } catch (error) {
                    console.error("Error evaluating rule:", error);
                    return false;
                }
            }
        }
        return true; // If no rule specified or if there's an error evaluating the rule, consider it passed
    }

    generateParameterCombinations() {
        const parameterCombinations = [];
        console.log("\nAll Parameter Combinations:");
        const allParameters = {};
        for (const [paramName, param] of Object.entries(this.params)) {
            if (paramName === "rule") {
                continue;
            }
            if (this.isTimeFormat(param)) {
                allParameters[paramName] = this.generateTimeList(param);
            } else if (param["types"]) {
                allParameters[paramName] = param["types"];
            } else {
                allParameters[paramName] = this.generatePeriodList(param);
            }
        }

        const rule = this.params["rule"];

        for (const combination of this.cartesianProduct(Object.values(allParameters))) {
            const paramsCombination = {};
            for (let i = 0; i < Object.keys(allParameters).length; i++) {
                const paramName = Object.keys(allParameters)[i];
                paramsCombination[paramName] = combination[i];
            }
            if (!rule || this.applyRule(paramsCombination, rule)) {
                parameterCombinations.push(paramsCombination);
                // console.log(paramsCombination); // Log each permutation
            }
        }

        return parameterCombinations;
    }

    cartesianProduct(arrays) {
        return arrays.reduce((a, b) => a.flatMap(x => b.map(y => [x, y].flat())));
    }

    isTimeFormat(params) {
        for (const value of Object.values(params)) {
            if (typeof value === "string") {
                try {
                    const time = value.split(":");
                    if (time.length === 2) {
                        const hour = parseInt(time[0]);
                        const minute = parseInt(time[1]);
                        if (!isNaN(hour) && !isNaN(minute) &&
                            hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59) {
                            return true;
                        }
                    }
                } catch (error) {
                    return false;
                }
            }
        }
        return false;
    }

    generateTimeList(params) {
        const startTime = params["default_value"] || "09:15";
        const minTime = params["min_time"] || startTime;
        const maxTime = params["max_time"] || "15:30";
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

    generatePeriodList(params) {
        const defaultValue = params["default_value"] || 1;
        const minvalue = params["min_value"] || 1;
        const maxvalue = params["max_value"] || 60;
        const increment = params["increment"] || 1;

        const periodList = [minvalue];
        let currentValue = minvalue;

        while (currentValue <= maxvalue) {
            currentValue += increment;
            if (currentValue <= maxvalue) {
                periodList.push(currentValue);
            }
        }
        console.log(periodList);
        return periodList;
    }
}

const paramsJson = `{
    "start_time": {"default_value": "09:30", "min_time": "09:30", "max_time": "12:00", "difference": 5},
    "end_time": {"default_value": "14:30", "min_time": "14:30", "max_time": "15:00", "difference": 15},
    "short_ma": {"period_name": "ShortPeriod", "default_value": 15, "min_value": 1, "max_value": 50, "increment": 1},
    "long_ma": {"period_name": "LongPeriod", "default_value": 30, "min_value": 1, "max_value": 50, "increment": 1},
    "rule": {"parameter_list": ["short_ma", "long_ma"], "relation": "2 <= long_ma - short_ma && long_ma - short_ma < 5"},
    "moving_average":{"default_value":"ema", "types" :["sma","ema","dema", "tema"]},
    "timeframe": {"default_value": 10, "min_value": 1, "max_value": 50, "increment": 5}
}`;

const optimizer = new Optimizer(paramsJson, true);
const tbc = new Date();
const combinations = optimizer.generateFinalCombinationList();
const tac = new Date();
console.log("Total Combinations:", combinations.length);
console.log("Time Taken:", tac - tbc, "milliseconds");
let counter = 0;
console.log(combinations.length);
for(const combination of combinations){
    console.log(combination)
    break
}
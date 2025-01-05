from datetime import datetime

def to_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

def validate_leg_relations(leg):
    # print("--------------------------entered validate leg------------------------------------")
    # print(leg)
    # print(f"trailing_options: {leg['trailing_options']}")
    # print(f"profit_reaches: {leg['profit_reaches']}, lock_profit: {leg['lock_profit']}")
    # print(f"increase_in_profit: {leg['increase_in_profit']}, trail_profit: {leg['trail_profit']}")
    
    # Check if trailing_options is False
    if not leg["strike_selection_criteria_trailing_options"]:
        leg["strike_selection_criteria_profit_reaches"] = 0
        leg["strike_selection_criteria_lock_profit"] = 0
        leg["strike_selection_criteria_increase_in_profit"] = 0
        leg["strike_selection_criteria_trail_profit"] = 0
        return True
    
    # Validate 'lock' case
    elif leg["strike_selection_criteria_trailing_options"] == "lock":
        leg["strike_selection_criteria_increase_in_profit"]=0
        leg["strike_selection_criteria_trail_profit"]=0
        if leg["strike_selection_criteria_profit_reaches"] < leg["strike_selection_criteria_lock_profit"]:
            print("Returning False: strike_selection_criteria_profit_reaches is less than strike_selection_criteria_lock_profit")
            return False
    
    # Validate 'lock_and_trail' case
    elif leg["strike_selection_criteria_trailing_options"] == "lockntrail":
        if leg["strike_selection_criteria_profit_reaches"] < leg["strike_selection_criteria_lock_profit"] or leg["strike_selection_criteria_increase_in_profit"] < leg["strike_selection_criteria_trail_profit"]:
            print("Returning False: lockntrail condition failed")
            return False
        
    if not leg["roll_strike_trailing_options"]:
        leg["roll_strike_profit_reaches"] = 0
        leg["roll_strike_lock_profit"] = 0
        leg["roll_strike_increase_in_profit"] = 0
        leg["roll_strike_trail_profit"] = 0
        return True
    
    # Validate 'lock' case
    elif leg["roll_strike_trailing_options"] == "lock":
        if leg["roll_strike_profit_reaches"] < leg["roll_strike_lock_profit"]:
            print("Returning False: roll_strike_profit_reaches is less than lock_profit")
            return False
    
    # Validate 'lock_and_trail' case
    elif leg["roll_strike_trailing_options"] == "lockntrail":
        if leg["roll_strike_profit_reaches"] < leg["roll_strike_lock_profit"] or leg["roll_strike_increase_in_profit"] < leg["roll_striketrail_profit"]:
            print("Returning False: lock_and_trail condition failed for roll_strike")
            return False
    
    return True  



def validate_relations(combination):
    print(combination)
    if not combination["trailing_options"]:
        combination["profit_reaches"] = 0
        combination["lock_profit"] = 0
        combination["increase_in_profit"] = 0
        combination["trail_profit"] = 0
    elif combination["trailing_options"] == "lock":
        combination["increase_in_profit"] = 0
        combination["trail_profit"] = 0
        if combination["profit_reaches"] < combination["lock_profit"]:
            return False
    elif combination["trailing_options"] == "lockntrail":
        if combination["profit_reaches"] < combination["lock_profit"] or combination["increase_in_profit"] < combination["trail_profit"]:
            return False
    else:
        pass

    
    if "entry_time" in combination and "last_entry_time" in combination:
        if combination["last_entry_time"] is not False:
            if to_time(combination["entry_time"]) >= to_time(combination["last_entry_time"]):
                return False
    if "last_entry_time" in combination and "exit_time" in combination:
        if combination["last_entry_time"] is not False:
            if to_time(combination["last_entry_time"]) > to_time(combination["exit_time"]):
                return False
        else:
            if "entry_time" in combination and to_time(combination["entry_time"]) >= to_time(combination["exit_time"]):
                return False

    if "legs" in combination:
        for leg in combination["legs"]:
            if not validate_leg_relations(leg):
                # print(f"{leg} is returning return as False ")
                return False

    return True

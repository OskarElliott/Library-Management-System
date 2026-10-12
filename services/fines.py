from datetime import date, timedelta

def count_chargeable_days(due_date, return_date, closed_days):
    due = date.fromisoformat(due_date)
    returned = date.fromisoformat(return_date)

    days = 0
    day = due + timedelta(days=1)

    while day <= returned:
        if day.weekday() < 5 and day.isoformat() not in closed_days:
            days += 1
        day += timedelta(days=1)

    return days

def calculate_fine(chargeable_days, rule):
    days_to_charge = chargeable_days - rule["grace_days"]

    if days_to_charge <= 0:
        return 0.0

    tier_1_days = min(days_to_charge, rule["tier_1_days"])
    tier_2_days = days_to_charge - tier_1_days

    amount = (tier_1_days * rule["tier_1_rate"] + tier_2_days * rule["tier_2_rate"])

    return round(min(amount, rule["max_amount"]), 2)
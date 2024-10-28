from datetime import datetime

date_format = "%d-%m-%Y"

categories = {
    "I": "Income",
    "E": "Expense"
}

def get_date(prompt, allow_default=False):
    date = input(prompt)
    if allow_default and not date:
        return datetime.today().strftime(date_format)
    
    try:
        valid_date = datetime.strptime(date, date_format)
        return valid_date.strftime(date_format)
    except ValueError:
        print("Invalid date format. Please enter the date in the format dd-mm-yyy _")
        return get_date(prompt, allow_default)

def get_amount():
    try:
        amount = float(input("Enter the amount:"))
        if amount <= 0:
            raise ValueError("Amount should not be less than or equal to zero")
        return amount
    except ValueError as e:
        print(e)
        return get_amount()

def get_category():
    category = input("Enter the category ('I' for Icome or 'E' for Expense) _").upper()
    if category in categories:
        return categories[category]
    else:
        print("Invalid category. Please enter ('I' for Icome or 'E' for Expense) _").upper()
        return get_category()
    

def get_description():
    description = input("Enter the description (Optional) _")
    return description
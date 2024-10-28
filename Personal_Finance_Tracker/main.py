import pandas as pd # type: ignore
import csv
from datetime import datetime
from data_entry import get_amount, get_category, get_date, get_description
from matplotlib import pyplot as plt # type: ignore

class CSV:
    CSV_FILE = "finance_date.csv" #name of the csv file that will store the data
    COLUMNS = ["date","amount","category","description"] #columns of the csv file
    
    """
    We will be using @classmethod decorator to define the class methods because we don't need to create an instance of the class to use these methods.
    e.g using here CSV.initialize() instead of creating an instance of the class and then calling the method like csv = CSV() and then csv.initialize()
    The use of 'cls' as the first argument of the class method is a convention in Python to refer to the class itself. It is similar to 'self' which is used to refer to the instance of the class.
    """
    
    @classmethod
    def initialize(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)
    
    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS) 
            writer.writerow(new_entry)
        print("Entry addded successfully :)")
    
    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        #Converting the date to datetime object for manipulation with datetime functions
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        end_date = datetime.strptime(end_date, "%d-%m-%Y")
        
        #Converting the date to string
        start_date_str = start_date.strftime("%d-%m-%Y")
        end_date_str = end_date.strftime("%d-%m-%Y")
        
        #Filtering the data based on the date range
        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]
        
        if filtered_df.empty:
            print("No transactions found :(")
        else:
            print(f"Transactions from {start_date_str} to {end_date_str} is ")
            print(filtered_df.to_string(index=False, formatters={
                "date": lambda x: x.strftime("%d-%m-%Y")
            }))
            
            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].fillna(0).sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].fillna(0).sum()
            
            print("\n Summary")
            print(f"Total Income: €{total_income: .2f}")
            print(f"Total Expense: €{total_expense: .2f}")
            print(f"Net savings: €{(total_income - total_expense):.2f}")
            
        return filtered_df
    
    @classmethod
    def plot_transactions(cls, df):
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        df.sort_values("date", inplace=True)
        df.set_index("date", inplace=True)
        
        income_df = df[df["category"] == "Income"].resample("D").sum().reindex(df.index, fill_value=0)
        expense_df = df[df["category"] == "Expense"].resample("D").sum().reindex(df.index, fill_value=0)
        
        plt.figure(figsize=(10, 6))
        plt.plot(income_df.index, income_df["amount"], label="Income", color="green")
        plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="red")
        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.title("Income vs Expense")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()  # Ensure everything fits without overlap
        plt.show()

def add():
    CSV.initialize()
    date = get_date("Enter the date of the transactions (dd-mm-yy) or press the enter key for today's date _", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)
    
def main():
    while True:
        print("1. Add a transaction")
        print("2. View transactions")
        print("3. Exit")
        choice = input("Enter your choice (1-3) _")
        
        if choice == "1":
            add()
        elif choice == "2":
            start_date = get_date("Enter the start date of the transactions (dd-mm-yy) _")
            end_date = get_date("Enter the end date of the transactions (dd-mm-yy) _")
            df = CSV.get_transactions(start_date, end_date)
            if input("Do you want to plot the transactions? (y/n) _").lower() == "y":
                CSV.plot_transactions(df)
            else:
                continue
        elif choice == "3":
            print("Exiting the program...")
            break
        else:
            print("Invalid choice. Please enter a valid choice (1, 2, or 3) _")



if __name__ == "__main__":
    main()
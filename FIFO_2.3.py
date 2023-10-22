from os import listdir, path, remove, system
import pandas as pd

localPath = path.dirname(__file__) + "\\Stocks\\"
backupPath = path.dirname(__file__) + "\\Backup\\"
csvPath = path.dirname(__file__) + "\\CSV\\"


# To buy stock for the first time. It creates a new file per stock and adds the new buy entry.
def NewStock():
    header = ["Date", "Buy_price", "Sell_price", "Amount", "Inventory", "Total_stock", "Balance", "Profit", "Profit_total", "Increase", "NI"]
    newStockName = input("Please insert new stock name: ")
    for i in listdir(localPath): # Scans through the existing stocks to avoid overriding any existing one with the same name.
        assert newStockName.lower() != i.lower()[:-4], "This stock already exists!"
    df = pd.DataFrame(columns=header)
    df.at[len(df.index), "Date"] = input("Please enter the date: ")
    df.at[df.index[-1], "Buy_price"] = float(input("Please enter the buy price: "))
    assert df.at[df.index[-1], "Buy_price"] > 0, "Buy price can't be negative nor nil."
    df.at[df.index[-1], "Sell_price"] = "-"
    df.at[df.index[-1], "Amount"] = float(input("Please enter the amount purchased: "))
    assert df.at[df.index[-1], "Amount"] > 0, "The amount purchased can't be negative nor nil."
    df.at[df.index[-1], "Inventory"] = df.at[df.index[-1], "Amount"]
    df.at[df.index[-1], "Total_stock"] = df.at[df.index[-1], "Amount"]
    df.at[df.index[-1], "Balance"] = df.at[df.index[-1], "Amount"] * df.at[df.index[-1], "Buy_price"] * -1
    df.at[df.index[-1], "Profit"] = 0
    df.at[df.index[-1], "Profit_total"] = 0
    df.at[df.index[-1], "Increase"] = 0
    df.at[df.index[-1], "NI"] = 0
    Backup(newStockName, df)
    df.to_pickle(localPath + newStockName + ".pk1")
    print(df)

# To buy an existing stock. It reads and writes the file created by the NewStock function.
def BuyStock():
    stockName = input("Please enter the stock name: ")
    
    if stockName.lower() in list(map(lambda x: x[:-4].lower(), listdir(localPath))): # To keep stockName with its original capitalisation.
        ix = list(map(lambda x: x[:-4].lower(), listdir(localPath))).index(stockName.lower())
        stockName = listdir(localPath)[ix][:-4]

    df = pd.read_pickle(localPath + stockName + ".pk1")
    dfb = df.copy()

    print(df.iloc[-5:])
    df.at[len(df.index), "Date"] = input("Please enter the date: ")
    df.at[df.index[-1], "Buy_price"] = float(input("Please enter the buy price: "))
    assert df.at[df.index[-1], "Buy_price"] > 0, "Buy price can't be negative nor nil."
    df.at[df.index[-1], "Sell_price"] = "-"
    df.at[df.index[-1], "Amount"] = float(input("Please enter the amount purchased: "))
    assert df.at[df.index[-1], "Amount"] > 0, "The amount purchased can't be negative nor nil."
    df.at[df.index[-1], "Inventory"] = df.at[df.index[-1], "Amount"]
    df.at[df.index[-1], "Total_stock"] = df.at[df.index[-2], "Total_stock"] + df.at[df.index[-1], "Amount"]
    df.at[df.index[-1], "Balance"] = df.at[df.index[-2], "Balance"] - df.at[df.index[-1], "Amount"] * df.at[df.index[-1], "Buy_price"]
    df.at[df.index[-1], "Profit"] = 0
    df.at[df.index[-1], "Profit_total"] = df.at[df.index[-2], "Profit_total"]
    df.at[df.index[-1], "Increase"] = df.at[df.index[-2], "Increase"]
    df.at[df.index[-1], "NI"] = df.at[df.index[-2], "NI"]

    Backup(stockName, dfb) # Backs up the copy created above.
    df.to_pickle(localPath + stockName + ".pk1")
    print(df.iloc[-5:])

# To sell an existing stock. It reads and writes the file created by the NewStock function.
def SellStock():
    stockName = input("Please enter the stock name: ")

    if stockName.lower() in list(map(lambda x: x[:-4].lower(), listdir(localPath))): # To keep stockName with its original capitalisation.
        ix = list(map(lambda x: x[:-4].lower(), listdir(localPath))).index(stockName.lower())
        stockName = listdir(localPath)[ix][:-4]

    df = pd.read_pickle(localPath + stockName + ".pk1")
    dfb = df.copy()
    
    print(df.iloc[-5:])
    df.at[len(df.index), "Date"] = input("Please enter the date: ")
    df.at[df.index[-1], "Buy_price"] = "-"
    df.at[df.index[-1], "Sell_price"] = float(input("Please enter the sell price: "))
    assert df.at[df.index[-1], "Sell_price"] > 0, "Sell price can't be negative nor nil."
    df.at[df.index[-1], "Amount"] = float(input("Please enter the amount sold: "))
    assert df.at[df.index[-1], "Amount"] > 0, "Amount sold can't be negative nor nil."
    assert df.at[df.index[-1], "Amount"] <= df.at[df.index[-2], "Total_stock"], "You can't sell more than you currently own."
    df.at[df.index[-1], "Inventory"] = "-"
    df.at[df.index[-1], "Total_stock"] = df.at[df.index[-2], "Total_stock"] - df.at[df.index[-1], "Amount"]
    df.at[df.index[-1], "Balance"] = df.at[df.index[-2], "Balance"] + df.at[df.index[-1], "Amount"] * df.at[df.index[-1], "Sell_price"]

    # Logic to calculate profits based on previous stocks owned at their given buy prices.
    amountSold = df.at[df.index[-1], "Amount"]
    sellPrice = df.at[df.index[-1], "Sell_price"]
    profit = 0
    nextIndex = df.at[df.index[-2], "NI"]
    for i in range(df.at[df.index[-2], "NI"], len(df.index - 1)): # For loop from the last NI to the end of the DataFrame.
        if type(df.at[df.index[i], "Buy_price"]) != float: # Skips anything that doesn't have a Buy_price float value.
            nextIndex += 1
            continue
        if amountSold > df.at[df.index[i], "Inventory"]:
            amountSold = amountSold - df.at[df.index[i], "Inventory"]
            profit = profit + (sellPrice - df.at[df.index[i], "Buy_price"]) * df.at[df.index[i], "Inventory"]
            df.at[df.index[i], "Inventory"] = 0
            nextIndex += 1
        else:
            df.at[df.index[i], "Inventory"] = df.at[df.index[i], "Inventory"] - amountSold
            profit = profit + (sellPrice - df.at[df.index[i], "Buy_price"]) * amountSold
            amountSold = 0
            if df.at[df.index[-1], "Total_stock"] == 0:
                nextIndex = len(df.index)
            break
    df.at[df.index[-1], "Profit"] = profit
    df.at[df.index[-1], "Profit_total"] = df.at[df.index[-2], "Profit_total"] + profit
    df.at[df.index[-1], "Increase"] = df.at[df.index[-2], "Increase"] + profit
    df.at[df.index[-1], "NI"] = nextIndex # Keeps track of the next index for the sell function to start scanning from.
     
    Backup(stockName, dfb) # Backs up the copy created above.
    
    df.to_pickle(localPath + stockName + ".pk1")
    print(df.iloc[-5:])

# To print a given stock.
def PrintStock():
    stockName = input("Please enter the stock name: ")
    df = pd.read_pickle(localPath + stockName + ".pk1")
    df.round(8)
    print(df)

# To print a list of just stock names.
def ListStocks():
    stockList = listdir(localPath)
    spacing = " " * 30
    index = 0

    while index < len(stockList):
        for i in range(0,3):
            print(stockList[index], end=spacing[:-len(stockList[index])])
            index += 1
            if index >= len(stockList):
                break
        print()

# To export a given stock to a CSV file.
def ToCSV():
    stockName = input("Please enter the stock name: ")
    df = pd.read_pickle(localPath + stockName + ".pk1")
    df.to_csv(csvPath + stockName + ".csv")

# To offset "Increase", for Christians to include in their income to then calculate their tithes and offerings.
def IncreaseOffset():
    stockName = input("Please enter the stock name: ")

    if stockName.lower() in list(map(lambda x: x[:-4].lower(), listdir(localPath))): # To keep stockName with its original capitalisation.
        ix = list(map(lambda x: x[:-4].lower(), listdir(localPath))).index(stockName.lower())
        stockName = listdir(localPath)[ix][:-4]

    df = pd.read_pickle(localPath + stockName + ".pk1")
    dfb = df.copy()

    print(df.iloc[-5:])
    df.at[len(df.index), "Date"] = input("Please enter the date: ")
    df.at[df.index[-1], "Buy_price"] = "Offset"
    df.at[df.index[-1], "Sell_price"] = float(input("Please enter the amount to offset: "))
    df.at[df.index[-1], "Amount"] = "-"
    df.at[df.index[-1], "Inventory"] = "-"
    df.at[df.index[-1], "Total_stock"] = df.at[df.index[-2], "Total_stock"]
    df.at[df.index[-1], "Balance"] = df.at[df.index[-2], "Balance"]
    df.at[df.index[-1], "Profit"] = 0
    df.at[df.index[-1], "Profit_total"] = df.at[df.index[-2], "Profit_total"]
    df.at[df.index[-1], "Increase"] = df.at[df.index[-2], "Increase"] + df.at[df.index[-1], "Sell_price"]
    df.at[df.index[-1], "NI"] = df.at[df.index[-2], "NI"]

    Backup(stockName, dfb) # Backs up the copy created above.
    df.to_pickle(localPath + stockName + ".pk1")
    print(df.iloc[-5:])

# Prints the last lines and totals of all stocks owned.
def LastLines():
    header = ["Name", "Date", "Total_stock", "Balance", "Profit_total", "Increase"]
    fdf = pd.DataFrame(columns=header) # New DataFrame gets created to then print it, as we don't need to print all columns.
    total_stock, balance, profit_total, increase = 0, 0, 0, 0
    for stock in listdir(localPath):
        df = pd.read_pickle(localPath + stock)
        fdf.at[len(fdf.index), "Name"] = stock[:-4]
        fdf.at[fdf.index[-1], "Date"] = df.at[df.index[-1], "Date"]
        fdf.at[fdf.index[-1], "Total_stock"] = df.at[df.index[-1], "Total_stock"]
        total_stock += fdf.at[fdf.index[-1], "Total_stock"]
        fdf.at[fdf.index[-1], "Balance"] = df.at[df.index[-1], "Balance"]
        balance += fdf.at[fdf.index[-1], "Balance"]
        fdf.at[fdf.index[-1], "Profit_total"] = df.at[df.index[-1], "Profit_total"]
        profit_total += fdf.at[fdf.index[-1], "Profit_total"]
        fdf.at[fdf.index[-1], "Increase"] = df.at[df.index[-1], "Increase"]
        increase += fdf.at[fdf.index[-1], "Increase"]
    fdf.at[len(fdf.index), "Name"] = "TOTALS"
    fdf.at[fdf.index[-1], "Date"] = "-"
    fdf.at[fdf.index[-1], "Total_stock"] = total_stock
    fdf.at[fdf.index[-1], "Balance"] = balance
    fdf.at[fdf.index[-1], "Profit_total"] = profit_total
    fdf.at[fdf.index[-1], "Increase"] = increase
    print(fdf)

# Creates a copy of the stock file and stores it in a separate folder. This is to be able to go back one transaction in case of an input error.
def Backup(stockName, dfb):
    dfb.to_pickle(backupPath + stockName + "_" + str(len(dfb.index) - 1) + ".pk1")

# Copies the last backup saved into the Stocks folder, and then deletes it.
def UndoLastTR(): 
    stockName = input("Please enter the stock name: ")
    
    for i in listdir(backupPath)[::-1]:
        if stockName.lower() == i.lower()[:i.rfind("_")]:
            backupFile = backupPath + i
            break
    for i in listdir(localPath):
        if stockName.lower() == i.lower()[:-4]:
            existingFile = localPath + i
            break
    
    system(f'copy /Y "{backupFile}" "{existingFile}"')
    remove(backupFile)
    df = pd.read_pickle(existingFile)
    print("Stock successfully restored to previous transaction.", end="\n\n")
    print(df.iloc[-5:])











# Main execution.
while True:
    print("""[]===================== FIFO Inventory Tracker =====================]
    
    1 - Buy new stock
    2 - Buy existing stock
    3 - Sell stock
    4 - Offset Increase
    5 - Undo last transaction
    6 - Print stock
    7 - Stocks list
    8 - Stocks totals
    9 - Stock to CSV file
    """)
    selector = input("Please select one of the options above: ")    
    
    while True:
        try:
            if selector == "1":
                NewStock() # Buy new stock
                input()
                break
            elif selector == "2":
                BuyStock() # Buy existing stock
                input()
                break
            elif selector == "3":
                SellStock() # Sell stock
                input()
                break
            elif selector == "4":
                IncreaseOffset() # Offset increase
                input()
                break
            elif selector == "5":
                UndoLastTR() # Undo last transaction
                input()
                break
            elif selector == "6":
                PrintStock() # Print stock
                input()
                break
            elif selector == "7":
                ListStocks() # Stocks list
                input()
                break
            elif selector == "8":
                LastLines() # Stock totals
                input()
                break
            elif selector == "9":
                ToCSV() # Stock to CSV file
                break
            else:
                print("Selection not valid, please try again.")
                input()
                break
        except AssertionError as ae:
            print(ae.args[0])
        except (FileNotFoundError, UnboundLocalError):
            print("You don't seem to own that stock.")
            input()
            break
        except ValueError:
            print("Buy/Sell/Offset must be a number!")
        except KeyboardInterrupt:
            break

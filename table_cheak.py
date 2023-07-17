import prettytable
import matplotlib.pyplot as pylot
import pandas

data= pandas.read_csv("spread.csv",encoding="shift-jis")
data["time"] = pandas.to_datetime(data["time"])


#テーブルを作る
table = prettytable.PrettyTable()
table.field_names=["PAIR", "Nomarl","light"]
table.add_row(["USDJPY",max(data["USDJPY LIGHT"]), max(data["USDJPY"])])
table.add_row(["MXNJPY", max(data["MXNJPY"]),max(data["MXNJPY LIGHT"])])
print("max spreads")
print(table)


pylot.plot(data["time"],data["MXNJPY"]);pylot.show()
pylot.plot(data["time"],data["USDJPY"]);pylot.show()
import os

folder_path = "/Users/vanshaj/Work/GitHub/Quant_Labs/Projects/Exploratory Market Analysis/src/data"  

data_path = {}
all_items = os.listdir(folder_path)

for item in all_items:
    item_path = os.path.join(folder_path, item)
    if os.path.isfile(item_path):
        data_path[item] = item_path

print(data_path)
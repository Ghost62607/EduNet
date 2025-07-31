import random

list_of_cell = []
for i in range(0,8):
    list_of_cell.append(input("Enter your cell type:"))
'''print(list_of_cell)'''

cells_data = {}

for idx, cell_type in enumerate(list_of_cell,start=1):
    cell_key = f"cell_{idx}_{cell_type}"
    
    voltage = 3.2 if cell_type == "lfp" else 3.6
    current = 0.0
    temp = round(random.uniform(25,40),1)
    capacity = round(voltage*current,2)
    
    cells_data[cell_key] = {
        "voltage": voltage,
        "current":current,
        "temp":temp,
        "capacity":capacity
        }
    
for key , values in cells_data.items():
    print(f"{key}:{values}")

for key in cell_data:
    current = float(input(f"entrer current values for {key}"))
    voltage = cells_data[key]['voltage']
    cells_data[key]["current"]= current
    cells_data[key]["capacity"] = round(voltage*current,2)

for key , values in cells_data.items():
    print(f"{key}:{values}")

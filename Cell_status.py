import random
import os
from typing import Dict, Any

class BatteryCellMonitor:
    def __init__(self):
        self.cells_data: Dict[str, Dict[str, Any]] = {}
        self.valid_cell_types = ["lfp", "li-ion", "nicad", "nimh", "lead-acid"]
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display program header"""
        print("=" * 60)
        print("          BATTERY CELL STATUS MONITOR")
        print("=" * 60)
        print()
    
    def get_cell_types(self):
        """Interactive cell type input with validation"""
        print("📋 STEP 1: Enter Cell Types")
        print(f"Valid cell types: {', '.join(self.valid_cell_types)}")
        print("(Press Enter without input to finish, minimum 1 cell required)")
        print("-" * 50)
        
        list_of_cells = []
        cell_count = 1
        
        while True:
            if len(list_of_cells) >= 8:
                print("⚠️  Maximum 8 cells reached!")
                break
                
            cell_type = input(f"Enter cell type #{cell_count} (or press Enter to finish): ").strip().lower()
            
            if not cell_type:
                if len(list_of_cells) == 0:
                    print("❌ At least one cell is required!")
                    continue
                else:
                    break
            
            if cell_type not in self.valid_cell_types:
                print(f"❌ Invalid cell type! Use one of: {', '.join(self.valid_cell_types)}")
                continue
            
            list_of_cells.append(cell_type)
            print(f"✅ Added {cell_type} cell")
            cell_count += 1
        
        return list_of_cells
    
    def initialize_cells(self, cell_types):
        """Initialize cell data with default values"""
        print(f"\n🔋 STEP 2: Initializing {len(cell_types)} cells...")
        print("-" * 50)
        
        for idx, cell_type in enumerate(cell_types, start=1):
            cell_key = f"cell_{idx}_{cell_type}"
            
            # Set default voltage based on cell type
            voltage_map = {
                "lfp": 3.2,
                "li-ion": 3.6,
                "nicad": 1.2,
                "nimh": 1.2,
                "lead-acid": 2.0
            }
            
            voltage = voltage_map.get(cell_type, 3.6)
            current = 0.0
            temp = round(random.uniform(25, 40), 1)
            capacity = round(voltage * current, 2)
            
            self.cells_data[cell_key] = {
                "voltage": voltage,
                "current": current,
                "temp": temp,
                "capacity": capacity,
                "status": "Initialized"
            }
            
            print(f"✅ {cell_key}: V={voltage}V, T={temp}°C")
    
    def display_cells_table(self):
        """Display cells data in a formatted table"""
        print("\n📊 CURRENT CELL STATUS")
        print("-" * 80)
        print(f"{'Cell ID':<20} {'Voltage':<10} {'Current':<10} {'Temp':<10} {'Capacity':<12} {'Status':<10}")
        print("-" * 80)
        
        for cell_id, data in self.cells_data.items():
            print(f"{cell_id:<20} {data['voltage']:<10}V {data['current']:<10}A "
                  f"{data['temp']:<10}°C {data['capacity']:<12}Wh {data['status']:<10}")
        print("-" * 80)
    
    def update_current_values(self):
        """Interactive current value updates"""
        print("\n⚡ STEP 3: Update Current Values")
        print("(Enter 0 to skip a cell, or 'q' to quit updating)")
        print("-" * 50)
        
        for cell_id in self.cells_data.keys():
            while True:
                try:
                    current_input = input(f"Enter current for {cell_id} (A): ").strip()
                    
                    if current_input.lower() == 'q':
                        print("🛑 Stopped updating currents")
                        return
                    
                    current = float(current_input)
                    
                    if current < 0:
                        print("❌ Current cannot be negative!")
                        continue
                    
                    # Update current and recalculate capacity
                    voltage = self.cells_data[cell_id]['voltage']
                    self.cells_data[cell_id]["current"] = current
                    self.cells_data[cell_id]["capacity"] = round(voltage * current, 2)
                    
                    # Update status
                    if current > 0:
                        self.cells_data[cell_id]["status"] = "Active"
                    else:
                        self.cells_data[cell_id]["status"] = "Standby"
                    
                    print(f"✅ Updated {cell_id}: {current}A -> {self.cells_data[cell_id]['capacity']}Wh")
                    break
                    
                except ValueError:
                    print("❌ Please enter a valid number!")
    
    def interactive_menu(self):
        """Main interactive menu"""
        while True:
            print("\n🔧 INTERACTIVE MENU")
            print("-" * 30)
            print("1. View Cell Status")
            print("2. Update Cell Current")
            print("3. Add New Cell")
            print("4. Remove Cell")
            print("5. Export Data")
            print("6. Clear Screen")
            print("0. Exit Program")
            print("-" * 30)
            
            choice = input("Select an option (0-6): ").strip()
            
            if choice == "1":
                self.display_cells_table()
            elif choice == "2":
                self.update_single_cell_current()
            elif choice == "3":
                self.add_new_cell()
            elif choice == "4":
                self.remove_cell()
            elif choice == "5":
                self.export_data()
            elif choice == "6":
                self.clear_screen()
                self.display_header()
            elif choice == "0":
                print("👋 Thank you for using Battery Cell Monitor!")
                break
            else:
                print("❌ Invalid option! Please try again.")
    
    def update_single_cell_current(self):
        """Update current for a specific cell"""
        if not self.cells_data:
            print("❌ No cells available!")
            return
        
        print("\nAvailable cells:")
        for i, cell_id in enumerate(self.cells_data.keys(), 1):
            print(f"{i}. {cell_id}")
        
        try:
            cell_num = int(input("Enter cell number to update: ")) - 1
            cell_id = list(self.cells_data.keys())[cell_num]
            
            current = float(input(f"Enter new current for {cell_id} (A): "))
            if current < 0:
                print("❌ Current cannot be negative!")
                return
            
            voltage = self.cells_data[cell_id]['voltage']
            self.cells_data[cell_id]["current"] = current
            self.cells_data[cell_id]["capacity"] = round(voltage * current, 2)
            self.cells_data[cell_id]["status"] = "Active" if current > 0 else "Standby"
            
            print(f"✅ Updated {cell_id} successfully!")
            
        except (ValueError, IndexError):
            print("❌ Invalid selection!")
    
    def add_new_cell(self):
        """Add a new cell to the system"""
        if len(self.cells_data) >= 8:
            print("❌ Maximum 8 cells reached!")
            return
        
        print(f"Valid cell types: {', '.join(self.valid_cell_types)}")
        cell_type = input("Enter new cell type: ").strip().lower()
        
        if cell_type not in self.valid_cell_types:
            print("❌ Invalid cell type!")
            return
        
        cell_num = len(self.cells_data) + 1
        cell_id = f"cell_{cell_num}_{cell_type}"
        
        voltage_map = {"lfp": 3.2, "li-ion": 3.6, "nicad": 1.2, "nimh": 1.2, "lead-acid": 2.0}
        voltage = voltage_map.get(cell_type, 3.6)
        
        self.cells_data[cell_id] = {
            "voltage": voltage,
            "current": 0.0,
            "temp": round(random.uniform(25, 40), 1),
            "capacity": 0.0,
            "status": "Initialized"
        }
        
        print(f"✅ Added new cell: {cell_id}")
    
    def remove_cell(self):
        """Remove a cell from the system"""
        if not self.cells_data:
            print("❌ No cells to remove!")
            return
        
        print("\nAvailable cells:")
        for i, cell_id in enumerate(self.cells_data.keys(), 1):
            print(f"{i}. {cell_id}")
        
        try:
            cell_num = int(input("Enter cell number to remove: ")) - 1
            cell_id = list(self.cells_data.keys())[cell_num]
            
            confirm = input(f"Are you sure you want to remove {cell_id}? (y/N): ").strip().lower()
            if confirm == 'y':
                del self.cells_data[cell_id]
                print(f"✅ Removed {cell_id}")
            else:
                print("❌ Removal cancelled")
                
        except (ValueError, IndexError):
            print("❌ Invalid selection!")
    
    def export_data(self):
        """Export cell data to a file"""
        filename = input("Enter filename (without extension): ").strip() or "cell_data"
        filename += ".txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("Battery Cell Status Report\n")
                f.write("=" * 50 + "\n\n")
                
                for cell_id, data in self.cells_data.items():
                    f.write(f"{cell_id}:\n")
                    for key, value in data.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
            
            print(f"✅ Data exported to {filename}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def run(self):
        """Main program execution"""
        self.clear_screen()
        self.display_header()
        
        # Step 1: Get cell types
        cell_types = self.get_cell_types()
        
        # Step 2: Initialize cells
        self.initialize_cells(cell_types)
        
        # Step 3: Display initial status
        self.display_cells_table()
        
        # Step 4: Update currents
        update_choice = input("\nWould you like to update current values now? (y/N): ").strip().lower()
        if update_choice == 'y':
            self.update_current_values()
            self.display_cells_table()
        
        # Step 5: Interactive menu
        self.interactive_menu()

# Run the program
if __name__ == "__main__":
    monitor = BatteryCellMonitor()
    monitor.run()

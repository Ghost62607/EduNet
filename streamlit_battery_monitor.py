import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import random
import numpy as np
from datetime import datetime, timedelta
import json
import os
import time

# Page configuration
st.set_page_config(
    page_title="Battery Cell Data Logger",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS for clean UI
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    
    .status-good { border-left-color: #2ca02c; }
    .status-warning { border-left-color: #ff7f0e; }
    .status-critical { border-left-color: #d62728; }
    
    .data-info {
        background-color: #e8f4f8;
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'cells_data' not in st.session_state:
        st.session_state.cells_data = {}
    if 'historical_data' not in st.session_state:
        st.session_state.historical_data = pd.DataFrame()
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    if 'simulation_running' not in st.session_state:
        st.session_state.simulation_running = False
    if 'data_file_path' not in st.session_state:
        st.session_state.data_file_path = "battery_data_log.csv"
    if 'recording_enabled' not in st.session_state:
        st.session_state.recording_enabled = False
    if 'last_record_time' not in st.session_state:
        st.session_state.last_record_time = None

init_session_state()

def get_cell_status(voltage, min_voltage, max_voltage):
    """Determine cell status based on voltage"""
    voltage_percent = (voltage - min_voltage) / (max_voltage - min_voltage) * 100
    if voltage_percent < 20:
        return ("Critical", "status-critical")
    elif voltage_percent < 50:
        return ("Warning", "status-warning")
    else:
        return ("Good", "status-good")

def create_cell_data(cell_type, cell_id):
    """Create cell data based on type"""
    base_configs = {
        "lfp": {"voltage": 3.2, "min_voltage": 2.8, "max_voltage": 3.6},
        "li-ion": {"voltage": 3.6, "min_voltage": 3.2, "max_voltage": 4.0},
        "lipo": {"voltage": 3.7, "min_voltage": 3.0, "max_voltage": 4.2},
        "nicd": {"voltage": 1.2, "min_voltage": 1.0, "max_voltage": 1.4},
        "nimh": {"voltage": 1.25, "min_voltage": 1.0, "max_voltage": 1.45}
    }
    
    config = base_configs.get(cell_type.lower(), base_configs["li-ion"])
    
    return {
        "type": cell_type,
        "voltage": round(random.uniform(config["min_voltage"], config["max_voltage"]), 3),
        "current": round(random.uniform(-5.0, 5.0), 3),
        "temp": round(random.uniform(25, 45), 2),
        "min_voltage": config["min_voltage"],
        "max_voltage": config["max_voltage"],
        "capacity": round(random.uniform(80, 100), 2),
        "cycle_count": random.randint(0, 1000),
        "resistance": round(random.uniform(0.01, 0.1), 4),
        "power": 0.0,
        "energy": round(random.uniform(10, 50), 2),
        "soc": round(random.uniform(20, 100), 1),  # State of Charge
        "soh": round(random.uniform(80, 100), 1),  # State of Health
        "timestamp": datetime.now()
    }

def update_cell_data():
    """Simulate real-time data updates"""
    for cell_id in st.session_state.cells_data:
        cell = st.session_state.cells_data[cell_id]
        
        # Simulate voltage fluctuation based on task
        current_task = st.session_state.tasks[0] if st.session_state.tasks else "IDLE"
        
        if current_task == "CC_CV":  # Charging
            voltage_change = random.uniform(0.0, 0.02)
        elif current_task == "CC_CD":  # Discharging
            voltage_change = random.uniform(-0.02, 0.0)
        else:  # IDLE
            voltage_change = random.uniform(-0.01, 0.01)
            
        new_voltage = cell["voltage"] + voltage_change
        cell["voltage"] = round(max(cell["min_voltage"], min(cell["max_voltage"], new_voltage)), 3)
        
        # Update current based on task
        if current_task == "CC_CV":
            cell["current"] = round(random.uniform(0.5, 3.0), 3)
        elif current_task == "CC_CD":
            cell["current"] = round(random.uniform(-3.0, -0.5), 3)
        else:
            cell["current"] = round(random.uniform(-0.5, 0.5), 3)
        
        # Simulate temperature changes
        temp_change = random.uniform(-0.5, 0.5)
        cell["temp"] = round(max(15, min(65, cell["temp"] + temp_change)), 2)
        
        # Calculate power
        cell["power"] = round(cell["voltage"] * cell["current"], 3)
        
        # Update capacity and SOC based on voltage
        voltage_ratio = (cell["voltage"] - cell["min_voltage"]) / (cell["max_voltage"] - cell["min_voltage"])
        cell["capacity"] = round(voltage_ratio * 100, 2)
        cell["soc"] = round(max(0, min(100, voltage_ratio * 100)), 1)
        
        # Simulate resistance changes
        cell["resistance"] = round(max(0.005, cell["resistance"] + random.uniform(-0.001, 0.001)), 4)
        
        # Update timestamp
        cell["timestamp"] = datetime.now()

def record_data_to_csv():
    """Record current cell data to CSV file with timestamp"""
    if not st.session_state.cells_data:
        return False
    
    # Prepare data for recording
    records = []
    current_time = datetime.now()
    
    for cell_id, cell_data in st.session_state.cells_data.items():
        record = {
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'cell_id': cell_id,
            'cell_type': cell_data['type'],
            'voltage': cell_data['voltage'],
            'current': cell_data['current'],
            'temperature': cell_data['temp'],
            'capacity': cell_data['capacity'],
            'power': cell_data['power'],
            'resistance': cell_data['resistance'],
            'soc': cell_data['soc'],
            'soh': cell_data['soh'],
            'energy': cell_data['energy'],
            'cycle_count': cell_data['cycle_count'],
            'task': st.session_state.task_assignments.get(cell_id, "IDLE")  # Individual task
        }
        records.append(record)
    
    # Convert to DataFrame
    new_data = pd.DataFrame(records)
    
    # Append to existing CSV or create new one
    try:
        if os.path.exists(st.session_state.data_file_path):
            # Append to existing file
            new_data.to_csv(st.session_state.data_file_path, mode='a', header=False, index=False)
        else:
            # Create new file with headers
            new_data.to_csv(st.session_state.data_file_path, index=False)
        
        # Update historical data in session state
        if st.session_state.historical_data.empty:
            st.session_state.historical_data = new_data
        else:
            st.session_state.historical_data = pd.concat([st.session_state.historical_data, new_data], 
                                                        ignore_index=True)
        
        st.session_state.last_record_time = current_time
        return True
    except Exception as e:
        st.error(f"Error recording data: {str(e)}")
        return False

def load_historical_data():
    """Load historical data from CSV file"""
    try:
        if os.path.exists(st.session_state.data_file_path):
            df = pd.read_csv(st.session_state.data_file_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            st.session_state.historical_data = df
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Main header
st.title("🔋 Battery Cell Data Logger & Monitoring System")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Data recording settings
    st.subheader("📊 Data Recording")
    
    data_file = st.text_input("Data File Name", value=st.session_state.data_file_path)
    if data_file != st.session_state.data_file_path:
        st.session_state.data_file_path = data_file
    
    st.session_state.recording_enabled = st.checkbox("Enable Data Recording", 
                                                     value=st.session_state.recording_enabled)
    
    recording_interval = st.selectbox("Recording Interval", 
                                     ["1 second", "5 seconds", "10 seconds", "30 seconds", "1 minute"],
                                     index=2)
    
    # Convert interval to seconds
    interval_map = {"1 second": 1, "5 seconds": 5, "10 seconds": 10, 
                   "30 seconds": 30, "1 minute": 60}
    record_interval_sec = interval_map[recording_interval]
    
    # Cell configuration
    st.subheader("🔧 Cell Setup")
    num_cells = st.number_input("Number of Cells", min_value=1, max_value=50, value=3)
    
    cell_types = ["LFP", "Li-Ion", "LiPo", "NiCd", "NiMH"]
    
    # Batch cell configuration
    batch_config = st.selectbox("Batch Configuration", 
                               ["Individual", "All Same Type", "Mixed Pack"])
    
    if batch_config == "All Same Type":
        default_type = st.selectbox("Cell Type for All", cell_types)
        cell_configs = [default_type] * num_cells
    elif batch_config == "Mixed Pack":
        # Predefined mixed configurations
        if num_cells <= 3:
            cell_configs = ["Li-Ion"] * num_cells
        else:
            cell_configs = (["Li-Ion"] * (num_cells//2) + 
                          ["LFP"] * (num_cells - num_cells//2))
    else:
        # Individual configuration
        cell_configs = []
        for i in range(min(num_cells, 10)):  # Limit UI elements
            cell_type = st.selectbox(f"Cell {i+1}", cell_types, key=f"cell_type_{i}")
            cell_configs.append(cell_type)
        
        # Fill remaining cells with Li-Ion if more than 10
        if num_cells > 10:
            cell_configs.extend(["Li-Ion"] * (num_cells - 10))
            st.info(f"Cells 11-{num_cells} set to Li-Ion (default)")
    
    # Initialize cells
    if st.button("🔄 Initialize Cells", type="primary"):
        st.session_state.cells_data = {}
        for i in range(num_cells):
            cell_type = cell_configs[i] if i < len(cell_configs) else "Li-Ion"
            cell_id = f"cell_{i+1:02d}_{cell_type.lower()}"
            st.session_state.cells_data[cell_id] = create_cell_data(cell_type, cell_id)
        st.success(f"✅ {num_cells} cells initialized!")
    
    # Task configuration
    st.subheader("⚡ Task Management")
    task_options = ["CC_CV", "IDLE", "CC_CD", "CCCV_CYCLE", "PULSE_TEST", "IMPEDANCE_TEST", "SELF_DISCHARGE"]
    
    # Task assignment mode
    task_mode = st.radio("Task Assignment Mode", 
                        ["Single Task (All Cells)", "Individual Tasks", "Group Tasks"],
                        horizontal=True)
    
    # Initialize task assignments if not exists
    if 'task_assignments' not in st.session_state:
        st.session_state.task_assignments = {}
    
    if task_mode == "Single Task (All Cells)":
        # Single task for all cells
        selected_task = st.selectbox("Task for All Cells", task_options)
        
        if st.button("📋 Apply to All Cells"):
            for cell_id in st.session_state.cells_data.keys():
                st.session_state.task_assignments[cell_id] = selected_task
            st.session_state.tasks = [selected_task]  # Keep for backward compatibility
            st.success(f"Task '{selected_task}' applied to all cells!")
    
    elif task_mode == "Individual Tasks":
        # Individual task for each cell
        st.write("**Assign tasks to individual cells:**")
        
        if st.session_state.cells_data:
            individual_tasks = {}
            
            # Create columns for better layout
            cells_list = list(st.session_state.cells_data.keys())
            num_cols = min(2, len(cells_list))
            cols = st.columns(num_cols)
            
            for idx, cell_id in enumerate(cells_list):
                with cols[idx % num_cols]:
                    current_task = st.session_state.task_assignments.get(cell_id, "IDLE")
                    task = st.selectbox(f"{cell_id}", task_options, 
                                      index=task_options.index(current_task) if current_task in task_options else 1,
                                      key=f"individual_task_{cell_id}")
                    individual_tasks[cell_id] = task
            
            if st.button("📋 Apply Individual Tasks"):
                st.session_state.task_assignments = individual_tasks
                st.session_state.tasks = list(set(individual_tasks.values()))  # Unique tasks
                st.success("Individual tasks applied!")
        else:
            st.info("Initialize cells first to assign individual tasks")
    
    else:  # Group Tasks
        # Group-based task assignment
        st.write("**Create task groups:**")
        
        if st.session_state.cells_data:
            # Group creation interface
            num_groups = st.number_input("Number of Task Groups", min_value=1, max_value=5, value=2)
            
            group_assignments = {}
            cells_list = list(st.session_state.cells_data.keys())
            
            for group_num in range(num_groups):
                st.write(f"**Group {group_num + 1}:**")
                group_col1, group_col2 = st.columns([2, 1])
                
                with group_col1:
                    # Multi-select for cells in this group
                    available_cells = [cell for cell in cells_list if cell not in group_assignments]
                    selected_cells = st.multiselect(
                        f"Select cells for Group {group_num + 1}",
                        available_cells,
                        key=f"group_{group_num}_cells"
                    )
                
                with group_col2:
                    # Task for this group
                    group_task = st.selectbox(
                        f"Task for Group {group_num + 1}",
                        task_options,
                        key=f"group_{group_num}_task"
                    )
                
                # Assign cells to this group
                for cell in selected_cells:
                    group_assignments[cell] = group_task
            
            # Show unassigned cells
            unassigned_cells = [cell for cell in cells_list if cell not in group_assignments]
            if unassigned_cells:
                st.warning(f"Unassigned cells: {', '.join(unassigned_cells)}")
                default_task = st.selectbox("Default task for unassigned cells", task_options, index=1)
                for cell in unassigned_cells:
                    group_assignments[cell] = default_task
            
            if st.button("📋 Apply Group Tasks"):
                st.session_state.task_assignments = group_assignments
                st.session_state.tasks = list(set(group_assignments.values()))  # Unique tasks
                st.success("Group tasks applied!")
        else:
            st.info("Initialize cells first to create task groups")
    
    # Display current task assignments
    if st.session_state.task_assignments:
        with st.expander("📋 Current Task Assignments"):
            task_summary = {}
            for cell_id, task in st.session_state.task_assignments.items():
                if task not in task_summary:
                    task_summary[task] = []
                task_summary[task].append(cell_id)
            
            for task, cells in task_summary.items():
                st.write(f"**{task}:** {', '.join(cells)}")
    
    # Advanced task parameters
    with st.expander("⚙️ Advanced Task Parameters"):
        # Global parameters that apply to all relevant tasks
        st.write("**Charging Parameters:**")
        charge_current = st.slider("Charge Current (A)", 0.1, 10.0, 2.0, key="global_charge_current")
        charge_voltage = st.slider("Charge Cutoff Voltage (V)", 3.0, 4.5, 4.2, key="global_charge_voltage")
        
        st.write("**Discharging Parameters:**")
        discharge_current = st.slider("Discharge Current (A)", 0.1, 10.0, 2.0, key="global_discharge_current")
        discharge_voltage = st.slider("Discharge Cutoff Voltage (V)", 2.5, 3.5, 2.8, key="global_discharge_voltage")
        
        st.write("**Test Parameters:**")
        pulse_duration = st.slider("Pulse Duration (s)", 1, 60, 10, key="pulse_duration")
        rest_duration = st.slider("Rest Duration (s)", 1, 300, 30, key="rest_duration")
        
        # Store parameters in session state
        st.session_state.task_params = {
            'charge_current': charge_current,
            'charge_voltage': charge_voltage,
            'discharge_current': discharge_current,
            'discharge_voltage': discharge_voltage,
            'pulse_duration': pulse_duration,
            'rest_duration': rest_duration
        }
    
    # Simulation controls
    st.subheader("🎮 Simulation")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.simulation_running = True
    with col2:
        if st.button("⏸️ Stop", use_container_width=True):
            st.session_state.simulation_running = False
    
    # Manual actions
    if st.button("🔄 Update Data", use_container_width=True):
        if st.session_state.cells_data:
            update_cell_data()
            st.success("Data updated!")
    
    if st.button("💾 Record Now", use_container_width=True):
        if st.session_state.cells_data:
            if record_data_to_csv():
                st.success("Data recorded to CSV!")
            else:
                st.error("Failed to record data!")
    
    # Data management
    st.subheader("📁 Data Management")
    
    if st.button("📂 Load Historical Data"):
        df = load_historical_data()
        if not df.empty:
            st.success(f"Loaded {len(df)} records")
        else:
            st.info("No historical data found")
    
    if st.button("🗑️ Clear Session Data"):
        st.session_state.cells_data = {}
        st.session_state.historical_data = pd.DataFrame()
        st.session_state.tasks = []
        st.session_state.simulation_running = False
        st.success("Session data cleared!")
    
    # Download options
    st.subheader("⬇️ Download Data")
    
    download_col1, download_col2 = st.columns(2)
    
    with download_col1:
        # Download current data
        if st.session_state.cells_data:
            current_data_df = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
            current_data_df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_csv = current_data_df.to_csv(index=True)
            
            st.download_button(
                label="📊 Download Current Data",
                data=current_csv,
                file_name=f"current_battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with download_col2:
        # Download historical data
        if not st.session_state.historical_data.empty:
            historical_csv = st.session_state.historical_data.to_csv(index=False)
            
            st.download_button(
                label="📈 Download Historical Data",
                data=historical_csv,
                file_name=f"historical_battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No historical data to download")
    
    # Download complete dataset (if CSV file exists)
    if os.path.exists(st.session_state.data_file_path):
        try:
            with open(st.session_state.data_file_path, 'r') as file:
                complete_csv = file.read()
            
            file_size = len(complete_csv)
            file_size_mb = file_size / (1024 * 1024)
            
            st.download_button(
                label=f"💾 Download Complete Dataset ({file_size_mb:.2f} MB)",
                data=complete_csv,
                file_name=f"complete_{st.session_state.data_file_path}",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

# Main dashboard area
if st.session_state.cells_data:
    
    # Auto-update and record when simulation is running
    if st.session_state.simulation_running:
        update_cell_data()
        
        # Auto-record based on interval
        if (st.session_state.recording_enabled and 
            (st.session_state.last_record_time is None or 
             (datetime.now() - st.session_state.last_record_time).total_seconds() >= record_interval_sec)):
            record_data_to_csv()
    
    # System overview metrics
    st.subheader("📊 System Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_cells = len(st.session_state.cells_data)
    avg_voltage = np.mean([cell["voltage"] for cell in st.session_state.cells_data.values()])
    avg_current = np.mean([cell["current"] for cell in st.session_state.cells_data.values()])
    avg_temp = np.mean([cell["temp"] for cell in st.session_state.cells_data.values()])
    total_power = sum([cell["power"] for cell in st.session_state.cells_data.values()])
    
    with col1:
        st.metric("🔋 Total Cells", total_cells)
    with col2:
        st.metric("⚡ Avg Voltage", f"{avg_voltage:.3f}V")
    with col3:
        st.metric("🔄 Avg Current", f"{avg_current:.3f}A")
    with col4:
        st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C")
    with col5:
        st.metric("⚡ Total Power", f"{total_power:.2f}W")
    
    # Status indicators
    status_info = []
    for cell_id, cell_data in st.session_state.cells_data.items():
        status, status_class = get_cell_status(cell_data["voltage"], 
                                             cell_data["min_voltage"], 
                                             cell_data["max_voltage"])
        status_info.append(status)
    
    status_counts = pd.Series(status_info).value_counts()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟢 Good Cells", status_counts.get("Good", 0))
    with col2:
        st.metric("🟡 Warning Cells", status_counts.get("Warning", 0))
    with col3:
        st.metric("🔴 Critical Cells", status_counts.get("Critical", 0))
    
    # Recording status
    if st.session_state.recording_enabled:
        record_count = len(st.session_state.historical_data) if not st.session_state.historical_data.empty else 0
        st.info(f"🔴 Recording enabled | {record_count} records | Interval: {recording_interval} | File: {st.session_state.data_file_path}")
    else:
        st.info("⚪ Recording disabled")
    
    # Current task display - show all active tasks
    if st.session_state.task_assignments:
        active_tasks = list(set(st.session_state.task_assignments.values()))
        if len(active_tasks) == 1:
            st.info(f"⚡ Current Task: **{active_tasks[0]}** (All Cells)")
        else:
            tasks_summary = []
            task_counts = {}
            for task in st.session_state.task_assignments.values():
                task_counts[task] = task_counts.get(task, 0) + 1
            
            for task, count in task_counts.items():
                tasks_summary.append(f"**{task}** ({count} cells)")
            
            st.info(f"⚡ Active Tasks: {' | '.join(tasks_summary)}")
    elif st.session_state.tasks:
        st.info(f"⚡ Current Task: **{st.session_state.tasks[0]}**")
    
    # Detailed cell data table
    st.subheader("📋 Cell Data Table")
    
    # Convert current data to DataFrame for display
    display_data = []
    for cell_id, cell_data in st.session_state.cells_data.items():
        status, _ = get_cell_status(cell_data["voltage"], 
                                  cell_data["min_voltage"], 
                                  cell_data["max_voltage"])
        
        # Get individual task for this cell
        individual_task = st.session_state.task_assignments.get(cell_id, "IDLE")
        
        display_data.append({
            'Cell ID': cell_id,
            'Type': cell_data['type'],
            'Task': individual_task,
            'Status': status,
            'Voltage (V)': cell_data['voltage'],
            'Current (A)': cell_data['current'],
            'Power (W)': cell_data['power'],
            'Temperature (°C)': cell_data['temp'],
            'SOC (%)': cell_data['soc'],
            'SOH (%)': cell_data['soh'],
            'Resistance (Ω)': cell_data['resistance'],
            'Cycles': cell_data['cycle_count'],
            'Energy (Wh)': cell_data['energy']
        })
    
    current_df = pd.DataFrame(display_data)
    
    # Color code the status
    def color_status(val):
        if val == 'Good':
            return 'background-color: #d4edda'
        elif val == 'Warning':
            return 'background-color: #fff3cd'
        elif val == 'Critical':
            return 'background-color: #f8d7da'
        return ''
    
    styled_df = current_df.style.applymap(color_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True, height=300)
    
    # Multiple graph types
    st.subheader("📈 Data Visualization")
    
    # Graph type selection
    col1, col2 = st.columns([3, 1])
    with col1:
        graph_tabs = st.tabs(["📊 Current Metrics", "📈 Time Series", "🔄 Comparison", "📉 Distribution", "🗺️ Correlation"])
    with col2:
        auto_refresh = st.checkbox("Auto Refresh Charts", value=st.session_state.simulation_running)
    
    # Tab 1: Current Metrics
    with graph_tabs[0]:
        metric_type = st.selectbox("Select Metric", 
                                  ["Voltage", "Current", "Power", "Temperature", "SOC", "Resistance"])
        
        # Create different chart types for current data
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Bar chart
            cell_names = list(st.session_state.cells_data.keys())
            if metric_type == "Voltage":
                values = [st.session_state.cells_data[cell]["voltage"] for cell in cell_names]
                unit = "V"
            elif metric_type == "Current":
                values = [st.session_state.cells_data[cell]["current"] for cell in cell_names]
                unit = "A"
            elif metric_type == "Power":
                values = [st.session_state.cells_data[cell]["power"] for cell in cell_names]
                unit = "W"
            elif metric_type == "Temperature":
                values = [st.session_state.cells_data[cell]["temp"] for cell in cell_names]
                unit = "°C"
            elif metric_type == "SOC":
                values = [st.session_state.cells_data[cell]["soc"] for cell in cell_names]
                unit = "%"
            else:  # Resistance
                values = [st.session_state.cells_data[cell]["resistance"] for cell in cell_names]
                unit = "Ω"
            
            fig_bar = px.bar(x=cell_names, y=values, 
                           title=f"{metric_type} by Cell (Bar Chart)",
                           labels={'x': 'Cell ID', 'y': f'{metric_type} ({unit})'})
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with chart_col2:
            # Pie chart for status distribution
            fig_pie = px.pie(values=list(status_counts.values), 
                           names=list(status_counts.index),
                           title="Cell Status Distribution")
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tab 2: Time Series
    with graph_tabs[1]:
        if not st.session_state.historical_data.empty:
            ts_metric = st.selectbox("Time Series Metric", 
                                   ["voltage", "current", "power", "temperature", "soc"],
                                   key="ts_metric")
            
            # Multi-line time series
            fig_ts = px.line(st.session_state.historical_data, 
                           x='timestamp', y=ts_metric, color='cell_id',
                           title=f"{ts_metric.title()} Over Time")
            fig_ts.update_layout(height=500)
            st.plotly_chart(fig_ts, use_container_width=True)
            
            # Show data statistics
            st.write("**Time Series Statistics:**")
            ts_stats = st.session_state.historical_data.groupby('cell_id')[ts_metric].agg(['mean', 'min', 'max', 'std'])
            st.dataframe(ts_stats)
        else:
            st.info("No historical data available. Enable recording and run simulation to collect time series data.")
    
    # Tab 3: Comparison
    with graph_tabs[2]:
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            # Radar chart comparison
            if len(st.session_state.cells_data) >= 2:
                selected_cells = st.multiselect("Select Cells to Compare", 
                                               list(st.session_state.cells_data.keys()),
                                               default=list(st.session_state.cells_data.keys())[:3])
                
                if selected_cells:
                    fig_radar = go.Figure()
                    
                    for cell_id in selected_cells:
                        cell = st.session_state.cells_data[cell_id]
                        # Normalize values for radar chart
                        normalized_values = [
                            (cell["voltage"] - cell["min_voltage"]) / (cell["max_voltage"] - cell["min_voltage"]) * 100,
                            cell["soc"],
                            cell["soh"],
                            min(100, cell["temp"] / 60 * 100),  # Normalize temp to 0-100
                            min(100, abs(cell["current"]) / 5 * 100)  # Normalize current to 0-100
                        ]
                        
                        fig_radar.add_trace(go.Scatterpolar(
                            r=normalized_values,
                            theta=['Voltage %', 'SOC %', 'SOH %', 'Temp %', 'Current %'],
                            fill='toself',
                            name=cell_id
                        ))
                    
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        title="Cell Comparison (Normalized %)",
                        height=500
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
        
        with comp_col2:
            # Box plot for metric distribution
            box_metric = st.selectbox("Box Plot Metric", 
                                    ["voltage", "current", "temperature", "soc"],
                                    key="box_metric")
            
            box_data = []
            for cell_id, cell_data in st.session_state.cells_data.items():
                if box_metric == "voltage":
                    box_data.append(cell_data["voltage"])
                elif box_metric == "current":
                    box_data.append(cell_data["current"])
                elif box_metric == "temperature":
                    box_data.append(cell_data["temp"])
                else:  # soc
                    box_data.append(cell_data["soc"])
            
            fig_box = go.Figure()
            fig_box.add_trace(go.Box(y=box_data, name=box_metric.title()))
            fig_box.update_layout(title=f"{box_metric.title()} Distribution", height=400)
            st.plotly_chart(fig_box, use_container_width=True)
    
    # Tab 4: Distribution
    with graph_tabs[3]:
        hist_col1, hist_col2 = st.columns(2)
        
        with hist_col1:
            # Histogram
            hist_metric = st.selectbox("Histogram Metric", 
                                     ["voltage", "current", "temperature", "power"],
                                     key="hist_metric")
            
            hist_data = []
            for cell_data in st.session_state.cells_data.values():
                if hist_metric == "voltage":
                    hist_data.append(cell_data["voltage"])
                elif hist_metric == "current":
                    hist_data.append(cell_data["current"])
                elif hist_metric == "temperature":
                    hist_data.append(cell_data["temp"])
                else:  # power
                    hist_data.append(cell_data["power"])
            
            fig_hist = px.histogram(x=hist_data, nbins=10, 
                                  title=f"{hist_metric.title()} Distribution")
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with hist_col2:
            # Scatter plot
            if len(st.session_state.cells_data) > 1:
                scatter_x = st.selectbox("X-axis", ["voltage", "current", "temperature"],
                                       key="scatter_x")
                scatter_y = st.selectbox("Y-axis", ["power", "soc", "resistance"],
                                       key="scatter_y")
                
                x_data = [cell[scatter_x if scatter_x != "temperature" else "temp"] 
                         for cell in st.session_state.cells_data.values()]
                y_data = [cell[scatter_y] for cell in st.session_state.cells_data.values()]
                
                fig_scatter = px.scatter(x=x_data, y=y_data,
                                       title=f"{scatter_y.title()} vs {scatter_x.title()}")
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Tab 5: Correlation
    with graph_tabs[4]:
        if len(st.session_state.cells_data) > 2:
            # Create correlation matrix
            corr_data = []
            for cell_data in st.session_state.cells_data.values():
                corr_data.append([
                    cell_data["voltage"],
                    cell_data["current"],
                    cell_data["temp"],
                    cell_data["power"],
                    cell_data["soc"],
                    cell_data["resistance"]
                ])
            
            corr_df = pd.DataFrame(corr_data, 
                                 columns=["Voltage", "Current", "Temperature", 
                                         "Power", "SOC", "Resistance"])
            corr_matrix = corr_df.corr()
            
            fig_corr = px.imshow(corr_matrix, 
                               title="Parameter Correlation Matrix",
                               color_continuous_scale="RdBu")
            fig_corr.update_layout(height=500)
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Need more cells for meaningful correlation analysis")

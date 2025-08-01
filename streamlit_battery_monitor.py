import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import random
import numpy as np
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="⚡ Battery Cell Monitoring System",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for futuristic styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    .main-header {
        font-family: 'Orbitron', monospace;
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(45deg, #00d4ff, #0099cc, #006bb3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 153, 204, 0.1));
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-healthy { background-color: #00ff88; }
    .status-warning { background-color: #ffaa00; }
    .status-critical { background-color: #ff4444; }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .task-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        font-family: 'Orbitron', monospace;
    }
    
    .task-cc-cv { background: linear-gradient(45deg, #4CAF50, #45a049); color: white; }
    .task-idle { background: linear-gradient(45deg, #2196F3, #1976D2); color: white; }
    .task-cc-cd { background: linear-gradient(45deg, #FF9800, #F57C00); color: white; }
    
    .stSelectbox > div > div {
        background-color: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'cells_data' not in st.session_state:
        st.session_state.cells_data = {}
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    if 'simulation_running' not in st.session_state:
        st.session_state.simulation_running = False
    if 'update_counter' not in st.session_state:
        st.session_state.update_counter = 0

init_session_state()

def get_cell_status(voltage, min_voltage, max_voltage):
    """Determine cell status based on voltage"""
    if voltage < min_voltage * 1.1:
        return ("Critical", "status-critical")
    elif voltage < min_voltage * 1.2:
        return ("Warning", "status-warning")
    else:
        return ("Healthy", "status-healthy")

def create_cell_data(cell_type, cell_id):
    """Create cell data based on type"""
    base_configs = {
        "lfp": {"voltage": 3.2, "min_voltage": 2.8, "max_voltage": 3.6},
        "li-ion": {"voltage": 3.6, "min_voltage": 3.2, "max_voltage": 4.0},
        "lipo": {"voltage": 3.7, "min_voltage": 3.0, "max_voltage": 4.2}
    }
    
    config = base_configs.get(cell_type.lower(), base_configs["li-ion"])
    
    return {
        "type": cell_type,
        "voltage": round(random.uniform(config["min_voltage"], config["max_voltage"]), 2),
        "current": round(random.uniform(-5.0, 5.0), 2),
        "temp": round(random.uniform(25, 45), 1),
        "min_voltage": config["min_voltage"],
        "max_voltage": config["max_voltage"],
        "capacity": round(random.uniform(80, 100), 1),
        "cycle_count": random.randint(0, 1000),
        "last_updated": datetime.now().strftime("%H:%M:%S")
    }

def update_cell_data():
    """Simulate real-time data updates"""
    for cell_id in st.session_state.cells_data:
        cell = st.session_state.cells_data[cell_id]
        
        # Simulate voltage fluctuation
        voltage_change = random.uniform(-0.05, 0.05)
        new_voltage = cell["voltage"] + voltage_change
        cell["voltage"] = round(max(cell["min_voltage"], min(cell["max_voltage"], new_voltage)), 2)
        
        # Simulate current changes
        cell["current"] = round(random.uniform(-5.0, 5.0), 2)
        
        # Simulate temperature changes
        temp_change = random.uniform(-1, 1)
        cell["temp"] = round(max(20, min(60, cell["temp"] + temp_change)), 1)
        
        # Update capacity based on voltage
        cell["capacity"] = round((cell["voltage"] / cell["max_voltage"]) * 100, 1)
        
        cell["last_updated"] = datetime.now().strftime("%H:%M:%S")
    
    st.session_state.update_counter += 1

# Main header
st.markdown('<h1 class="main-header">⚡ BATTERY CELL MONITORING SYSTEM</h1>', unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.markdown("### 🔧 System Controls")
    
    # Cell configuration
    st.markdown("#### Cell Configuration")
    num_cells = st.number_input("Number of Cells", min_value=1, max_value=20, value=3)
    
    cell_types = ["LFP", "Li-Ion", "LiPo"]
    
    # Dynamic cell type selection
    cell_configs = []
    for i in range(num_cells):
        cell_type = st.selectbox(f"Cell {i+1} Type", cell_types, key=f"cell_type_{i}")
        cell_configs.append(cell_type)
    
    # Create cells
    if st.button("🔄 Initialize Cells", type="primary"):
        st.session_state.cells_data = {}
        for i, cell_type in enumerate(cell_configs):
            cell_id = f"cell_{i+1}_{cell_type.lower()}"
            st.session_state.cells_data[cell_id] = create_cell_data(cell_type, cell_id)
        st.success(f"✅ {num_cells} cells initialized!")
    
    # Task configuration
    st.markdown("#### Task Configuration")
    task_options = ["CC_CV", "IDLE", "CC_CD"]
    
    num_tasks = st.number_input("Number of Tasks", min_value=0, max_value=10, value=0)
    
    if num_tasks > 0:
        tasks = []
        for i in range(num_tasks):
            task = st.selectbox(f"Task {i+1}", task_options, key=f"task_{i}")
            tasks.append(task)
        
        if st.button("📋 Apply Tasks"):
            st.session_state.tasks = tasks
            st.success("Tasks applied successfully!")
    
    # Simulation controls
    st.markdown("#### Simulation Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start"):
            st.session_state.simulation_running = True
    
    with col2:
        if st.button("⏸️ Stop"):
            st.session_state.simulation_running = False
    
    # Manual update button
    if st.button("🔄 Update Data"):
        if st.session_state.cells_data:
            update_cell_data()
            st.success("Data updated!")
    
    # Display simulation status
    if st.session_state.simulation_running:
        st.success("🟢 Simulation Running")
        if st.session_state.cells_data:
            update_cell_data()  # Auto-update when simulation is running
    else:
        st.info("🔴 Simulation Stopped")

# Main dashboard
if st.session_state.cells_data:
    
    # Create metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    total_cells = len(st.session_state.cells_data)
    avg_voltage = np.mean([cell["voltage"] for cell in st.session_state.cells_data.values()])
    avg_temp = np.mean([cell["temp"] for cell in st.session_state.cells_data.values()])
    avg_capacity = np.mean([cell["capacity"] for cell in st.session_state.cells_data.values()])
    
    with col1:
        st.metric("🔋 Total Cells", total_cells)
    with col2:
        st.metric("⚡ Avg Voltage", f"{avg_voltage:.2f}V")
    with col3:
        st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C")
    with col4:
        st.metric("📊 Avg Capacity", f"{avg_capacity:.1f}%")
    
    # Display update counter
    st.caption(f"🔄 Updates: {st.session_state.update_counter} | Last update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Cell status cards
    st.markdown("### 📱 Cell Status Overview")
    
    # Create columns based on number of cells
    num_cols = min(3, len(st.session_state.cells_data))
    cols = st.columns(num_cols)
    
    for idx, (cell_id, cell_data) in enumerate(st.session_state.cells_data.items()):
        with cols[idx % num_cols]:
            status, status_class = get_cell_status(
                cell_data["voltage"], 
                cell_data["min_voltage"], 
                cell_data["max_voltage"]
            )
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>🔋 {cell_id.upper()}</h4>
                <p><span class="status-indicator {status_class}"></span><strong>Status:</strong> {status}</p>
                <p><strong>Type:</strong> {cell_data['type']}</p>
                <p><strong>Voltage:</strong> {cell_data['voltage']:.2f}V</p>
                <p><strong>Current:</strong> {cell_data['current']:.2f}A</p>
                <p><strong>Temperature:</strong> {cell_data['temp']:.1f}°C</p>
                <p><strong>Capacity:</strong> {cell_data['capacity']:.1f}%</p>
                <p><strong>Cycles:</strong> {cell_data['cycle_count']}</p>
                <p><strong>Updated:</strong> {cell_data['last_updated']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Real-time charts
    st.markdown("### 📈 Real-time Monitoring")
    
    # Create subplots for different metrics
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Voltage Levels', 'Current Flow', 'Temperature', 'Capacity'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Extract data for plotting
    cell_names = list(st.session_state.cells_data.keys())
    voltages = [st.session_state.cells_data[cell]["voltage"] for cell in cell_names]
    currents = [st.session_state.cells_data[cell]["current"] for cell in cell_names]
    temperatures = [st.session_state.cells_data[cell]["temp"] for cell in cell_names]
    capacities = [st.session_state.cells_data[cell]["capacity"] for cell in cell_names]
    
    # Add traces
    fig.add_trace(go.Bar(x=cell_names, y=voltages, name="Voltage", marker_color='#00d4ff'), row=1, col=1)
    fig.add_trace(go.Bar(x=cell_names, y=currents, name="Current", marker_color='#00ff88'), row=1, col=2)
    fig.add_trace(go.Bar(x=cell_names, y=temperatures, name="Temperature", marker_color='#ffaa00'), row=2, col=1)
    fig.add_trace(go.Bar(x=cell_names, y=capacities, name="Capacity", marker_color='#ff6b6b'), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Cell Metrics Dashboard",
        title_font=dict(family="Orbitron", size=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Add y-axis labels
    fig.update_yaxes(title_text="Voltage (V)", row=1, col=1)
    fig.update_yaxes(title_text="Current (A)", row=1, col=2)
    fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)
    fig.update_yaxes(title_text="Capacity (%)", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Task status display
    if st.session_state.tasks:
        st.markdown("### 📋 Active Tasks")
        task_html = ""
        for i, task in enumerate(st.session_state.tasks):
            task_class = f"task-{task.lower().replace('_', '-')}"
            task_html += f'<span class="task-badge {task_class}">Task {i+1}: {task}</span>'
        
        st.markdown(task_html, unsafe_allow_html=True)
    
    # Data table
    with st.expander("📊 Detailed Cell Data"):
        df = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
        # Reorder columns for better display
        column_order = ['type', 'voltage', 'current', 'temp', 'capacity', 'min_voltage', 'max_voltage', 'cycle_count', 'last_updated']
        df = df[column_order]
        st.dataframe(df, use_container_width=True)
    
    # Export functionality and controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Export Data"):
            df = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
            csv = df.to_csv(index=True)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📄 Export JSON"):
            json_data = json.dumps(st.session_state.cells_data, indent=2, default=str)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("🗑️ Clear All Data"):
            st.session_state.cells_data = {}
            st.session_state.tasks = []
            st.session_state.simulation_running = False
            st.session_state.update_counter = 0
            st.success("All data cleared!")

else:
    # Welcome message
    st.markdown("""
    ### 🚀 Welcome to the Battery Cell Monitoring System
    
    This futuristic dashboard allows you to:
    - 🔧 Configure multiple battery cells (LFP, Li-Ion, LiPo)
    - 📊 Monitor real-time voltage, current, temperature, and capacity
    - ⚡ Simulate different charging/discharging tasks
    - 📈 Visualize data with interactive charts
    - 💾 Export data for analysis (CSV & JSON)
    
    **Get started by configuring your cells in the sidebar!**
    """)
    
    # System info
    st.info("💡 **Tip:** Set up your cells first, then use the simulation controls to see live data updates!")

# Auto-refresh for simulation
if st.session_state.simulation_running:
    # This will cause the app to refresh every few seconds when simulation is running
    st.empty().write("")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; font-family: Orbitron; color: #00d4ff;">⚡ Powered by Advanced Battery Analytics ⚡</div>',
    unsafe_allow_html=True
)

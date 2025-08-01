import streamlit as st
import pandas as pd
import random
import json
from datetime import datetime
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Battery Cell Monitor",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StreamlitBatteryCellMonitor:
    def __init__(self):
        self.valid_cell_types = ["lfp", "li-ion", "nicad", "nimh", "lead-acid"]
        self.voltage_map = {
            "lfp": 3.2,
            "li-ion": 3.6,
            "nicad": 1.2,
            "nimh": 1.2,
            "lead-acid": 2.0
        }
        if 'cells_data' not in st.session_state:
            st.session_state.cells_data = {}
        if 'cell_counter' not in st.session_state:
            st.session_state.cell_counter = 0

    def add_cell(self, cell_type):
        if len(st.session_state.cells_data) >= 8:
            return False, "Maximum 8 cells reached!"
        st.session_state.cell_counter += 1
        cell_id = f"cell_{st.session_state.cell_counter}_{cell_type}"
        voltage = self.voltage_map.get(cell_type, 3.6)
        st.session_state.cells_data[cell_id] = {
            "type": cell_type,
            "voltage": voltage,
            "current": 0.0,
            "temp": round(random.uniform(25, 40), 1),
            "capacity": 0.0,
            "status": "Ready",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return True, f"Added new cell: {cell_id}"

    def remove_cell(self, cell_id):
        if cell_id in st.session_state.cells_data:
            del st.session_state.cells_data[cell_id]
            return True, f"Removed cell: {cell_id}"
        return False, "Cell not found!"

    def update_cell_current(self, cell_id, current):
        if cell_id in st.session_state.cells_data:
            voltage = st.session_state.cells_data[cell_id]['voltage']
            st.session_state.cells_data[cell_id]["current"] = current
            st.session_state.cells_data[cell_id]["capacity"] = round(voltage * current, 2)
            st.session_state.cells_data[cell_id]["status"] = "Active" if current > 0 else "Standby"
            return True
        return False

    def get_cells_dataframe(self):
        if not st.session_state.cells_data:
            return pd.DataFrame()
        data = []
        for cell_id, cell_data in st.session_state.cells_data.items():
            row = {"Cell ID": cell_id}
            row.update(cell_data)
            data.append(row)
        return pd.DataFrame(data)

    def export_data(self, format='json'):
        if format == 'json':
            return json.dumps(st.session_state.cells_data, indent=2)
        elif format == 'csv':
            df = self.get_cells_dataframe()
            return df.to_csv(index=False)

def main():
    monitor = StreamlitBatteryCellMonitor()

    st.title("🔋 Battery Cell Status Monitor")
    st.markdown("---")

    with st.sidebar:
        st.header("🛠️ Cell Management")
        cell_type = st.selectbox("Select Cell Type", monitor.valid_cell_types, format_func=str.upper)
        if st.button("➕ Add Cell"):
            success, msg = monitor.add_cell(cell_type)
            if success:
                st.success(msg)
                st.experimental_rerun()
            else:
                st.error(msg)

        st.info(f"Current cells: {len(st.session_state.cells_data)}/8")
        
        st.markdown("---")

        if st.button("🗑️ Clear All"):
            st.session_state.cells_data = {}
            st.session_state.cell_counter = 0
            st.experimental_rerun()

        if st.button("🎲 Random Data"):
            for cell_id in list(st.session_state.cells_data.keys()):
                monitor.update_cell_current(cell_id, round(random.uniform(0,5),2))
            st.experimental_rerun()

    if not st.session_state.cells_data:
        st.info("👆 Add some battery cells using the sidebar to start!")
    else:
        df = monitor.get_cells_dataframe()
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()

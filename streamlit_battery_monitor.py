import streamlit as st
import pandas as pd
import random
import json
from datetime import datetime
import plotly.express as px

# Page configuration
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

    # Sidebar controls
    with st.sidebar:
        st.header("🛠️ Cell Management")

        cell_type = st.selectbox("Select Cell Type", monitor.valid_cell_types, format_func=str.upper)
        if st.button("➕ Add Cell"):
            success, msg = monitor.add_cell(cell_type)
            if success:
                st.success(msg)
            else:
                st.error(msg)
            st.experimental_rerun()

        st.info(f"Current cells: {len(st.session_state.cells_data)}/8")
        st.markdown("---")

        if st.button("🗑️ Clear All"):
            st.session_state.cells_data = {}
            st.session_state.cell_counter = 0
            st.experimental_rerun()

        if st.button("🎲 Random Data"):
            for cell_id in list(st.session_state.cells_data.keys()):
                random_current = round(random.uniform(0, 5), 2)
                monitor.update_cell_current(cell_id, random_current)
            st.experimental_rerun()

    # Main panel
    if not st.session_state.cells_data:
        st.info("👆 Add some battery cells using the sidebar to get started!")
    else:
        df = monitor.get_cells_dataframe()

        # Metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Cells", len(df))
        col2.metric("Active Cells", len(df[df['status'] == 'Active']))
        col3.metric("Total Capacity (Wh)", f"{df['capacity'].sum():.2f}")
        col4.metric("Avg Temperature (°C)", f"{df['temp'].mean():.1f}")
        col5.metric("Total Current (A)", f"{df['current'].sum():.2f}")

        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Cell Status", "⚡ Update Currents", "📈 Analytics", "💾 Export"])

        with tab1:
            st.subheader("Current Cell Status")

            def highlight_status(val):
                if val == 'Active':
                    return 'background-color: #d4edda; color: #155724'
                elif val == 'Standby':
                    return 'background-color: #fff3cd; color: #856404'
                else:
                    return 'background-color: #f8f9fa; color: #6c757d'

            styled_df = df.drop(columns=['created'], errors='ignore').style.applymap(
                highlight_status, subset=['status']
            )
            st.dataframe(styled_df, use_container_width=True)

            st.subheader("🗑️ Remove Individual Cells")
            cell_to_remove = st.selectbox("Select cell to remove", df['Cell ID'].tolist())
            if st.button("Remove Cell"):
                success, msg = monitor.remove_cell(cell_to_remove)
                if success:
                    st.success(msg)
                    st.experimental_rerun()
                else:
                    st.error(msg)

        with tab2:
            st.subheader("⚡ Update Cell Currents")
            with st.form("update_currents_form"):
                updated_currents = {}
                for _, row in df.iterrows():
                    cell_id = row['Cell ID']
                    new_current = st.number_input(
                        f"{cell_id} ({row['type'].upper()}) Current (A)",
                        min_value=0.0,
                        max_value=10.0,
                        value=float(row['current']),
                        step=0.1,
                        key=f"current_{cell_id}"
                    )
                    updated_currents[cell_id] = new_current
                    capacity = row['voltage'] * new_current
                    st.write(f"Estimated Capacity: {capacity:.2f} Wh")
                submitted = st.form_submit_button("🔄 Update All Currents")
                if submitted:
                    for cell_id, current in updated_currents.items():
                        monitor.update_cell_current(cell_id, current)
                    st.success("✅ All currents updated successfully!")
                    st.experimental_rerun()

        with tab3:
            st.subheader("📈 Analytics & Visualizations")
            if len(df) > 0:
                col1, col2 = st.columns(2)

                with col1:
                    capacity_by_type = df.groupby('type')['capacity'].sum().reset_index()
                    fig1 = px.pie(
                        capacity_by_type,
                        values='capacity',
                        names='type',
                        title='Capacity Distribution by Cell Type',
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    fig2 = px.scatter(
                        df,
                        x='voltage',
                        y='current',
                        size='capacity',
                        color='type',
                        title='Current vs Voltage (Size: Capacity)',
                        hover_data=['Cell ID', 'temp', 'status'],
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                fig3 = px.histogram(
                    df,
                    x='temp',
                    color='type',
                    nbins=10,
                    title='Temperature Distribution',
                    template='plotly_dark'
                )
                st.plotly_chart(fig3, use_container_width=True)

                status_counts = df['status'].value_counts()
                fig4 = px.bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    color=status_counts.index,
                    title='Cell Status Summary',
                    template='plotly_dark'
                )
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No data available for analytics")

        with tab4:
            st.subheader("💾 Export Data")
            col1, col2 = st.columns(2)
            with col1:
                json_data = monitor.export_data('json')
                st.download_button(
                    "📥 Download JSON",
                    data=json_data,
                    file_name=f"battery_cells_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                with st.expander("Preview JSON"):
                    st.code(json_data, language="json")
            with col2:
                csv_data = monitor.export_data('csv')
                st.download_button(
                    "📥 Download CSV",
                    data=csv_data,
                    file_name=f"battery_cells_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                with st.expander("Preview CSV"):
                    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#666;'>🔋 Battery Cell Status Monitor | Built with Streamlit</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

import streamlit as st
import random
from PIL import Image

# Demo GIF/meme URLs (replace with your own assets)
futuristic_gif = "https://media.giphy.com/media/xT0Gqjc8p320vQ4cBa/giphy.gif"

st.set_page_config(page_title="⚡ Cell Futurizer 3000 ⚡", layout="wide")

def inject_custom_css():
    st.markdown("""
        <style>
        body {
            background: linear-gradient(120deg, #1a223a 0%, #4e54c8 100%);
            color: #fff;
        }
        .stApp {font-family: 'Segoe UI', sans-serif;}
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Fancy header
st.title("⚡ Welcome to the Cell Futurizer 3000! ⚡")
st.image(futuristic_gif, caption="All systems, go!", use_column_width=True)

with st.expander("🤖 About this App"):
    st.write("A next-gen app where you invent battery cell realities, now with micro-jokes and futuristic flair.")

number_of_cell = st.slider("🔢 How many cells would you like to calibrate?", 1, 20, 3)

list_of_cell = []
st.markdown("### Describe your cell types (dream big!):")
cols = st.columns(number_of_cell)
for i in range(number_of_cell):
    with cols[i]:
        cell_type = st.text_input(f"Type for Cell {i+1}", placeholder="e.g. lfp, unicorn, unobtanium...", key=f"cell_{i}")
        list_of_cell.append(cell_type or f"CellType{i+1}")

# Humor: celebrate user creativity
if "unicorn" in [c.lower() for c in list_of_cell]:
    st.success("🦄 Unicorn cell detected - magical output guaranteed!")

cells_data = {}
for idx, cell_type in enumerate(list_of_cell, start=1):
    key = f"cell_{idx}_{cell_type}"
    voltage = 3.7 if cell_type.lower() == "unicorn" else (3.2 if cell_type.lower() == "lfp" else 3.6)
    min_voltage, max_voltage = (2.7, 4.5) if cell_type.lower() == "unicorn" else \
                              (2.8, 3.6) if cell_type.lower() == "lfp" else (3.2, 4.0)
    temp = round(random.uniform(25, 40), 1)
    capacity = round(voltage * 0.5, 2)
    cells_data[key] = {
        "voltage": voltage, "temp": temp, "capacity": capacity,
        "min_voltage": min_voltage, "max_voltage": max_voltage,
    }

st.markdown("## 🔬 Generated Cells Data")
for key, val in cells_data.items():
    st.info(f"**{key}:** {val}")

# Interactive Task Section
st.markdown("---")
st.subheader("🛰️ Mission Control: Assign Operations")
task_number = st.slider("Number of missions", 1, 5, 2)
tasks = []
for i in range(task_number):
    t = st.selectbox(f"Mission for Task {i+1}", ["CC_CV", "IDLE", "CC_CD", "DEEP_SLEEP", "PARTY_MODE"], key=f"task_{i}")
    tasks.append(t)
st.write(f"Your chosen missions: {tasks}")

# Humor: Easter egg tasks
if "PARTY_MODE" in tasks:
    st.balloons()
    st.warning("🎉 Party mode engaged! Warning: unpredictable levels of fun ahead.")

# Futuristic interaction: animated loading
with st.spinner('Calibrating quantum fields... Please don’t panic 🚀'):
    st.progress(random.randint(60, 100))

st.success("All systems nominal. May your cells power the future!")


import streamlit as st
import pandas as pd
import random

# 1. Page Configuration
st.set_page_config(page_title="Yarn Warehouse Simulation", layout="wide")
st.title("🧵 Yarn Inventory Pegging & Management Simulation")
st.caption("A dynamic supply chain simulation demonstrating allocated vs. unallocated inventory workflows.")

# 2. Initialize Mock Database (Session State)
if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"lot_id": "LOT-101", "type": "Cotton 30s", "color": "Navy Blue", "weight_kg": 500, "tagged_order": "ORD-5001"},
        {"lot_id": "LOT-102", "type": "Polyester 150D", "color": "Crimson", "weight_kg": 350, "tagged_order": "ORD-5002"},
        {"lot_id": "LOT-103", "type": "Cotton 30s", "color": "Navy Blue", "weight_kg": 200, "tagged_order": "Unallocated"},
        {"lot_id": "LOT-104", "type": "Wool Blend", "color": "Charcoal", "weight_kg": 150, "tagged_order": "ORD-5003"},
        {"lot_id": "LOT-105", "type": "Polyester 150D", "color": "Crimson", "weight_kg": 400, "tagged_order": "Unallocated"},
    ]

# Helper function to get unique orders
def get_active_orders():
    orders = set(item["tagged_order"] for item in st.session_state.inventory)
    orders.discard("Unallocated")
    return list(orders)

# 3. Main Dashboard Layout (Metrics)
df = pd.DataFrame(st.session_state.inventory)
total_lots = len(df)
allocated_lots = len(df[df["tagged_order"] != "Unallocated"])
unallocated_lots = total_lots - allocated_lots

m1, m2, m3 = st.columns(3)
m1.metric("Total Yarn Lots", total_lots)
m2.metric("🟢 Allocated Lots", allocated_lots)
m3.metric("🟡 Unallocated Lots", unallocated_lots)

st.divider()

# 4. Inventory Database View
st.subheader("📋 Warehouse Inventory Ledger")
# Highlight unallocated rows for scannability
def highlight_unallocated(row):
    return ['background-color: #fff3cd; color: #856404' if row.tagged_order == 'Unallocated' else '' for _ in row]

st.dataframe(df.style.apply(highlight_unallocated, axis=1), use_container_width=True)

st.divider()

# 5. Simulation Action Panel
st.subheader("⚙️ Simulation Controls")
col1, col2, col3 = st.columns(3)

# --- PANEL 1: PROCUREMENT & INCOMING TAGGING ---
with col1:
    st.markdown("### 📌 1. Receive & Tag Lot")
    with st.form("receive_form", clear_on_submit=True):
        new_lot = f"LOT-{random.randint(106, 999)}"
        yarn_type = st.selectbox("Yarn Type", ["Cotton 30s", "Polyester 150D", "Wool Blend"])
        yarn_color = st.text_input("Color", value="Raw White")
        weight = st.number_input("Weight (KG)", min_value=10, max_value=5000, value=250)
        order_tag = st.text_input("Procured For Order ID (e.g., ORD-5004)", placeholder="Leave blank for Unallocated")
        
        submit_receive = st.form_submit_button("Inbound to Warehouse")
        if submit_receive:
            final_tag = order_tag.strip() if order_tag.strip() != "" else "Unallocated"
            st.session_state.inventory.append({
                "lot_id": new_lot, "type": yarn_type, "color": yarn_color, "weight_kg": weight, "tagged_order": final_tag
            })
            st.success(f"Received {new_lot} pegged to {final_tag}!")
            st.rerun()

# --- PANEL 2: DE-TAGGING (ORDER CANCEL/CHANGE) ---
with col2:
    st.markdown("### 🔓 2. De-Tag / Release Lot")
    active_orders = get_active_orders()
    
    if active_orders:
        selected_order = st.selectbox("Select Altered Customer Order", active_orders)
        # Find lots associated with this order
        associated_lots = [item["lot_id"] for item in st.session_state.inventory if item["tagged_order"] == selected_order]
        selected_lot_to_detag = st.selectbox("Select Lot to Release", associated_lots)
        
        if st.button("Strip Order Tag (De-Tag)", type="primary"):
            for item in st.session_state.inventory:
                if item["lot_id"] == selected_lot_to_detag:
                    item["tagged_order"] = "Unallocated"
            st.warning(f"{selected_lot_to_detag} is now Unallocated Safety Stock.")
            st.rerun()
    else:
        st.info("No currently allocated orders to de-tag.")

# --- PANEL 3: RE-PEGGING (RE-ALLOCATION) ---
with col3:
    st.markdown("### 🔄 3. Re-Peg Unallocated Stock")
    unallocated_lots_list = [item["lot_id"] for item in st.session_state.inventory if item["tagged_order"] == "Unallocated"]
    
    if unallocated_lots_list:
        selected_unallocated = st.selectbox("Select Available Lot", unallocated_lots_list)
        target_order = st.text_input("New Target Order ID (e.g., ORD-7001)")
        
        if st.button("Re-Peg to New Order"):
            if target_order.strip() != "":
                for item in st.session_state.inventory:
                    if item["lot_id"] == selected_unallocated:
                        item["tagged_order"] = target_order.strip()
                st.success(f"{selected_unallocated} successfully re-allocated to {target_order}!")
                st.rerun()
            else:
                st.error("Please enter a valid Target Order ID.")
    else:
        st.info("No unallocated inventory available for re-pegging.")

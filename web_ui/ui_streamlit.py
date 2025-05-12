import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json # Added missing import


# Thiết lập cấu hình trang
st.set_page_config(page_title="Interactive Analytics Dashboard", layout="wide")

# CSS tùy chỉnh - Đã sửa lỗi và cải thiện giao diện
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        .filter-card {
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            border-radius: 0.5rem;
            border-left: 4px solid;
            background-color: #ffffff;
            margin: 0.5rem 0;
            height: 80px; /* Ensure cards in a row have same height */
            display: flex; /* Use flexbox for vertical layout */
            flex-direction: column; /* Stack children vertically */
            justify-content: space-between; /* Space out title, select, badge */
        }
        .filter-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .chart-container {
            height: 450px; /* Increased height slightly */
            background-color: #f8fafc;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-top: 1rem;
            display: flex; /* For centering message */
            flex-direction: column; /* For centering message */
            justify-content: center; /* For centering message */
        }
        .breadcrumb-item:not(:last-child)::after {
            content: "›";
            margin: 0 8px;
            color: #94a3b8;
        }
        .stButton>button {
            background-color: #2563eb;
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
            width: 100%;
            margin: 0.5rem 0;
        }
        .stButton>button:hover {
            background-color: #1d4ed8;
        }
        .summary-card {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            height: 100px; /* Fixed height for summary cards */
        }
        .center-message {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            height: 100%; /* Ensure message takes full chart container height */
        }
        .data-table {
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
            overflow: hidden;
        }
        /* Ensure selectbox label is not shown if we use custom title */
        .stSelectbox label {
            /* display: none !important; /* Uncomment if you want to hide all selectbox labels */
        }
    </style>
""", unsafe_allow_html=True)

# Khởi tạo trạng thái phiên (do this before defining display_names if it depends on session_state)
if 'data_type' not in st.session_state:
    st.session_state.data_type = 'sales'
if 'selections' not in st.session_state:
    st.session_state.selections = {
        'time': {'level': '[]', 'display': 'All Time'},
        'customer': {'level': '[]', 'display': 'All Customers' if st.session_state.data_type == 'sales' else 'All Stores'},
        'item': {'level': '[]', 'display': 'All Items'},
        'geo': {'level': '[]', 'display': 'All Regions'}
    }
if 'visualization_data' not in st.session_state:
    st.session_state.visualization_data = None
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = 'table'

# Dữ liệu và cấu hình
# display_names can now safely use st.session_state as script reruns on data_type change
display_names = {
    'time': {
        '[]': 'All Time',
        '["t.Nam"]': 'Year',
        '["t.Quy"]': 'Quarter',
        '["t.Thang"]': 'Month',
        '["t.Nam", "t.Quy"]': 'Year-Quarter',
        '["t.Nam", "t.Quy", "t.Thang"]': 'Year-Quarter-Month'
    },
    'customer': {
        '[]': 'All Customers' if st.session_state.data_type == 'sales' else 'All Stores',
        '["s.MaCuaHang"]': 'Store'
    },
    'item': {
        '[]': 'All Items',
        '["i.KichCo"]': 'Size',
        '["WeightRange"]': 'Weight Range',
        '["i.MaMH"]': 'Product Code',
        '["i.KichCo", "WeightRange"]': 'Size & Weight'
    },
    'geo': {
        '[]': 'All Regions',
        '["g.Bang"]': 'State',
        '["g.MaThanhPho"]': 'City',
        '["g.Bang", "g.MaThanhPho"]': 'State-City'
    }
}

# Colors for filter cards and badges
filter_colors = {
    'time': {'main': '#3b82f6', 'badge_bg': '#dbeafe', 'badge_text': '#1e40af', 'icon': 'fas fa-calendar-alt'},
    'customer': {'main': '#10b981', 'badge_bg': '#d1fae5', 'badge_text': '#065f46', 'icon': 'fas fa-users'},
    'item': {'main': '#8b5cf6', 'badge_bg': '#ede9fe', 'badge_text': '#5b21b6', 'icon': 'fas fa-box-open'},
    'geo': {'main': '#f59e0b', 'badge_bg': '#ffedd5', 'badge_text': '#9a3412', 'icon': 'fas fa-globe-americas'}
}

# Hàm tạo dữ liệu giả
def generate_mock_data(request_data):
    time_levels = json.loads(request_data['time'])
    customer_levels = json.loads(request_data['customer'])
    item_levels = json.loads(request_data['item'])
    geo_levels = json.loads(request_data['geo'])
    data_points = []
    # Generate between 0 and 15 data points if any dimension is selected, otherwise a small fixed number
    has_selection = any(json.loads(request_data[dim]) for dim in ['time', 'customer', 'item', 'geo'])
    count = np.random.randint(5, 16) if has_selection else 3 + np.random.randint(0,3)
    if not has_selection and request_data['time'] == '[]' and request_data['customer'] == '[]' and request_data['item'] == '[]' and request_data['geo'] == '[]':
        count = 1 # Single row for "All" summary

    base_names = {'time': 'Period', 'customer': 'Cust', 'item': 'Prod', 'geo': 'Loc'}

    for i in range(count):
        point = {}
        # Simplified naming for mock data
        if time_levels:
            point['time'] = '-'.join([f"{level.split('.')[1] if '.' in level else level}_{i+1}" for level in time_levels])
        elif not has_selection and count == 1: point['time'] = "Overall"

        if customer_levels:
             # Adjust label based on data type
            cust_label_prefix = "Cust" if st.session_state.data_type == 'sales' else "Store"
            point['customer'] = '-'.join([f"{cust_label_prefix}_{level.split('.')[-1]}_{i+1}" for level in customer_levels])
        elif not has_selection and count == 1:
             point['customer'] = "All"

        if item_levels:
            point['item'] = '-'.join([f"{level.split('.')[-1] if '.' in level else level}_{i+1}" for level in item_levels])
        elif not has_selection and count == 1: point['item'] = "All"

        if geo_levels:
            point['geo'] = '-'.join([f"{level.split('.')[-1] if '.' in level else level}_{i+1}" for level in geo_levels])
        elif not has_selection and count == 1: point['geo'] = "All"

        # Create meaningful placeholder column names for the 'All' case
        if not (time_levels or customer_levels or item_levels or geo_levels) and count == 1:
            point['Period'] = point.pop('time', 'Overall')
            point['Customer'] = point.pop('customer', 'All')
            point['Item'] = point.pop('item', 'All')
            point['Geography'] = point.pop('geo', 'All')
            # Rename 'Customer' column if inventory data
            if request_data['data_type'] == 'inventory':
                 point['Store'] = point.pop('Customer')


        if request_data['data_type'] == 'sales':
            point['revenue'] = np.random.randint(1000, 100000)
            point['quantity'] = np.random.randint(10, 200)
            point['profit'] = int(point['revenue'] * np.random.uniform(0.1, 0.3))
        else: # inventory
            point['stock'] = np.random.randint(50, 1000)
            point['reorder_level'] = int(point['stock'] * np.random.uniform(0.2, 0.4))
            point['lead_time'] = np.random.randint(1, 15)
        data_points.append(point)

    df = pd.DataFrame(data_points)

    # Set index for charting if dimensions are present
    chart_index_cols = [col for col in ['time', 'customer', 'item', 'geo'] if col in df.columns]
    if chart_index_cols:
        # Create a more readable index for charts if multiple dimensions are selected
        if len(chart_index_cols) > 1:
            # Combine multiple dimension columns into a single 'chart_label' index
            df['chart_label'] = df[chart_index_cols].apply(lambda row: ' - '.join(row.astype(str)), axis=1)
            df = df.set_index('chart_label')
            # Drop original dimension columns after creating combined index
            df = df.drop(columns=chart_index_cols)
        elif len(chart_index_cols) == 1:
            # If only one dimension, use it directly as the index
            df = df.set_index(chart_index_cols[0])

    # Handle the 'All' case where placeholder columns exist
    elif not chart_index_cols and count == 1:
        placeholder_cols = [col for col in ['Period', 'Customer', 'Store', 'Item', 'Geography'] if col in df.columns]
        if placeholder_cols:
             # Create a descriptive index for the 'All' row
            df['chart_label'] = df[placeholder_cols].apply(lambda row: ' - '.join(row.astype(str)), axis=1)
            df = df.set_index('chart_label')
            df = df.drop(columns=placeholder_cols)

    return df


# Header
st.title("📊 Interactive Analytics Dashboard")
st.markdown("Select dimensions and filters to analyze your sales or inventory data.")

# Data Type Tabs
tab_cols = st.columns(2)
with tab_cols[0]:
    if st.button("📈 Sales Data", key="sales_tab", use_container_width=True, type='primary' if st.session_state.data_type == 'sales' else 'secondary'):
        if st.session_state.data_type != 'sales':
            st.session_state.data_type = 'sales'
            st.session_state.selections = { # Reset selections on data type change
                'time': {'level': '[]', 'display': 'All Time'},
                'customer': {'level': '[]', 'display': 'All Customers'}, # Default for sales
                'item': {'level': '[]', 'display': 'All Items'},
                'geo': {'level': '[]', 'display': 'All Regions'}
            }
            st.session_state.visualization_data = None
            st.rerun()
with tab_cols[1]:
    if st.button("📦 Inventory Data", key="inventory_tab", use_container_width=True, type='primary' if st.session_state.data_type == 'inventory' else 'secondary'):
         if st.session_state.data_type != 'inventory':
            st.session_state.data_type = 'inventory'
            st.session_state.selections = { # Reset selections on data type change
                'time': {'level': '[]', 'display': 'All Time'},
                'customer': {'level': '[]', 'display': 'All Stores'}, # Default for inventory
                'item': {'level': '[]', 'display': 'All Items'},
                'geo': {'level': '[]', 'display': 'All Regions'}
            }
            st.session_state.visualization_data = None
            st.rerun()

# Breadcrumb Navigation
st.markdown("**Current View:**", unsafe_allow_html=True)
breadcrumb_parts = []
active_filters_desc = []
base_breadcrumb_text = f"All {st.session_state.data_type.capitalize()} Data Overview"

for dim, selection in st.session_state.selections.items():
    if json.loads(selection['level']): # Only show if a specific level is selected
        dim_name = dim.capitalize()
        if dim == 'customer':
            dim_name = 'Customer' if st.session_state.data_type == 'sales' else 'Store'
        active_filters_desc.append(f"{dim_name}: {selection['display']}")

if not active_filters_desc:
    breadcrumb_parts.append(f"<div style='display: inline-block;' class='breadcrumb-item font-medium text-blue-600'>{base_breadcrumb_text}</div>")
else:
    breadcrumb_parts.append(f"<div style='display: inline-block; margin-right: 5px;' class='breadcrumb-item font-medium text-blue-600'>{st.session_state.data_type.capitalize()} Data by:</div>")
    for i, desc in enumerate(active_filters_desc):
         is_last = i == len(active_filters_desc) - 1
         style_class = 'font-medium text-gray-700' if not is_last else 'font-semibold text-gray-900' # Highlight last filter
         breadcrumb_parts.append(f"<div style='display: inline-block;' class='breadcrumb-item {style_class}'>{desc}</div>")


st.markdown(" ".join(breadcrumb_parts), unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)


# Filter Controls
st.markdown("### <i class='fas fa-filter'></i> Filter Controls", unsafe_allow_html=True)
filter_cols = st.columns(4)

# --- CORRECTED FILTER CARD SECTIONS START ---

# Time Dimension Filter
with filter_cols[0]:
    color_cfg = filter_colors['time']
    # --- Card Start ---
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3 style='font-weight: 600; color: #1f2937; margin-bottom: 0.75rem; margin-top:-1.5rem'><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.5rem;'></i>Time Dimension</h3>", unsafe_allow_html=True)

    # --- Title (Inside the card) ---
    # st.markdown(f"<h3 style='font-weight: 600; color: #1f2937; margin-bottom: 0.75rem;'><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>Time Dimension</h3>", unsafe_allow_html=True)

    # --- Selectbox ---
    time_selection = st.selectbox(
        "Select Time Granularity", # Hidden label
        options=list(display_names['time'].keys()),
        format_func=lambda x: display_names['time'][x],
        key="time_dimension_selector",
        index=list(display_names['time'].keys()).index(st.session_state.selections['time']['level']),
        label_visibility="collapsed" # Keeps label collapsed
    )
    if time_selection != st.session_state.selections['time']['level']:
        st.session_state.selections['time']['level'] = time_selection
        st.session_state.selections['time']['display'] = display_names['time'][time_selection]
        st.rerun()

    # --- Badge (Inside the card) ---
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block; margin-top: 0.5rem;'>Current: {st.session_state.selections['time']['display']}</span>", unsafe_allow_html=True)

    # --- Card End ---
    st.markdown("</div>", unsafe_allow_html=True)

# Customer/Store Dimension Filter
with filter_cols[1]:
    color_cfg = filter_colors['customer']
    customer_dim_title = "Customer Dimension" if st.session_state.data_type == 'sales' else "Store Dimension"
    # Get dynamic display names for customer based on current data_type
    current_customer_display_names = display_names['customer']

    # --- Card Start ---
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3 style='font-weight: 600; color: #1f2937; margin-bottom: 0.75rem; margin-top:-2rem'><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>{customer_dim_title}</h3>", unsafe_allow_html=True)

    # --- Title (Inside the card) ---
    # st.markdown(f"<h3 style='font-weight: 600; color: #1f2937; margin-bottom: 0.75rem;'><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>{customer_dim_title}</h3>", unsafe_allow_html=True)

    # --- Selectbox ---
    customer_options_keys = list(current_customer_display_names.keys())
    # Find the current index safely
    current_level_cust = st.session_state.selections['customer']['level']
    try:
        cust_index = customer_options_keys.index(current_level_cust)
    except ValueError:
        cust_index = 0 # Default to first option ('All') if current level isn't valid (e.g., after data type switch)
        st.session_state.selections['customer']['level'] = customer_options_keys[0]
        st.session_state.selections['customer']['display'] = current_customer_display_names[customer_options_keys[0]]


    customer_selection = st.selectbox(
        f"Select {customer_dim_title.split(' ')[0]} Granularity", # Hidden label
        options=customer_options_keys,
        format_func=lambda x: current_customer_display_names[x], # Use dynamic display names
        key="customer_dimension_selector",
        index=cust_index,
        label_visibility="collapsed"
    )
    if customer_selection != st.session_state.selections['customer']['level']:
        st.session_state.selections['customer']['level'] = customer_selection
        st.session_state.selections['customer']['display'] = current_customer_display_names[customer_selection]
        st.rerun()

    # --- Badge (Inside the card) ---
    # Ensure badge reflects the current selection, even if defaulted
    current_display_cust = st.session_state.selections['customer']['display']
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block; margin-top: 0.5rem;'>Current: {current_display_cust}</span>", unsafe_allow_html=True)

    # --- Card End ---
    st.markdown("</div>", unsafe_allow_html=True)


# Item Dimension Filter
with filter_cols[2]:
    color_cfg = filter_colors['item']
    # --- Card Start ---
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3 style='font-weight: 600; color: #1f2937; margin-bottom: 0.75rem; margin-top:-1.5rem'><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>Item Dimension</h3>", unsafe_allow_html=True)

    # --- Title (Inside the card) ---
    # st.markdown(f"<h3 style='font-weight: 600; color: #1f2937; margin-bottom: 0.75rem;'><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>Item Dimension</h3>", unsafe_allow_html=True)

    # --- Selectbox ---
    item_selection = st.selectbox(
        "Select Item Granularity", # Hidden label
        options=list(display_names['item'].keys()),
        format_func=lambda x: display_names['item'][x],
        key="item_dimension_selector",
        index=list(display_names['item'].keys()).index(st.session_state.selections['item']['level']),
        label_visibility="collapsed"
    )
    if item_selection != st.session_state.selections['item']['level']:
        st.session_state.selections['item']['level'] = item_selection
        st.session_state.selections['item']['display'] = display_names['item'][item_selection]
        st.rerun()

    # --- Badge (Inside the card) ---
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block; margin-top: 0.5rem;'>Current: {st.session_state.selections['item']['display']}</span>", unsafe_allow_html=True)

    # --- Card End ---
    st.markdown("</div>", unsafe_allow_html=True)

# Geo Dimension Filter
with filter_cols[3]:
    color_cfg = filter_colors['geo']
    # --- Card Start ---
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3 style='font-weight: 600; color: #1f2937; margin-bottom: 0.75rem; margin-top:-2rem'><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>Geography Dimension</h3>", unsafe_allow_html=True)

    # --- Title (Inside the card) ---
    # st.markdown(f"<h3 style='font-weight: 600; color: #1f2937; margin-bottom: 0.75rem;'><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>Geography Dimension</h3>", unsafe_allow_html=True)

    # --- Selectbox ---
    geo_selection = st.selectbox(
        "Select Geographic Granularity", # Hidden label
        options=list(display_names['geo'].keys()),
        format_func=lambda x: display_names['geo'][x],
        key="geo_dimension_selector",
        index=list(display_names['geo'].keys()).index(st.session_state.selections['geo']['level']),
        label_visibility="collapsed"
    )
    if geo_selection != st.session_state.selections['geo']['level']:
        st.session_state.selections['geo']['level'] = geo_selection
        st.session_state.selections['geo']['display'] = display_names['geo'][geo_selection]
        st.rerun()

    # --- Badge (Inside the card) ---
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block; margin-top: 0.5rem;'>Current: {st.session_state.selections['geo']['display']}</span>", unsafe_allow_html=True)

    # --- Card End ---
    st.markdown("</div>", unsafe_allow_html=True)

# --- CORRECTED FILTER CARD SECTIONS END ---


# Apply Button and Visualization Type side-by-side
# st.markdown("<div class='button-container-apply'>", unsafe_allow_html=True)

# # Đặt nút bên trong container. Bỏ use_container_width=True
# # Lưu ý: Logic bên trong 'if' vẫn giữ nguyên
# if st.button("🚀 Apply Filters & Visualize", key="apply_filters", type="primary"): # Bỏ use_container_width
#     with st.spinner("🔄 Applying filters and generating visualization..."):
#         request_data = {
#             'data_type': st.session_state.data_type,
#             'time': st.session_state.selections['time']['level'],
#             'customer': st.session_state.selections['customer']['level'],
#             'item': st.session_state.selections['item']['level'],
#             'geo': st.session_state.selections['geo']['level'],
#         }
#         df = generate_mock_data(request_data)

#         st.session_state.visualization_data = {
#             'data': df,
#             'data_type': request_data['data_type'],
#             'chart_type': st.session_state.chart_type # Use chart_type selected *before* button click
#         }
#         # No st.rerun() here, let the script flow to display data

# st.markdown("</div>", unsafe_allow_html=True)

action_cols = st.columns([3,1]) # Give more space to Apply button
with action_cols[0]:
    st.markdown("<div style='height: 3px;'></div>", unsafe_allow_html=True) # Placeholder for alignment
    if st.button("🚀 Apply Filters & Visualize", key="apply_filters", use_container_width=True, type="primary"):
        with st.spinner("🔄 Applying filters and generating visualization..."):
            request_data = {
                'data_type': st.session_state.data_type,
                'time': st.session_state.selections['time']['level'],
                'customer': st.session_state.selections['customer']['level'],
                'item': st.session_state.selections['item']['level'],
                'geo': st.session_state.selections['geo']['level'],
            }
            df = generate_mock_data(request_data)

            st.session_state.visualization_data = {
                'data': df,
                'data_type': request_data['data_type'],
                'chart_type': st.session_state.chart_type # Use chart_type selected *before* button click
            }
            # No st.rerun() here, let the script flow to display data
with action_cols[1]:
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True) # Placeholder for alignment
    # Update chart_type in session state immediately when selection changes
    selected_chart_type = st.selectbox(
        "View Type",
        options=['table', 'bar', 'line', 'pie'],
        format_func=lambda x: {'table': '📊 Table View', 'bar': '📶 Bar Chart', 'line': '📈 Line Chart', 'pie': '🥧 Pie Chart'}[x],
        key="chart_type_selector",
        # Use the value from session state to ensure consistency
        index=['table', 'bar', 'line', 'pie'].index(st.session_state.chart_type)
    )
    # Update session state if the selection changed
    if selected_chart_type != st.session_state.chart_type:
        st.session_state.chart_type = selected_chart_type
        # If data already exists, update its chart type immediately for redraw
        if isinstance(st.session_state.visualization_data, dict):
             st.session_state.visualization_data['chart_type'] = selected_chart_type
        st.rerun() # Rerun to reflect the change in chart type selection visually


# Visualization Area
st.markdown("### 🖼️ Data Visualization")
# st.markdown("<div class='chart-container'>", unsafe_allow_html=True) # Apply chart-container style

# Check if visualization data exists and is a dict
if not isinstance(st.session_state.visualization_data, dict):
    st.markdown("""
        <div class='center-message'>
            <div>
                <i class='fas fa-search-dollar fa-3x text-gray-400 mb-3'></i>
                <p class='text-gray-600 text-lg'>Select dimension options and click <strong>Apply Filters</strong> to visualize data.</p>
                <p class='text-sm text-gray-500 mt-1'>Results will appear here. You can then choose your preferred view type.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    vis_data = st.session_state.visualization_data
    df_to_display = vis_data['data']
    active_chart_type = vis_data['chart_type'] # Use the chart_type stored when data was generated
    data_type_title = vis_data['data_type'].capitalize()

    if df_to_display is None or df_to_display.empty:
        st.warning("No data generated for the current filter combination.")
    else:
        # Determine primary dimension for charts based on index name or default
        x_axis_data = df_to_display.index
        x_axis_title = df_to_display.index.name if df_to_display.index.name else 'Details' # Use index name or default

        if active_chart_type == 'table':
            # For table view, reset index to show dimension columns properly
            # Check if the index has a name (meaning it was set from dimensions)
            if df_to_display.index.name:
                 st.dataframe(df_to_display.reset_index(), use_container_width=True)
            else: # If index is default RangeIndex (e.g., multiple rows but no specific dimension chosen)
                 st.dataframe(df_to_display, use_container_width=True)

            st.caption(f"Showing {len(df_to_display)} records of {data_type_title} data.")
        else:
            # Determine value field based on data type
            value_field = 'revenue' if vis_data['data_type'] == 'sales' else 'stock'
            value_field_title = 'Revenue' if vis_data['data_type'] == 'sales' else 'Stock Level'

            if value_field not in df_to_display.columns:
                st.error(f"Required value field '{value_field}' not found in the generated data for charting.")
            else:
                # Construct chart title based on filters
                chart_title = f"{data_type_title} Analysis"
                filter_context = []
                for dim_key, sel_info in st.session_state.selections.items():
                    if json.loads(sel_info['level']): # if a specific level is chosen
                        dim_name_for_title = dim_key.capitalize()
                        if dim_key == 'customer': dim_name_for_title = 'Customer' if st.session_state.data_type == 'sales' else 'Store'
                        filter_context.append(f"{dim_name_for_title}: {sel_info['display']}")
                if filter_context:
                    chart_title += f" (Filtered by: {', '.join(filter_context)})"
                elif df_to_display.index.name and 'All - All - All' in df_to_display.index.name: # Check if it's the overall summary row
                     chart_title = f"Overall {data_type_title} Summary"


                fig = None
                try:
                    if active_chart_type == 'bar':
                        fig = px.bar(df_to_display, x=x_axis_data, y=value_field, color=value_field,
                                     title=chart_title, template="plotly_white",
                                     labels={value_field: value_field_title, x_axis_data.name if x_axis_data.name else 'index': x_axis_title})
                    elif active_chart_type == 'line':
                        fig = px.line(df_to_display, x=x_axis_data, y=value_field, title=chart_title,
                                      template="plotly_white", markers=True,
                                      labels={value_field: value_field_title, x_axis_data.name if x_axis_data.name else 'index': x_axis_title})
                    elif active_chart_type == 'pie':
                        df_for_pie = df_to_display
                        names_field_pie = x_axis_data
                        # Pie charts are best for a few categories. Warn if too many.
                        if len(df_to_display) > 15:
                             st.warning(f"Pie chart may be less effective with {len(df_to_display)} categories. Consider using a Bar chart or applying more filters.")
                        # Check if all values are positive for pie chart
                        if (df_to_display[value_field] <= 0).any():
                             st.warning("Pie chart cannot display zero or negative values. These entries will be excluded.")
                             df_for_pie = df_to_display[df_to_display[value_field] > 0]
                             names_field_pie = df_for_pie.index


                        if not df_for_pie.empty:
                           fig = px.pie(df_for_pie, values=value_field, names=names_field_pie, title=chart_title,
                                     template="plotly_white", hole=0.3) # Added a small hole for donut effect
                           fig.update_traces(textposition='inside', textinfo='percent+label')
                        else:
                           st.info("No positive data available to display in the Pie chart.")


                    if fig:
                        fig.update_layout(margin=dict(l=30, r=30, t=60, b=30), title_x=0.5) # Increased top margin for title
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption(f"Visualizing {len(df_to_display)} record(s) of {data_type_title} data as a {active_chart_type} chart.")
                    elif active_chart_type != 'pie': # Don't show this if pie chart had no positive data
                        st.info("Chart generation failed or was skipped.")

                except Exception as e:
                    st.error(f"An error occurred while generating the {active_chart_type} chart: {e}")
                    st.exception(e) # Show full traceback for debugging

st.markdown("</div>", unsafe_allow_html=True)


# Selected Dimensions Summary (appears below visualization)
st.markdown("<hr style='margin-top: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
st.markdown("### <i class='fas fa-th-list'></i> Current Dimension Selections", unsafe_allow_html=True)
summary_cols = st.columns(4)
summary_colors_map = { # Using the main colors from filter_colors for consistency
    'time': filter_colors['time']['main'],
    'customer': filter_colors['customer']['main'],
    'item': filter_colors['item']['main'],
    'geo': filter_colors['geo']['main']
}

for i, (dim, selection) in enumerate(st.session_state.selections.items()):
    with summary_cols[i]:
        dim_display_name = dim.capitalize()
        # Dynamically set display name based on data type for customer/store
        current_display = selection['display']
        if dim == 'customer':
            dim_display_name = 'Customer' if st.session_state.data_type == 'sales' else 'Store'
            # Update display text if it's 'All' to match data type
            if selection['level'] == '[]':
                 current_display = display_names['customer']['[]'] # Get the correct 'All' text

        border_color = summary_colors_map[dim]
        bg_color_summary = f"{border_color}1A" # Adding alpha for background (e.g., #3b82f61A)

        st.markdown(f"""
            <div class='summary-card' style='background-color: {bg_color_summary}; border-left: 4px solid {border_color}; display: flex; flex-direction: column; justify-content: center;'>
                <h4 style='font-size: 0.9rem; font-weight: 600; color: {border_color}; margin-bottom: 0.3rem;'>
                    <i class='{filter_colors[dim]['icon']}' style='margin-right: 0.5rem;'></i>{dim_display_name}
                </h4>
                <p style='font-size: 0.85rem; color: #374151;'>{current_display}</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
st.caption("Developed with Streamlit.")
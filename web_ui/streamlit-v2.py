import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json


import pyarrow
import os
import pandas as pd

import clickhouse_connect

client_sales = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='',  # nếu chưa set mật khẩu
    database='sale_cube'
)
client_inventory = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='',  # nếu chưa set mật khẩu
    database='test_db2'
)

# Thiết lập cấu hình trang
st.set_page_config(page_title="Interactive Analytics Dashboard", layout="wide")

# CSS tùy chỉnh - Đã sửa lỗi và cải thiện giao diện
# (CSS code remains the same - omitted for brevity)
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
            height: 100px; /* Adjusted height for better fit */
            display: flex; /* Use flexbox for vertical layout */
            flex-direction: column; /* Stack children vertically */
            justify-content: space-between; /* Space out title, select, badge */
        }
        .filter-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .chart-container {
            min-height: 450px; /* Use min-height to allow shrinking */
            background-color: #f8fafc;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-top: 1rem;
            display: flex; /* For centering message */
            flex-direction: column; /* For centering message */
            justify-content: center; /* For centering message */
            border: 1px solid #e5e7eb; /* Added subtle border */
        }
        .breadcrumb-item:not(:last-child)::after {
            content: "›";
            margin: 0 8px;
            color: #94a3b8;
        }
        .stButton>button {
            background-color: ##b6d7a8;
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
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .center-message {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            height: 100%; /* Ensure message takes full chart container height */
            min-height: 300px; /* Ensure message area has minimum height */
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
        /* Adjust spacing inside filter card */
        .filter-card h3 {
            margin-bottom: 0.5rem !important; /* Reduced bottom margin */
            margin-top: -0.5rem !important; /* Pull title up slightly */
            font-size: 1.05rem; /* Slightly smaller title */
        }
        .filter-card .stSelectbox {
             margin-top: -0.5rem; /* Pull selectbox up */
             margin-bottom: 0.25rem; /* Reduce space below selectbox */
        }
         .filter-card span {
             /* Badge styling */
             margin-top: auto; /* Push badge to bottom */
         }
    </style>
""", unsafe_allow_html=True)


# --- MOVED UP: Colors for filter cards and badges ---
filter_colors = {
    'time': {'main': '#3b82f6', 'badge_bg': '#dbeafe', 'badge_text': '#1e40af', 'icon': 'fas fa-calendar-alt'},
    'customer': {'main': '#10b981', 'badge_bg': '#d1fae5', 'badge_text': '#065f46', 'icon': 'fas fa-users'}, # Icon remains same
    'item': {'main': '#8b5cf6', 'badge_bg': '#ede9fe', 'badge_text': '#5b21b6', 'icon': 'fas fa-box-open'},
    'geo': {'main': '#f59e0b', 'badge_bg': '#ffedd5', 'badge_text': '#9a3412', 'icon': 'fas fa-globe-americas'}
}



mapping_dim = {
    '[]': 0,
    '["LoaiKH"]': 1,

    '["s.MaCuaHang"]': 1,

    '["t.Nam"]': 1,
    '["t.Quy"]': 2,
    '["t.Thang"]': 3,

    '["i.KichCo"]': 1,
    '["WeightRange"]': 2,
    '["i.MaMH"]': 3,
    '["i.KichCo", "WeightRange"]': 4,

    '["g.Bang"]': 1,
    '["g.Bang", "g.MaThanhPho"]': 2
}


customer_display_names_sales = {
    '[]': 'All Customers',
    '["LoaiKH"]': 'Customer Type' # As requested
}

customer_display_names_inventory = {
    '[]': 'All Stores',
    '["s.MaCuaHang"]': 'Store Code' # As requested
}

# Define common dimension options
time_display_names = {
    '[]': 'All Time',
    '["t.Nam"]': 'Year',
    '["t.Quy"]': 'Quarter',
    '["t.Thang"]': 'Month',
}

item_display_names = {
    '[]': 'All Items',
    '["i.KichCo"]': 'Size',
    '["WeightRange"]': 'Weight Range',
    '["i.MaMH"]': 'Product Code',
    '["i.KichCo", "WeightRange"]': 'Size & Weight'
}

geo_display_names = {
    '[]': 'All Regions',
    '["g.Bang"]': 'State',
    '["g.Bang", "g.MaThanhPho"]': 'State-City'
}

# Helper function to get current customer/store dimension info
# Now this function can safely access filter_colors
def get_current_customer_config():
    if st.session_state.data_type == 'sales':
        return {
            'title': "Customer Dimension",
            'options': customer_display_names_sales,
            'icon': filter_colors['customer']['icon'] # Use consistent icon
        }
    else: # inventory
        return {
            'title': "Store Dimension",
            'options': customer_display_names_inventory,
            'icon': filter_colors['customer']['icon'] # Use consistent icon
        }

# --- SESSION STATE INITIALIZATION ---
if 'data_type' not in st.session_state:
    st.session_state.data_type = 'sales'

# Initialize selections *after* defining helper functions and filter_colors
if 'selections' not in st.session_state:
    # Set initial customer display based on default data_type ('sales')
    # get_current_customer_config() can now be called safely
    initial_customer_all_display = get_current_customer_config()['options']['[]']
    st.session_state.selections = {
        'time': {'level': '[]', 'display': time_display_names['[]']},
        'customer': {'level': '[]', 'display': initial_customer_all_display},
        'item': {'level': '[]', 'display': item_display_names['[]']},
        'geo': {'level': '[]', 'display': geo_display_names['[]']},
        # 'store': {'level': '[]', 'display': customer_display_names_inventory['[]']} # Added for clarity
    }
if 'visualization_data' not in st.session_state:
    st.session_state.visualization_data = None
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = 'table'


# Hàm tạo dữ liệu giả (Updated to handle customer/store labels)
# (generate_mock_data function remains the same - omitted for brevity)
def generate_mock_data(request_data):
    time_levels = request_data['time']
    # Customer levels might represent 'LoaiKH' or 'MaCuaHang'
    customer_levels = request_data['customer']
    item_levels = request_data['item']
    geo_levels = request_data['geo']
    data_type = request_data['data_type']
    df = None
    query = None
    if data_type == 'sales':
        table_name = f"time{time_levels}_customer{customer_levels}_item{item_levels}_geo{geo_levels}"
        query = f"SELECT * FROM {table_name}"
        df = client_sales.query_arrow(query).to_pandas()
    else:
        table_name = f"inventory_fact_time{time_levels}_store{customer_levels}_item{item_levels}_geo{geo_levels}"
        query = f"SELECT * FROM {table_name}"
        df = client_inventory.query_arrow(query).to_pandas()
        
    print(query)
    return df

# Header
st.title("📊 Interactive Analytics Dashboard")
st.markdown("Select dimensions and filters to analyze your sales or inventory data.")

# --- Data Type Tabs (Updated Reset Logic) ---
tab_cols = st.columns(2)
with tab_cols[0]:
    if st.button("📈 Sales Data", key="sales_tab", use_container_width=True, type='primary' if st.session_state.data_type == 'sales' else 'secondary'):
        if st.session_state.data_type != 'sales':
            st.session_state.data_type = 'sales'
            # Reset selections using the *correct* 'All' display text for the new type
            customer_all_display = get_current_customer_config()['options']['[]']
            st.session_state.selections = {
                'time': {'level': '[]', 'display': time_display_names['[]']},
                'customer': {'level': '[]', 'display': customer_all_display},
                'item': {'level': '[]', 'display': item_display_names['[]']},
                'geo': {'level': '[]', 'display': geo_display_names['[]']}
            }
            st.session_state.visualization_data = None
            st.rerun()
with tab_cols[1]:
    if st.button("📦 Inventory Data", key="inventory_tab", use_container_width=True, type='primary' if st.session_state.data_type == 'inventory' else 'secondary'):
         if st.session_state.data_type != 'inventory':
            st.session_state.data_type = 'inventory'
            # Reset selections using the *correct* 'All' display text for the new type
            customer_all_display = get_current_customer_config()['options']['[]']
            st.session_state.selections = {
                'time': {'level': '[]', 'display': time_display_names['[]']},
                'customer': {'level': '[]', 'display': customer_all_display},
                'item': {'level': '[]', 'display': item_display_names['[]']},
                'geo': {'level': '[]', 'display': geo_display_names['[]']}
            }
            st.session_state.visualization_data = None
            st.rerun()

# --- Breadcrumb Navigation (Updated for dynamic Customer/Store) ---
# (Breadcrumb code remains the same - omitted for brevity)
st.markdown("**Current View:**", unsafe_allow_html=True)
breadcrumb_parts = []
active_filters_desc = []
base_breadcrumb_text = f"All {st.session_state.data_type.capitalize()} Data Overview"

for dim, selection in st.session_state.selections.items():
    if json.loads(selection['level']): # Only show if a specific level is selected
        dim_name = dim.capitalize()
        # Use dynamic name for customer/store dimension
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

# --- Time Dimension Filter ---
with filter_cols[0]:
    color_cfg = filter_colors['time']
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.5rem;'></i>Time Dimension</h3>", unsafe_allow_html=True)
    time_options_keys = list(time_display_names.keys())
    time_selection = st.selectbox(
        "Select Time Granularity",
        options=time_options_keys,
        format_func=lambda x: time_display_names[x],
        key="time_dimension_selector",
        index=time_options_keys.index(st.session_state.selections['time']['level']),
        label_visibility="collapsed"
    )
    if time_selection != st.session_state.selections['time']['level']:
        st.session_state.selections['time']['level'] = time_selection
        st.session_state.selections['time']['display'] = time_display_names[time_selection]
        st.rerun()
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block;'>Current: {st.session_state.selections['time']['display']}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Customer/Store Dimension Filter (DYNAMIC) ---
with filter_cols[1]:
    color_cfg = filter_colors['customer']
    # Get current config based on data type
    customer_config = get_current_customer_config()
    customer_dim_title = customer_config['title']
    current_customer_display_names = customer_config['options']
    icon_class = customer_config['icon']

    # --- Card Start ---
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3><i class='{icon_class}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>{customer_dim_title}</h3>", unsafe_allow_html=True)

    # --- Selectbox ---
    customer_options_keys = list(current_customer_display_names.keys())
    current_level_cust = st.session_state.selections['customer']['level']
    # Safely find index, default to 0 ('All') if level mismatch after tab switch
    try:
        cust_index = customer_options_keys.index(current_level_cust)
    except ValueError:
        cust_index = 0 # Default to 'All' index
        st.session_state.selections['customer']['level'] = customer_options_keys[0] # Reset level state
        st.session_state.selections['customer']['display'] = current_customer_display_names[customer_options_keys[0]] # Reset display state

    customer_selection = st.selectbox(
        f"Select {customer_dim_title.split(' ')[0]} Granularity", # Dynamic label for screen readers
        options=customer_options_keys,
        format_func=lambda x: current_customer_display_names[x], # Use dynamic display names
        key="customer_dimension_selector", # Key remains the same
        index=cust_index,
        label_visibility="collapsed"
    )
    if customer_selection != st.session_state.selections['customer']['level']:
        st.session_state.selections['customer']['level'] = customer_selection
        st.session_state.selections['customer']['display'] = current_customer_display_names[customer_selection]
        st.rerun()

    # --- Badge (Inside the card) ---
    current_display_cust = st.session_state.selections['customer']['display'] # Read current state display
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block;'>Current: {current_display_cust}</span>", unsafe_allow_html=True)

    # --- Card End ---
    st.markdown("</div>", unsafe_allow_html=True)


# --- Item Dimension Filter ---
with filter_cols[2]:
    color_cfg = filter_colors['item']
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>Item Dimension</h3>", unsafe_allow_html=True)
    item_options_keys = list(item_display_names.keys())
    item_selection = st.selectbox(
        "Select Item Granularity",
        options=item_options_keys,
        format_func=lambda x: item_display_names[x],
        key="item_dimension_selector",
        index=item_options_keys.index(st.session_state.selections['item']['level']),
        label_visibility="collapsed"
    )
    if item_selection != st.session_state.selections['item']['level']:
        st.session_state.selections['item']['level'] = item_selection
        st.session_state.selections['item']['display'] = item_display_names[item_selection]
        st.rerun()
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block;'>Current: {st.session_state.selections['item']['display']}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Geo Dimension Filter ---
with filter_cols[3]:
    color_cfg = filter_colors['geo']
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>Geography Dimension</h3>", unsafe_allow_html=True)
    geo_options_keys = list(geo_display_names.keys())
    geo_selection = st.selectbox(
        "Select Geographic Granularity",
        options=geo_options_keys,
        format_func=lambda x: geo_display_names[x],
        key="geo_dimension_selector",
        index=geo_options_keys.index(st.session_state.selections['geo']['level']),
        label_visibility="collapsed"
    )
    if geo_selection != st.session_state.selections['geo']['level']:
        st.session_state.selections['geo']['level'] = geo_selection
        st.session_state.selections['geo']['display'] = geo_display_names[geo_selection]
        st.rerun()
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block;'>Current: {st.session_state.selections['geo']['display']}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# Apply Button and Visualization Type side-by-side
action_cols = st.columns([3,1])
with action_cols[0]: 
    st.markdown("<p></p>", unsafe_allow_html=True) # Spacer
    if st.button("🚀 Apply Filters & Visualize", key="apply_filters", use_container_width=True, type="primary"):
        with st.spinner("🔄 Applying filters and generating visualization..."):
            request_data = {
                'data_type': st.session_state.data_type,
                'time': mapping_dim[st.session_state.selections['time']['level']],
                'customer': mapping_dim[st.session_state.selections['customer']['level']], # Pass the level
                'item': mapping_dim[st.session_state.selections['item']['level']],
                'geo': mapping_dim[st.session_state.selections['geo']['level']],
            }
            df = generate_mock_data(request_data)
            print(request_data)
            st.session_state.visualization_data = {
                'data': df,
                'data_type': request_data['data_type'],
                'chart_type': st.session_state.chart_type
            }
with action_cols[1]:
    selected_chart_type = st.selectbox(
        "View Type",
        options=['table', 'bar', 'line', 'pie'],
        format_func=lambda x: {'table': '📊 Table View', 'bar': '📶 Bar Chart', 'line': '📈 Line Chart', 'pie': '🥧 Pie Chart'}[x],
        key="chart_type_selector",
        index=['table', 'bar', 'line', 'pie'].index(st.session_state.chart_type)
    )
    if selected_chart_type != st.session_state.chart_type:
        st.session_state.chart_type = selected_chart_type
        if isinstance(st.session_state.visualization_data, dict):
             st.session_state.visualization_data['chart_type'] = selected_chart_type
        st.rerun()


# Visualization Area
# (Visualization code remains the same - omitted for brevity)
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
    active_chart_type = vis_data['chart_type']
    data_type_title = vis_data['data_type'].capitalize()

    if df_to_display is None or df_to_display.empty:
        st.warning("No data generated for the current filter combination.")
    else:
        if active_chart_type == 'table':
            # Display dataframe using st.dataframe
            st.markdown('<div class="data-table">', unsafe_allow_html=True) # Wrap table for styling
            # Reset index for table view *only if* it's not the default RangeIndex
            # And check if index name exists (meaning it was likely set from dimensions)
            df_to_display_corrected = df_to_display.copy() # Nên tạo bản sao

            # Duyệt qua từng cột để tìm cột dạng bytes
            for col in df_to_display_corrected.columns:
                # Kiểm tra xem cột có chứa dữ liệu bytes không (kiểm tra phần tử đầu tiên là đủ trong nhiều trường hợp)
                if df_to_display_corrected[col].apply(type).eq(bytes).any():
                    try:
                        # Nếu là cột bytes, dùng .decode() để chuyển sang string
                        # Giả định mã hóa là 'utf-8', thay đổi nếu cần
                        df_to_display_corrected[col] = df_to_display_corrected[col].apply(
                            lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
                        )
                    except Exception as e:
                        st.warning(f"Could not decode column '{col}' automatically. Error: {e}")
                        # Bạn có thể quyết định hiển thị cột gốc hoặc xử lý khác ở đây

            # --- KẾT THÚC PHẦN SỬA ---

            # Bây giờ hiển thị DataFrame đã được sửa
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            st.dataframe(
                df_to_display_corrected.reset_index(), # DÙNG DATAFRAME ĐÃ SỬA
                use_container_width=True,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption(f"Showing {len(df_to_display)} records of {data_type_title} data.")
        else:
            # --- CHARTING LOGIC ---
            value_field = 'revenue' if vis_data['data_type'] == 'sales' else 'stock'
            value_field_title = 'Revenue' if vis_data['data_type'] == 'sales' else 'Stock Level'

            if value_field not in df_to_display.columns:
                st.error(f"Required value field '{value_field}' not found in the generated data for charting.")
            else:
                # Use the DataFrame's index for the x-axis/names
                x_axis_data = df_to_display.index
                # Determine x-axis title dynamically (use index name if available)
                x_axis_title = x_axis_data.name if x_axis_data.name else 'Details'

                # Construct chart title based on filters
                chart_title = f"{data_type_title} Analysis"
                filter_context = []
                for dim_key, sel_info in st.session_state.selections.items():
                    if json.loads(sel_info['level']):
                        dim_name_for_title = dim_key.capitalize()
                        if dim_key == 'customer': dim_name_for_title = 'Customer' if st.session_state.data_type == 'sales' else 'Store'
                        filter_context.append(f"{dim_name_for_title}: {sel_info['display']}")
                if filter_context:
                    chart_title += f" by {x_axis_title}" # Add dimension name if filtered
                # Special title for the absolute 'All' case
                elif x_axis_data.name == 'chart_label' and 'Overall - All' in x_axis_data[0]:
                     chart_title = f"Overall {data_type_title} Summary"


                fig = None
                try:
                    if active_chart_type == 'bar':
                        fig = px.bar(df_to_display, x=x_axis_data, y=value_field, color=value_field,
                                     title=chart_title, template="plotly_white",
                                     labels={value_field: value_field_title, 'index': x_axis_title}) # Use 'index' for label key
                    elif active_chart_type == 'line':
                        fig = px.line(df_to_display, x=x_axis_data, y=value_field, title=chart_title,
                                      template="plotly_white", markers=True,
                                      labels={value_field: value_field_title, 'index': x_axis_title}) # Use 'index' for label key
                    elif active_chart_type == 'pie':
                        # Handle potential negative/zero values for pie chart
                        df_for_pie = df_to_display[df_to_display[value_field] > 0]
                        names_field_pie = df_for_pie.index

                        if len(df_to_display) > 15:
                             st.warning(f"Pie chart may be less effective with {len(df_to_display)} categories. Consider Bar chart or more filters.")
                        if len(df_for_pie) < len(df_to_display):
                             st.warning("Zero or negative values excluded from Pie chart.")

                        if not df_for_pie.empty:
                           fig = px.pie(df_for_pie, values=value_field, names=names_field_pie, title=chart_title,
                                     template="plotly_white", hole=0.3)
                           fig.update_traces(textposition='inside', textinfo='percent+label')
                        else:
                           st.info("No positive data available to display in the Pie chart.")

                    if fig:
                        fig.update_layout(margin=dict(l=30, r=30, t=60, b=30), title_x=0.5, xaxis_title=x_axis_title) # Set explicit x-axis title
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption(f"Visualizing {len(df_to_display)} record(s) of {data_type_title} data as a {active_chart_type} chart, grouped by {x_axis_title}.")
                    elif active_chart_type != 'pie': # Avoid double message if pie had no data
                        st.info("Chart generation failed or was skipped.")

                except Exception as e:
                    st.error(f"An error occurred while generating the {active_chart_type} chart: {e}")
                    st.exception(e) # Show full traceback for debugging

st.markdown("</div>", unsafe_allow_html=True) # End chart-container


# --- Selected Dimensions Summary (Updated for dynamic Customer/Store) ---
# (Summary code remains the same - omitted for brevity)
st.markdown("<hr style='margin-top: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
st.markdown("### <i class='fas fa-th-list'></i> Current Dimension Selections", unsafe_allow_html=True)
summary_cols = st.columns(4)
summary_colors_map = {
    'time': filter_colors['time']['main'],
    'customer': filter_colors['customer']['main'],
    'item': filter_colors['item']['main'],
    'geo': filter_colors['geo']['main']
}

for i, (dim, selection) in enumerate(st.session_state.selections.items()):
    with summary_cols[i]:
        # Get current display text directly from state
        current_display = selection['display']
        # Set display name and icon dynamically for customer/store
        if dim == 'customer':
            customer_config = get_current_customer_config()
            dim_display_name = customer_config['title'].replace(" Dimension","") # Get "Customer" or "Store"
            icon_class = customer_config['icon']
            # Ensure 'All' text is correct even if state was reset
            if selection['level'] == '[]':
                 current_display = customer_config['options']['[]']
        else:
            # For other dimensions, get name and icon from static config
            dim_display_name = dim.capitalize()
            icon_class = filter_colors[dim]['icon']

        border_color = summary_colors_map[dim]
        bg_color_summary = f"{border_color}1A" # Adding alpha for background

        st.markdown(f"""
            <div class='summary-card' style='background-color: {bg_color_summary}; border-left: 4px solid {border_color};'>
                <h4 style='font-size: 0.9rem; font-weight: 600; color: {border_color}; margin-bottom: 0.3rem;'>
                    <i class='{icon_class}' style='margin-right: 0.5rem;'></i>{dim_display_name}
                </h4>
                <p style='font-size: 0.85rem; color: #374151; margin-bottom: 0;'>{current_display}</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
st.caption("Developed with Streamlit.")
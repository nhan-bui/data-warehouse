import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import pyarrow
import os
# import pandas as pd # Already imported

import clickhouse_connect

client_sales = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='',
    database='sale_cube'
)
client_inventory = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='',
    database='test_db2'
)

st.set_page_config(page_title="Interactive Analytics Dashboard", layout="wide")

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
            height: 100px; 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between; 
        }
        .filter-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .chart-container {
            min-height: 450px; 
            background-color: #f8fafc;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-top: 1rem;
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
            border: 1px solid #e5e7eb; 
        }
        .breadcrumb-item:not(:last-child)::after {
            content: "›";
            margin: 0 8px;
            color: #94a3b8;
        }
        .stButton>button, .stDownloadButton>button, .stFormSubmitButton>button { /* Added .stFormSubmitButton */
            background-color: #76a7d4;
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
            width: 100%;
            margin: 0.5rem 0;
            border: none; /* Ensure no default border */
        }
        .stButton>button:hover, .stDownloadButton>button:hover, .stFormSubmitButton>button:hover { /* Added .stFormSubmitButton */
            background-color: #3d83c3;
        }
        /* Specific styling for detailed filter apply button if needed */
        .detailed-filter-container .stFormSubmitButton>button {
            background-color: #059669; /* A green color for apply */
            margin-top: 1rem; /* Add some space above it */
        }
        .detailed-filter-container .stFormSubmitButton>button:hover {
            background-color: #047857;
        }

        .summary-card {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            height: 100px; 
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
            height: 100%; 
            min-height: 300px; 
        }
        .data-table {
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
            overflow: hidden;
        }
        .stSelectbox label {}
        .filter-card h3 {
            margin-bottom: 0.5rem !important; 
            margin-top: -0.5rem !important; 
            font-size: 1.05rem; 
        }
        .filter-card .stSelectbox {
             margin-top: -0.5rem; 
             margin-bottom: 0.25rem; 
        }
         .filter-card span {
             margin-top: auto; 
         }
         .detailed-filter-container {
            background-color: #f9fafb; 
            padding: 1.5rem; /* Increased padding */
            border-radius: 0.5rem;
            margin-top: 1.5rem;
            border: 1px solid #e5e7eb;
         }
         .detailed-filter-container .stSelectbox, 
         .detailed-filter-container .stMultiSelect {
            background-color: white; 
         }
    </style>
""", unsafe_allow_html=True)

filter_colors = {
    'time': {'main': '#3b82f6', 'badge_bg': '#dbeafe', 'badge_text': '#1e40af', 'icon': 'fas fa-calendar-alt'},
    'customer': {'main': '#10b981', 'badge_bg': '#d1fae5', 'badge_text': '#065f46', 'icon': 'fas fa-users'},
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

DIMENSION_LEVEL_TO_COLUMNS_MAP = {
    '["t.Nam"]': ['Nam'],
    '["t.Quy"]': ['Nam', 'Quy'],
    '["t.Thang"]': ['Nam', 'Thang'],
    '["LoaiKH"]': ['LoaiKH'],
    '["s.MaCuaHang"]': ['MaCuaHang'],
    '["i.KichCo"]': ['KichCo'],
    '["WeightRange"]': ['WeightRange'],
    '["i.MaMH"]': ['MaMH'],
    '["i.KichCo", "WeightRange"]': ['KichCo', 'WeightRange'],
    '["g.Bang"]': ['Bang'],
    '["g.Bang", "g.MaThanhPho"]': ['Bang', 'MaThanhPho']
}

customer_display_names_sales = {
    '[]': 'All Customers',
    '["LoaiKH"]': 'Customer Type'
}
customer_display_names_inventory = {
    '[]': 'All Stores',
    '["s.MaCuaHang"]': 'Store Code'
}
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

def get_current_customer_config():
    if st.session_state.data_type == 'sales':
        return {'title': "Customer Dimension", 'options': customer_display_names_sales, 'icon': filter_colors['customer']['icon']}
    else:
        return {'title': "Store Dimension", 'options': customer_display_names_inventory, 'icon': filter_colors['customer']['icon']}

if 'data_type' not in st.session_state:
    st.session_state.data_type = 'sales'
if 'selections' not in st.session_state:
    initial_customer_all_display = get_current_customer_config()['options']['[]']
    st.session_state.selections = {
        'time': {'level': '[]', 'display': time_display_names['[]']},
        'customer': {'level': '[]', 'display': initial_customer_all_display},
        'item': {'level': '[]', 'display': item_display_names['[]']},
        'geo': {'level': '[]', 'display': geo_display_names['[]']},
    }
if 'visualization_data' not in st.session_state:
    st.session_state.visualization_data = None
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = 'table'
if 'detailed_filters_applied_values' not in st.session_state:
    st.session_state.detailed_filters_applied_values = {}

def generate_mock_data(request_data):
    time_levels = request_data['time']
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
    print(f"Executed Query: {query}")
    return df

st.title("📊 Interactive Analytics Dashboard")
st.markdown("Select dimensions and filters to analyze your sales or inventory data.")

def reset_all_filters_and_data():
    # Determine customer_all_display *before* changing st.session_state.data_type
    # or based on the target data_type if it's passed as an argument.
    # For now, assuming get_current_customer_config() correctly reflects the intended new type.
    customer_all_display = get_current_customer_config()['options']['[]']
    st.session_state.selections = {
        'time': {'level': '[]', 'display': time_display_names['[]']},
        'customer': {'level': '[]', 'display': customer_all_display}, # This needs to be correct for the *new* type
        'item': {'level': '[]', 'display': item_display_names['[]']},
        'geo': {'level': '[]', 'display': geo_display_names['[]']}
    }
    st.session_state.visualization_data = None
    st.session_state.detailed_filters_applied_values = {}

tab_cols = st.columns(2)
with tab_cols[0]:
    if st.button("📈 Sales Data", key="sales_tab", use_container_width=True, type='primary' if st.session_state.data_type == 'sales' else 'secondary'):
        if st.session_state.data_type != 'sales':
            st.session_state.data_type = 'sales' # Change type first
            reset_all_filters_and_data()        # Then reset based on new type
            st.rerun()
with tab_cols[1]:
    if st.button("📦 Inventory Data", key="inventory_tab", use_container_width=True, type='primary' if st.session_state.data_type == 'inventory' else 'secondary'):
         if st.session_state.data_type != 'inventory':
            st.session_state.data_type = 'inventory' # Change type first
            reset_all_filters_and_data()           # Then reset based on new type
            st.rerun()

# --- Breadcrumb Navigation ---
st.markdown("**Current View:**", unsafe_allow_html=True)
breadcrumb_parts = []
active_filters_desc = []
base_breadcrumb_text = f"All {st.session_state.data_type.capitalize()} Data Overview"
for dim, selection in st.session_state.selections.items():
    if json.loads(selection['level']):
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
         style_class = 'font-medium text-gray-700' if not is_last else 'font-semibold text-gray-900'
         breadcrumb_parts.append(f"<div style='display: inline-block;' class='breadcrumb-item {style_class}'>{desc}</div>")
st.markdown(" ".join(breadcrumb_parts), unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

# --- Filter Controls ---
st.markdown("### <i class='fas fa-filter'></i> Filter Controls", unsafe_allow_html=True)
filter_cols = st.columns(4)
# Time Dimension Filter
with filter_cols[0]:
    color_cfg = filter_colors['time']
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.5rem;'></i>Time Dimension</h3>", unsafe_allow_html=True)
    time_options_keys = list(time_display_names.keys())
    time_selection = st.selectbox("Select Time Granularity", options=time_options_keys, format_func=lambda x: time_display_names[x], key="time_dimension_selector", index=time_options_keys.index(st.session_state.selections['time']['level']), label_visibility="collapsed")
    if time_selection != st.session_state.selections['time']['level']:
        st.session_state.selections['time']['level'] = time_selection
        st.session_state.selections['time']['display'] = time_display_names[time_selection]
        st.rerun()
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block;'>Current: {st.session_state.selections['time']['display']}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Customer/Store Dimension Filter
with filter_cols[1]:
    color_cfg = filter_colors['customer']
    customer_config = get_current_customer_config()
    customer_dim_title = customer_config['title']
    current_customer_display_names = customer_config['options']
    icon_class = customer_config['icon']
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3><i class='{icon_class}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>{customer_dim_title}</h3>", unsafe_allow_html=True)
    customer_options_keys = list(current_customer_display_names.keys())
    current_level_cust = st.session_state.selections['customer']['level']
    try:
        cust_index = customer_options_keys.index(current_level_cust)
    except ValueError:
        cust_index = 0
        st.session_state.selections['customer']['level'] = customer_options_keys[0]
        st.session_state.selections['customer']['display'] = current_customer_display_names[customer_options_keys[0]]
    customer_selection = st.selectbox(f"Select {customer_dim_title.split(' ')[0]} Granularity", options=customer_options_keys, format_func=lambda x: current_customer_display_names[x], key="customer_dimension_selector", index=cust_index, label_visibility="collapsed")
    if customer_selection != st.session_state.selections['customer']['level']:
        st.session_state.selections['customer']['level'] = customer_selection
        st.session_state.selections['customer']['display'] = current_customer_display_names[customer_selection]
        st.rerun()
    current_display_cust = st.session_state.selections['customer']['display']
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block;'>Current: {current_display_cust}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Item Dimension Filter
with filter_cols[2]:
    color_cfg = filter_colors['item']
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>Item Dimension</h3>", unsafe_allow_html=True)
    item_options_keys = list(item_display_names.keys())
    item_selection = st.selectbox("Select Item Granularity", options=item_options_keys, format_func=lambda x: item_display_names[x], key="item_dimension_selector", index=item_options_keys.index(st.session_state.selections['item']['level']), label_visibility="collapsed")
    if item_selection != st.session_state.selections['item']['level']:
        st.session_state.selections['item']['level'] = item_selection
        st.session_state.selections['item']['display'] = item_display_names[item_selection]
        st.rerun()
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block;'>Current: {st.session_state.selections['item']['display']}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Geo Dimension Filter
with filter_cols[3]:
    color_cfg = filter_colors['geo']
    st.markdown(f"<div class='filter-card' style='border-left-color: {color_cfg['main']};'><h3><i class='{color_cfg['icon']}' style='color: {color_cfg['main']}; margin-right: 0.75rem;'></i>Geography Dimension</h3>", unsafe_allow_html=True)
    geo_options_keys = list(geo_display_names.keys())
    geo_selection = st.selectbox("Select Geographic Granularity", options=geo_options_keys, format_func=lambda x: geo_display_names[x], key="geo_dimension_selector", index=geo_options_keys.index(st.session_state.selections['geo']['level']), label_visibility="collapsed")
    if geo_selection != st.session_state.selections['geo']['level']:
        st.session_state.selections['geo']['level'] = geo_selection
        st.session_state.selections['geo']['display'] = geo_display_names[geo_selection]
        st.rerun()
    st.markdown(f"<span style='font-size: 0.85rem; background-color: {color_cfg['badge_bg']}; color: {color_cfg['badge_text']}; padding: 0.25rem 0.75rem; border-radius: 9999px; display: inline-block;'>Current: {st.session_state.selections['geo']['display']}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Apply Button and Visualization Type ---
action_cols = st.columns([3,1])
with action_cols[0]:
    st.markdown("<p></p>", unsafe_allow_html=True)
    if st.button("🚀 Apply Filters & Visualize", key="apply_filters", use_container_width=True, type="primary"):
        with st.spinner("🔄 Applying filters and generating visualization..."):
            st.session_state.detailed_filters_applied_values = {} # Reset detailed filters on primary apply
            request_data = {
                'data_type': st.session_state.data_type,
                'time': mapping_dim[st.session_state.selections['time']['level']],
                'customer': mapping_dim[st.session_state.selections['customer']['level']],
                'item': mapping_dim[st.session_state.selections['item']['level']],
                'geo': mapping_dim[st.session_state.selections['geo']['level']],
            }
            df = generate_mock_data(request_data)
            st.session_state.visualization_data = {
                'data': df,
                'data_type': request_data['data_type'],
                'chart_type': st.session_state.chart_type 
            }
            # No explicit rerun here, script flow continues to visualization.
            # Detailed filters are reset, so their previous state won't affect this new view until changed again.
with action_cols[1]:
    selected_chart_type = st.selectbox("View Type", options=['table', 'bar', 'line', 'pie'], format_func=lambda x: {'table': '📊 Table View', 'bar': '📶 Bar Chart', 'line': '📈 Line Chart', 'pie': '🥧 Pie Chart'}[x], key="chart_type_selector", index=['table', 'bar', 'line', 'pie'].index(st.session_state.chart_type))
    if selected_chart_type != st.session_state.chart_type:
        st.session_state.chart_type = selected_chart_type
        if isinstance(st.session_state.visualization_data, dict):
             st.session_state.visualization_data['chart_type'] = selected_chart_type
        st.rerun()

# --- Data Visualization Area ---
st.markdown("### 🖼️ Data Visualization")
# st.markdown("<div class='chart-container'>", unsafe_allow_html=True)

def apply_stored_detailed_filters(df_input, detailed_filter_selections):
    if not detailed_filter_selections or df_input is None or df_input.empty:
        return df_input
    df_filtered = df_input.copy()
    for col_name, Svalue in detailed_filter_selections.items():
        if col_name in df_filtered.columns:
            is_selectbox_all = isinstance(Svalue, str) and Svalue == "All"
            is_multiselect_all = isinstance(Svalue, list) and not Svalue
            if is_selectbox_all or is_multiselect_all: continue
            column_as_str = df_filtered[col_name].astype(str)
            if isinstance(Svalue, str):
                 df_filtered = df_filtered[column_as_str == Svalue]
            elif isinstance(Svalue, list) and Svalue:
                 svalue_str_list = [str(v) for v in Svalue]
                 df_filtered = df_filtered[column_as_str.isin(svalue_str_list)]
            if df_filtered.empty: break
    return df_filtered

df_for_visualization = None
df_decoded_for_view = None # Will hold data after primary filters + byte decoding, used for populating detailed filter options

if not isinstance(st.session_state.visualization_data, dict) or st.session_state.visualization_data['data'] is None:
    st.markdown("""
        <div class='center-message'>
            <div><i class='fas fa-search-dollar fa-3x text-gray-400 mb-3'></i>
                 <p class='text-gray-600 text-lg'>Select dimension options and click <strong>Apply Filters</strong> to visualize data.</p>
                 <p class='text-sm text-gray-500 mt-1'>Results will appear here. You can then choose your preferred view type.</p>
            </div></div>""", unsafe_allow_html=True)
else:
    vis_data = st.session_state.visualization_data
    df_original_for_view = vis_data['data']
    active_chart_type = vis_data['chart_type']
    data_type_title = vis_data['data_type'].capitalize()

    df_decoded_for_view = df_original_for_view.copy() if df_original_for_view is not None else pd.DataFrame()
    if not df_decoded_for_view.empty:
        for col in df_decoded_for_view.columns:
            if df_decoded_for_view[col].apply(type).eq(bytes).any():
                try:
                    df_decoded_for_view[col] = df_decoded_for_view[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
                except Exception as e:
                    st.warning(f"Could not decode column '{col}' automatically. Error: {e}")
    
    df_for_visualization = apply_stored_detailed_filters(df_decoded_for_view, st.session_state.detailed_filters_applied_values)

    if df_for_visualization is None or df_for_visualization.empty:
        st.warning("No data to display after applying all filters. Try adjusting your filter criteria.")
    else:
        # Visualization logic (table, bar, line, pie) using df_for_visualization
        # This part remains largely the same as your existing code, just ensure it uses df_for_visualization
        if active_chart_type == 'table':
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            st.dataframe(df_for_visualization.reset_index(drop=True), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption(f"Showing {len(df_for_visualization)} records of {data_type_title} data (after detailed filtering).")
        else:
            value_field = 'revenue' if vis_data['data_type'] == 'sales' else 'stock'
            value_field_title = 'Revenue' if vis_data['data_type'] == 'sales' else 'Stock Level'
            if value_field not in df_for_visualization.columns:
                st.error(f"Required value field '{value_field}' not found in the data for charting.")
            else:
                x_axis_data = df_for_visualization.index 
                x_axis_title = x_axis_data.name if x_axis_data.name else 'Details'
                chart_title = f"{data_type_title} Analysis"
                primary_filter_context = []
                for dim_key, sel_info in st.session_state.selections.items():
                    if json.loads(sel_info['level']):
                        dim_name_for_title = dim_key.capitalize()
                        if dim_key == 'customer': dim_name_for_title = 'Customer' if st.session_state.data_type == 'sales' else 'Store'
                        primary_filter_context.append(f"{dim_name_for_title}: {sel_info['display']}")
                if primary_filter_context: chart_title += f" by {', '.join(primary_filter_context)}"
                if x_axis_data.name and x_axis_data.name != 'index' and x_axis_data.name not in chart_title: chart_title += f" (Grouped by {x_axis_title})"
                fig = None
                try:
                    if active_chart_type == 'bar':
                        fig = px.bar(df_for_visualization, x=x_axis_data, y=value_field, color=value_field, title=chart_title, template="plotly_white", labels={value_field: value_field_title, 'index': x_axis_title})
                    elif active_chart_type == 'line':
                        fig = px.line(df_for_visualization, x=x_axis_data, y=value_field, title=chart_title, template="plotly_white", markers=True, labels={value_field: value_field_title, 'index': x_axis_title})
                    elif active_chart_type == 'pie':
                        df_for_pie = df_for_visualization[df_for_visualization[value_field] > 0]
                        names_field_pie = df_for_pie.index
                        if len(df_for_visualization) > 15: st.warning(f"Pie chart may be less effective with {len(df_for_visualization)} categories.")
                        if len(df_for_pie) < len(df_for_visualization): st.warning("Zero or negative values excluded from Pie chart.")
                        if not df_for_pie.empty:
                           fig = px.pie(df_for_pie, values=value_field, names=names_field_pie, title=chart_title, template="plotly_white", hole=0.3)
                           fig.update_traces(textposition='inside', textinfo='percent+label')
                        else: st.info("No positive data available for Pie chart.")
                    if fig:
                        fig.update_layout(margin=dict(l=30, r=30, t=60, b=30), title_x=0.5, xaxis_title=x_axis_title)
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption(f"Visualizing {len(df_for_visualization)} record(s) of {data_type_title} data as a {active_chart_type} chart, grouped by {x_axis_title} (after detailed filtering).")
                    elif active_chart_type != 'pie': st.info("Chart generation failed or was skipped.")
                except Exception as e:
                    st.error(f"An error occurred while generating the {active_chart_type} chart: {e}")
                    st.exception(e)
st.markdown("</div>", unsafe_allow_html=True) # End chart-container

# --- MODIFIED: DETAILED FILTERS SECTION WITH APPLY BUTTON ---
if df_decoded_for_view is not None and not df_decoded_for_view.empty: # Use df_decoded_for_view to populate options
    detailed_filter_column_definitions = []
    for dim_key in ['time', 'customer', 'item', 'geo']:
        level_str = st.session_state.selections[dim_key]['level']
        if level_str != '[]':
            cols_for_this_dim = DIMENSION_LEVEL_TO_COLUMNS_MAP.get(level_str, [])
            for col_name in cols_for_this_dim:
                if col_name in df_decoded_for_view.columns:
                    widget_type = 'selectbox' if dim_key == 'time' and col_name in ['Nam', 'Quy', 'Thang'] else 'multiselect'
                    detailed_filter_column_definitions.append({
                        'col_name': col_name,
                        'label': f"Refine by {col_name.replace('_', ' ').title()}", # Prettier label
                        'widget_type': widget_type
                    })
    
    if detailed_filter_column_definitions:
        # st.markdown("<div class='detailed-filter-container'>", unsafe_allow_html=True)
        st.markdown("#### <i class='fas fa-filter'></i> Refine Displayed Results", unsafe_allow_html=True)
        
        with st.form(key="detailed_filters_form"):
            num_detailed_filters = len(detailed_filter_column_definitions)
            filter_cols_layout = st.columns(min(num_detailed_filters, 3))
            
            for i, filter_def in enumerate(detailed_filter_column_definitions):
                col_name = filter_def['col_name']
                label = filter_def['label']
                widget_type = filter_def['widget_type']
                current_col_for_layout = filter_cols_layout[i % min(num_detailed_filters, 3)]

                with current_col_for_layout:
                    # Populate options from df_decoded_for_view (data *before* detailed filters)
                    unique_values = sorted(df_decoded_for_view[col_name].astype(str).unique())
                    
                    if widget_type == 'selectbox':
                        options = ["All"] + unique_values
                        # Get current *applied* value for default, or "All" if not set
                        current_applied_value = st.session_state.detailed_filters_applied_values.get(col_name, "All")
                        try:
                            default_index = options.index(current_applied_value)
                        except ValueError:
                            default_index = 0 # Default to "All" if value not in options (e.g., after primary filter change)
                        
                        st.selectbox(
                            label,
                            options=options,
                            index=default_index,
                            key=f"detailed_filter_formwidget_sb_{col_name}" # Unique key for form widget
                        )
                    
                    elif widget_type == 'multiselect':
                        current_applied_value = st.session_state.detailed_filters_applied_values.get(col_name, [])
                        # Ensure default values are valid options
                        valid_default_selection = [s for s in current_applied_value if s in unique_values]
                        
                        st.multiselect(
                            label,
                            options=unique_values,
                            default=valid_default_selection,
                            key=f"detailed_filter_formwidget_ms_{col_name}" # Unique key for form widget
                        )
            
            # Place submit button within the form, potentially spanning columns or below them
            submitted_detailed_filters = st.form_submit_button(
                label="🔍 Apply Refinements", 
                use_container_width=True
            )

        if submitted_detailed_filters:
            # This block runs after the form is submitted and the page reruns once.
            # Values from form widgets are in st.session_state with their keys.
            
            filters_changed_by_form = False
            newly_set_detailed_filters = {}

            for filter_def in detailed_filter_column_definitions:
                col_name = filter_def['col_name']
                widget_type = filter_def['widget_type']
                form_widget_key = f"detailed_filter_formwidget_{'sb' if widget_type == 'selectbox' else 'ms'}_{col_name}"
                
                value_from_form_widget = st.session_state[form_widget_key]
                newly_set_detailed_filters[col_name] = value_from_form_widget

                # Check if this value is different from what was previously applied
                previously_applied_value = st.session_state.detailed_filters_applied_values.get(col_name)
                
                if widget_type == 'selectbox':
                    if previously_applied_value is None: previously_applied_value = "All" # Normalize for comparison
                    if value_from_form_widget != previously_applied_value:
                        filters_changed_by_form = True
                elif widget_type == 'multiselect':
                    if previously_applied_value is None: previously_applied_value = [] # Normalize
                    if sorted(value_from_form_widget) != sorted(previously_applied_value):
                        filters_changed_by_form = True
            
            if filters_changed_by_form:
                st.session_state.detailed_filters_applied_values = newly_set_detailed_filters
                st.rerun() # Rerun again to apply the newly committed detailed filters
            # If no actual change, the first rerun (from form submission) is enough,
            # and apply_stored_detailed_filters will use the (unchanged) detailed_filters_applied_values.

        st.markdown("</div>", unsafe_allow_html=True)

# --- Selected Dimensions Summary ---
st.markdown("<hr style='margin-top: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
st.markdown("### <i class='fas fa-th-list'></i> Current Dimension Selections", unsafe_allow_html=True)
summary_cols = st.columns(4)
summary_colors_map = {'time': filter_colors['time']['main'], 'customer': filter_colors['customer']['main'], 'item': filter_colors['item']['main'], 'geo': filter_colors['geo']['main']}
for i, (dim, selection) in enumerate(st.session_state.selections.items()):
    with summary_cols[i]:
        current_display = selection['display']
        if dim == 'customer':
            customer_config = get_current_customer_config()
            dim_display_name = customer_config['title'].replace(" Dimension","")
            icon_class = customer_config['icon']
            if selection['level'] == '[]': current_display = customer_config['options']['[]']
        else:
            dim_display_name = dim.capitalize()
            icon_class = filter_colors[dim]['icon']
        border_color = summary_colors_map[dim]
        bg_color_summary = f"{border_color}1A"
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
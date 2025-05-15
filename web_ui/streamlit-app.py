import streamlit as st
import pandas as pd # Để tạo ví dụ dữ liệu cho bảng

# --- Cấu hình trang ---
st.set_page_config(layout="wide", page_title="Interactive Analytics Dashboard")

# --- Khởi tạo Session State ---
# Dùng để lưu trữ các lựa chọn filter đã áp dụng
if 'applied_filters' not in st.session_state:
    st.session_state.applied_filters = {
        "time": "All Time",
        "customer": "All Customers",
        "item": "All Items",
        "geography": "All Regions"
    }
if 'show_data' not in st.session_state:
    st.session_state.show_data = False # Ban đầu không hiển thị dữ liệu

# --- Dữ liệu mẫu cho các dropdowns ---
time_options = ["All Time", "Last 7 Days", "Last 30 Days", "Custom Range"]
customer_options = ["All Customers", "New Customers", "Returning Customers", "Specific Segment"]
item_options = ["All Items", "Category A", "Category B", "Specific Product"]
geography_options = ["All Regions", "North America", "Europe", "Asia", "Specific Country"]

# --- Header ---
st.markdown("""
<style>
    /* Tùy chỉnh nhỏ cho tiêu đề nếu cần */
    .stApp > header {
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px; /* Khoảng cách giữa các tab */
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: #F0F2F6; /* Màu nền tab không active */
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0E1117; /* Màu nền tab active */
        color: white;
    }
    .current-selection-box {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px; /* Thêm khoảng cách dưới */
    }
    .current-selection-box h5 { /* Tiêu đề trong box */
        margin-top: 0;
        margin-bottom: 5px;
    }
    .current-selection-box p { /* Nội dung trong box */
        margin-bottom: 0;
        font-size: 0.9em;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

col_title_icon, col_title_text = st.columns([0.05, 0.95])
with col_title_icon:
    st.image("https://img.icons8.com/fluency/48/000000/statistics.png", width=48) # Thay bằng icon của bạn nếu có
with col_title_text:
    st.title("Interactive Analytics Dashboard")
st.caption("Select dimensions and filters to analyze your sales or inventory data.")

# --- Tabs Data Source ---
tab_sales, tab_inventory = st.tabs(["✔️ Sales Data", "📦 Inventory Data"])

with tab_sales:
    col_current_view, col_advanced_filters_placeholder = st.columns([0.7, 0.3])
    with col_current_view:
        st.markdown("**Current View:** <span style='color: #1E90FF;'>All Sales Data Overview</span>", unsafe_allow_html=True)
    with col_advanced_filters_placeholder:
        st.button("Advanced Filters", key="adv_filters_sales", help="Configure advanced filtering options")


    st.markdown("---") # Đường kẻ ngang

    # --- Filter Controls ---
    st.subheader("🔍 Filter Controls")

    filter_cols = st.columns(4)

    with filter_cols[0]:
        st.markdown("🗓️ **Time Dimension**")
        selected_time = st.selectbox("Select Time", time_options, key="time_select_sales", label_visibility="collapsed")
        st.info(f"Current: {selected_time}")

    with filter_cols[1]:
        st.markdown("👥 **Customer Dimension**")
        selected_customer = st.selectbox("Select Customer", customer_options, key="customer_select_sales", label_visibility="collapsed")
        st.success(f"Current: {selected_customer}") # Xanh lá

    with filter_cols[2]:
        st.markdown("🧊 **Item Dimension**") # Emoji khác
        selected_item = st.selectbox("Select Item", item_options, key="item_select_sales", label_visibility="collapsed")
        st.markdown(f"<span style='background-color: #E6E6FA; color: #4B0082; padding: 5px 10px; border-radius: 15px;'>Current: {selected_item}</span>", unsafe_allow_html=True) # Tím

    with filter_cols[3]:
        st.markdown("🌐 **Geography Dimension**")
        selected_geography = st.selectbox("Select Geography", geography_options, key="geography_select_sales", label_visibility="collapsed")
        st.warning(f"Current: {selected_geography}") # Cam

    # --- Apply Button and Table View ---
    apply_col, table_view_col = st.columns([0.8, 0.2])

    with apply_col:
        if st.button("🚀 Apply Filters & Visualize", use_container_width=True, type="primary"):
            st.session_state.applied_filters["time"] = selected_time
            st.session_state.applied_filters["customer"] = selected_customer
            st.session_state.applied_filters["item"] = selected_item
            st.session_state.applied_filters["geography"] = selected_geography
            st.session_state.show_data = True
            st.toast("Filters applied and data visualized!", icon="🎉")

    with table_view_col:
        view_option = st.selectbox(
            "📊 Table View",
            ["Chart View", "Table View"],
            key="view_select_sales",
            label_visibility="collapsed"
        )

    st.markdown("---")

    # --- Data Display Area ---
    if st.session_state.show_data:
        st.subheader("📊 Visualization / Data Table")
        if view_option == "Chart View":
            # Placeholder cho biểu đồ
            st.write(f"Displaying **Chart View** based on applied filters:")
            st.write(st.session_state.applied_filters)
            # Ví dụ: tạo biểu đồ thanh đơn giản
            chart_data = pd.DataFrame({
                'Category': ['A', 'B', 'C', 'D'],
                'Values': [
                    len(st.session_state.applied_filters['time']),
                    len(st.session_state.applied_filters['customer']),
                    len(st.session_state.applied_filters['item']),
                    len(st.session_state.applied_filters['geography'])
                ] # Giá trị ngẫu nhiên dựa trên độ dài tên filter
            })
            st.bar_chart(chart_data.set_index('Category'))
        else:
            # Placeholder cho bảng
            st.write(f"Displaying **Table View** based on applied filters:")
            # Ví dụ: tạo bảng từ các filter đã chọn
            df_filters = pd.DataFrame.from_dict(st.session_state.applied_filters, orient='index', columns=['Selected Value'])
            df_filters.index.name = "Dimension"
            st.dataframe(df_filters, use_container_width=True)

    else:
        # "No Data to Display" message
        st.markdown(
            """
            <div style="text-align: center; padding: 50px; background-color: #F9F9F9; border-radius: 10px;">
                <span style="font-size: 70px; opacity: 0.5;">🚫</span>
                <h3 style="color: #555;">No Data to Display</h3>
                <p style="color: #777;">Select dimension options and click <b>Apply Filters & Visualize</b> to visualize your data.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- Current Dimension Selections (hiển thị sau khi Apply) ---
    if st.session_state.show_data:
        st.subheader("📋 Current Dimension Selections")
        selection_cols = st.columns(4)

        with selection_cols[0]:
            st.markdown(
                f"""
                <div class="current-selection-box" style="border-left: 5px solid #007bff;">
                    <h5>🗓️ Time</h5>
                    <p>{st.session_state.applied_filters['time']}</p>
                </div>
                """, unsafe_allow_html=True
            )

        with selection_cols[1]:
            st.markdown(
                f"""
                <div class="current-selection-box" style="border-left: 5px solid #28a745;">
                    <h5>👥 Customer</h5>
                    <p>{st.session_state.applied_filters['customer']}</p>
                </div>
                """, unsafe_allow_html=True
            )

        with selection_cols[2]:
            st.markdown(
                f"""
                <div class="current-selection-box" style="border-left: 5px solid #6f42c1;">
                    <h5>🧊 Item</h5>
                    <p>{st.session_state.applied_filters['item']}</p>
                </div>
                """, unsafe_allow_html=True
            )

        with selection_cols[3]:
            st.markdown(
                f"""
                <div class="current-selection-box" style="border-left: 5px solid #ffc107;">
                    <h5>🌐 Geo</h5>
                    <p>{st.session_state.applied_filters['geography']}</p>
                </div>
                """, unsafe_allow_html=True
            )

with tab_inventory:
    st.header("Inventory Data Analysis")
    st.write("This section is for inventory data analysis. (To be implemented)")
    # Bạn có thể thêm các control tương tự như tab Sales Data ở đây

# --- Footer ---
st.markdown("---")
st.caption("Developed with Streamlit (Python)")
# Nút "Activ" không phải là một phần tử chuẩn của Streamlit, nó có vẻ là một watermark.
# Nếu bạn muốn thêm text ở góc, bạn có thể dùng HTML/CSS phức tạp hơn.
st.markdown("<div style='position: fixed; bottom: 10px; right: 20px; font-size: 24px; color: #cccccc; font-weight: bold; z-index: 9999;'>Activ</div>", unsafe_allow_html=True)
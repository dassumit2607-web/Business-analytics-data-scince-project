import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score



st.set_page_config(
    page_title="Business Sales & Profit Analytics",
    page_icon="📊",
    layout="wide"
)



st.title("📊 Business Sales & Profit Analytics")

st.write(
    "Upload your business CSV or Excel file and analyze "
    "sales, profit, products, categories, regions and trends."
)



currency_options = {
    "₹ INR": "₹",
    "$ USD": "$",
    "€ EUR": "€",
    "£ GBP": "£",
    "¥ JPY": "¥"
}

currency_name = st.sidebar.selectbox(
    "💰 Currency",
    list(currency_options.keys())
)

currency_symbol = currency_options[currency_name]




COLUMN_ALIASES = {

    "date": [
        "date",
        "order date",
        "transaction date",
        "sales date",
        "invoice date",
        "purchase date",
        "billing date",
        "bill date",
        "orderdate",
        "transactiondate",
        "invoicedate",
        "purchasedate"
    ],

    "product": [
        "product",
        "product name",
        "item",
        "item name",
        "product_name",
        "productname",
        "item_name",
        "itemname",
        "sku",
        "product title",
        "product_title"
    ],

    "sales": [
        "sales",
        "sale",
        "revenue",
        "total sales",
        "total sale",
        "sales amount",
        "sale amount",
        "revenue amount",
        "amount",
        "total amount",
        "selling price",
        "income",
        "turnover",
        "net sales",
        "gross sales",
        "sales value",
        "sales_value"
    ],

    "profit": [
        "profit",
        "net profit",
        "gross profit",
        "profit amount",
        "profit value",
        "net_profit",
        "gross_profit",
        "margin",
        "profit margin"
    ],

    "quantity": [
        "quantity",
        "qty",
        "units",
        "units sold",
        "number of units",
        "items sold",
        "volume",
        "count"
    ],

    "category": [
        "category",
        "product category",
        "product type",
        "type",
        "department",
        "group",
        "product group",
        "segment"
    ],

    "region": [
        "region",
        "area",
        "location",
        "zone",
        "territory",
        "city",
        "state",
        "branch",
        "market"
    ],

    "discount": [
        "discount",
        "discount rate",
        "discount %",
        "discount percentage",
        "discount percent",
        "discount_rate",
        "discount_percentage"
    ]
}



def normalize_name(name):
    """
    Makes column names easier to compare.
    """

    name = str(name)

    name = (
        name
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace(".", "")
    )

    name = " ".join(name.split())

    return name


def clean_column_names(df):
    """
    Removes hidden characters and unnecessary spaces.
    """

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
        .str.replace("\xa0", " ", regex=False)
    )

    return df


def find_column(df_columns, aliases):
    """
    Finds the best matching column.
    """

    normalized_columns = {
        normalize_name(col): col
        for col in df_columns
    }

    normalized_aliases = [
        normalize_name(alias)
        for alias in aliases
    ]

    # Exact match
    for alias in normalized_aliases:

        if alias in normalized_columns:

            return normalized_columns[alias]

    # Partial match
    for col_normalized, original_col in normalized_columns.items():

        for alias in normalized_aliases:

            if (
                alias in col_normalized
                or col_normalized in alias
            ):

                return original_col

    return None


def detect_columns(df):
    """
    Automatically detects business columns.
    """

    detected = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

        detected[standard_name] = find_column(
            df.columns,
            aliases
        )

    return detected


def convert_numeric(series):
    """
    Converts values such as:

    ₹1,200
    $500
    1,200
    500

    into numbers.
    """

    if pd.api.types.is_numeric_dtype(series):

        return pd.to_numeric(
            series,
            errors="coerce"
        )

    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace("£", "", regex=False)
        .str.replace("¥", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce"
    )


def money(value):

    if pd.isna(value):

        return f"{currency_symbol}0"

    return f"{currency_symbol}{value:,.2f}"


def format_number(value):

    if pd.isna(value):

        return "0"

    return f"{value:,.0f}"


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📁 Upload your business dataset",
    type=["csv", "xlsx", "xls"]
)


if uploaded_file is None:

    st.info(
        "Upload a CSV or Excel file to start the analysis."
    )

    st.markdown(
        """
        ### Your dataset can contain columns such as:

        **Required**
        - Date
        - Product
        - Sales / Revenue

        **Optional**
        - Profit
        - Quantity
        - Category
        - Region
        - Discount

        The app will automatically detect common column names.
        If it cannot, you can manually map them.
        """
    )

    st.stop()


# ============================================================
# READ FILE
# ============================================================

try:

    if uploaded_file.name.lower().endswith(".csv"):

        try:

            df = pd.read_csv(
                uploaded_file,
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            uploaded_file.seek(0)

            df = pd.read_csv(
                uploaded_file,
                encoding="latin1"
            )

    else:

        df = pd.read_excel(
            uploaded_file
        )

except Exception as e:

    st.error(
        f"❌ Could not read this file.\n\nError: {e}"
    )

    st.stop()


# ============================================================
# BASIC VALIDATION
# ============================================================

if df.empty:

    st.error(
        "❌ This file does not contain any data."
    )

    st.stop()


df = clean_column_names(df)


# ============================================================
# VIEW ORIGINAL COLUMNS
# ============================================================

with st.expander("🔎 View detected columns"):

    st.write(
        list(df.columns)
    )


# ============================================================
# AUTOMATIC COLUMN DETECTION
# ============================================================

detected = detect_columns(df)


# ============================================================
# COLUMN MAPPING
# ============================================================

st.sidebar.header("🔧 Column Mapping")

st.sidebar.caption(
    "The app automatically detects your columns. "
    "Change them manually if needed."
)


def mapping_dropdown(
    label,
    detected_value,
    required=False
):

    options = [
        "-- None --"
    ] + list(df.columns)

    if detected_value in df.columns:

        default_index = options.index(
            detected_value
        )

    else:

        default_index = 0

    selected = st.sidebar.selectbox(
        label,
        options,
        index=default_index
    )

    if selected == "-- None --":

        return None

    return selected


date_col = mapping_dropdown(
    "📅 Date column *",
    detected["date"],
    required=True
)

product_col = mapping_dropdown(
    "📦 Product column *",
    detected["product"],
    required=True
)

sales_col = mapping_dropdown(
    "💰 Sales / Revenue column *",
    detected["sales"],
    required=True
)

profit_col = mapping_dropdown(
    "📈 Profit column",
    detected["profit"]
)

quantity_col = mapping_dropdown(
    "🔢 Quantity column",
    detected["quantity"]
)

category_col = mapping_dropdown(
    "🏷️ Category column",
    detected["category"]
)

region_col = mapping_dropdown(
    "🌍 Region / Location column",
    detected["region"]
)

discount_col = mapping_dropdown(
    "🏷️ Discount column",
    detected["discount"]
)


# ============================================================
# REQUIRED COLUMN VALIDATION
# ============================================================

missing_required = []

if date_col is None:

    missing_required.append(
        "Date"
    )

if product_col is None:

    missing_required.append(
        "Product"
    )

if sales_col is None:

    missing_required.append(
        "Sales / Revenue"
    )


if missing_required:

    st.error(
        "❌ Please select the following required "
        "columns from the sidebar:"
    )

    for column in missing_required:

        st.write(
            f"- {column}"
        )

    st.info(
        "💡 Your dataset uses different column names. "
        "Select the correct columns manually from "
        "Column Mapping."
    )

    st.stop()


# ============================================================
# STANDARDIZE DATA
# ============================================================

work_df = df.copy()


# Date
work_df["date"] = pd.to_datetime(
    work_df[date_col],
    errors="coerce"
)


# Product
work_df["product"] = (
    work_df[product_col]
    .astype(str)
    .str.strip()
)


# Sales
work_df["sales"] = convert_numeric(
    work_df[sales_col]
)


# Profit
if profit_col:

    work_df["profit"] = convert_numeric(
        work_df[profit_col]
    )

else:

    work_df["profit"] = pd.NA


# Quantity
if quantity_col:

    work_df["quantity"] = convert_numeric(
        work_df[quantity_col]
    )

else:

    work_df["quantity"] = 1


# Category
if category_col:

    work_df["category"] = (
        work_df[category_col]
        .astype(str)
        .str.strip()
    )

else:

    work_df["category"] = "All"


# Region
if region_col:

    work_df["region"] = (
        work_df[region_col]
        .astype(str)
        .str.strip()
    )

else:

    work_df["region"] = "All"


# Discount
if discount_col:

    work_df["discount"] = convert_numeric(
        work_df[discount_col]
    )

else:

    work_df["discount"] = pd.NA


# ============================================================
# REMOVE INVALID ROWS
# ============================================================

before_rows = len(work_df)

work_df = work_df.dropna(
    subset=[
        "date",
        "product",
        "sales"
    ]
)

after_rows = len(work_df)

removed_rows = (
    before_rows - after_rows
)


if work_df.empty:

    st.error(
        "❌ After cleaning, no valid rows remained. "
        "Please check your Date, Product and Sales columns."
    )

    st.stop()


# ============================================================
# DATE FEATURES
# ============================================================

work_df["year_month"] = (
    work_df["date"]
    .dt.to_period("M")
    .astype(str)
)

work_df["month_name"] = (
    work_df["date"]
    .dt.strftime("%b %Y")
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.divider()

st.sidebar.header("🎛️ Filters")


# Region
if region_col:

    regions = sorted(
        work_df["region"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_regions = st.sidebar.multiselect(
        "Region",
        regions,
        default=regions
    )

    if selected_regions:

        work_df = work_df[
            work_df["region"].isin(
                selected_regions
            )
        ]


# Category
if category_col:

    categories = sorted(
        work_df["category"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_categories = st.sidebar.multiselect(
        "Category",
        categories,
        default=categories
    )

    if selected_categories:

        work_df = work_df[
            work_df["category"].isin(
                selected_categories
            )
        ]


# Date filter
min_date = (
    work_df["date"]
    .min()
    .date()
)

max_date = (
    work_df["date"]
    .max()
    .date()
)


selected_dates = st.sidebar.date_input(
    "Date range",
    value=(
        min_date,
        max_date
    ),
    min_value=min_date,
    max_value=max_date
)


if (
    isinstance(selected_dates, tuple)
    and len(selected_dates) == 2
):

    start_date, end_date = selected_dates

    work_df = work_df[
        (
            work_df["date"].dt.date
            >= start_date
        )
        &
        (
            work_df["date"].dt.date
            <= end_date
        )
    ]


# ============================================================
# CHECK AFTER FILTERING
# ============================================================

if work_df.empty:

    st.warning(
        "⚠️ No data matches the selected filters."
    )

    st.stop()


# ============================================================
# DATA QUALITY
# ============================================================

if removed_rows > 0:

    st.warning(
        f"⚠️ {removed_rows:,} rows were removed because "
        "their Date, Product or Sales value was invalid."
    )


# ============================================================
# KPI SECTION
# ============================================================

st.header("📌 Business Overview")


total_sales = (
    work_df["sales"].sum()
)

total_profit = (
    work_df["profit"].sum(
        min_count=1
    )
)

total_quantity = (
    work_df["quantity"].sum()
)

total_products = (
    work_df["product"].nunique()
)

total_records = len(work_df)


col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Total Sales",
        money(total_sales)
    )


with col2:

    if pd.isna(total_profit):

        st.metric(
            "Total Profit",
            "Not available"
        )

    else:

        st.metric(
            "Total Profit",
            money(total_profit)
        )


with col3:

    st.metric(
        "Products",
        format_number(
            total_products
        )
    )


with col4:

    st.metric(
        "Quantity",
        format_number(
            total_quantity
        )
    )


with col5:

    st.metric(
        "Records / Orders",
        format_number(
            total_records
        )
    )


# ============================================================
# PROFIT MARGIN
# ============================================================

if (
    not pd.isna(total_profit)
    and total_sales != 0
):

    profit_margin = (
        total_profit
        / total_sales
        * 100
    )

    st.info(
        f"📈 Overall profit margin: "
        f"**{profit_margin:.2f}%**"
    )


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Dashboard",
        "❓ Business Questions",
        "💡 Business Insights",
        "🔮 Sales Forecast"
    ]
)


# ============================================================
# TAB 1 - DASHBOARD
# ============================================================

with tab1:

    # --------------------------------------------------------
    # CATEGORY PERFORMANCE
    # --------------------------------------------------------

    if category_col:

        st.subheader(
            "🏷️ Category Performance"
        )

        category_data = (
            work_df
            .groupby("category")
            .agg(
                Sales=("sales", "sum"),
                Quantity=("quantity", "sum")
            )
        )

        if not work_df["profit"].isna().all():

            category_profit = (
                work_df
                .groupby("category")["profit"]
                .sum()
            )

            category_data["Profit"] = (
                category_profit
            )

        category_data = (
            category_data
            .sort_values(
                "Sales",
                ascending=False
            )
        )

        st.dataframe(
            category_data,
            use_container_width=True
        )


    # --------------------------------------------------------
    # MONTHLY TREND
    # --------------------------------------------------------

    st.subheader(
        "📅 Monthly Sales Trend"
    )

    monthly_data = (
        work_df
        .groupby("year_month")
        .agg(
            Sales=("sales", "sum")
        )
    )


    if not work_df["profit"].isna().all():

        monthly_data["Profit"] = (
            work_df
            .groupby("year_month")["profit"]
            .sum()
        )


    monthly_data = (
        monthly_data
        .sort_index()
    )


    fig, ax = plt.subplots(
        figsize=(12, 5)
    )


    ax.plot(
        monthly_data.index,
        monthly_data["Sales"],
        marker="o",
        label="Sales"
    )


    if "Profit" in monthly_data.columns:

        ax.plot(
            monthly_data.index,
            monthly_data["Profit"],
            marker="o",
            label="Profit"
        )


    ax.set_xlabel(
        "Month"
    )

    ax.set_ylabel(
        "Amount"
    )

    ax.set_title(
        "Monthly Sales and Profit"
    )

    ax.tick_params(
        axis="x",
        rotation=45
    )

    ax.legend()

    plt.tight_layout()

    st.pyplot(fig)


    # --------------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------------

    st.subheader(
        "🏆 Top Products by Sales"
    )


    top_products = (
        work_df
        .groupby("product")["sales"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )


    fig, ax = plt.subplots(
        figsize=(10, 5)
    )


    top_products.sort_values().plot(
        kind="barh",
        ax=ax
    )


    ax.set_xlabel(
        "Sales"
    )

    ax.set_ylabel(
        "Product"
    )

    ax.set_title(
        "Top 10 Products"
    )


    plt.tight_layout()

    st.pyplot(fig)


    # --------------------------------------------------------
    # REGIONAL PERFORMANCE
    # --------------------------------------------------------

    if region_col:

        st.subheader(
            "🌍 Regional Performance"
        )


        region_data = (
            work_df
            .groupby("region")
            .agg(
                Sales=("sales", "sum"),
                Quantity=("quantity", "sum"),
                Records=("product", "count")
            )
        )


        if not work_df["profit"].isna().all():

            region_data["Profit"] = (
                work_df
                .groupby("region")["profit"]
                .sum()
            )


        region_data = (
            region_data
            .sort_values(
                "Sales",
                ascending=False
            )
        )


        st.dataframe(
            region_data,
            use_container_width=True
        )


    # --------------------------------------------------------
    # DISCOUNT VS PROFIT
    # --------------------------------------------------------

    if (
        discount_col
        and not work_df["profit"].isna().all()
    ):

        st.subheader(
            "🏷️ Discount vs Profit"
        )


        discount_data = (
            work_df[
                [
                    "discount",
                    "profit"
                ]
            ]
            .dropna()
        )


        if not discount_data.empty:

            fig, ax = plt.subplots(
                figsize=(10, 5)
            )


            ax.scatter(
                discount_data["discount"],
                discount_data["profit"],
                alpha=0.6
            )


            ax.set_xlabel(
                "Discount"
            )

            ax.set_ylabel(
                "Profit"
            )

            ax.set_title(
                "Relationship Between Discount and Profit"
            )


            plt.tight_layout()

            st.pyplot(fig)


# ============================================================
# TAB 2 - BUSINESS QUESTIONS
# ============================================================

with tab2:

    st.header(
        "❓ Business Questions"
    )


    # --------------------------------------------------------
    # BEST SELLING PRODUCT
    # --------------------------------------------------------

    st.subheader(
        "1️⃣ Which product sells the most?"
    )


    product_sales = (
        work_df
        .groupby("product")["sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    if not product_sales.empty:

        best_product = (
            product_sales.index[0]
        )

        best_product_sales = (
            product_sales.iloc[0]
        )


        st.success(
            f"🏆 **{best_product}** "
            f"has the highest sales: "
            f"**{money(best_product_sales)}**"
        )


    # --------------------------------------------------------
    # MOST PROFITABLE PRODUCT
    # --------------------------------------------------------

    st.subheader(
        "2️⃣ Which product is most profitable?"
    )


    if not work_df["profit"].isna().all():

        product_profit = (
            work_df
            .groupby("product")["profit"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        best_profit_product = (
            product_profit.index[0]
        )

        best_profit = (
            product_profit.iloc[0]
        )


        st.success(
            f"💰 **{best_profit_product}** "
            f"has the highest profit: "
            f"**{money(best_profit)}**"
        )


    else:

        st.info(
            "Profit data is not available."
        )


    # --------------------------------------------------------
    # BEST CATEGORY
    # --------------------------------------------------------

    st.subheader(
        "3️⃣ Which category performs best?"
    )


    if category_col:

        category_sales = (
            work_df
            .groupby("category")["sales"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        best_category = (
            category_sales.index[0]
        )


        st.success(
            f"🏷️ Highest-sales category: "
            f"**{best_category}** "
            f"with "
            f"{money(category_sales.iloc[0])}"
        )


    else:

        st.info(
            "Category information is not available."
        )


    # --------------------------------------------------------
    # HIGHEST SALES MONTH
    # --------------------------------------------------------

    st.subheader(
        "4️⃣ Which month had the highest sales?"
    )


    monthly_sales = (
        work_df
        .groupby("year_month")["sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    best_sales_month = (
        monthly_sales.index[0]
    )


    st.success(
        f"📅 Highest-sales month: "
        f"**{best_sales_month}** "
        f"with "
        f"{money(monthly_sales.iloc[0])}"
    )


    # --------------------------------------------------------
    # HIGHEST PROFIT MONTH
    # --------------------------------------------------------

    st.subheader(
        "5️⃣ Which month had the highest profit?"
    )


    if not work_df["profit"].isna().all():

        monthly_profit = (
            work_df
            .groupby("year_month")["profit"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        best_profit_month = (
            monthly_profit.index[0]
        )


        st.success(
            f"📈 Highest-profit month: "
            f"**{best_profit_month}** "
            f"with "
            f"{money(monthly_profit.iloc[0])}"
        )


    else:

        st.info(
            "Profit data is not available."
        )


    # --------------------------------------------------------
    # BEST REGION
    # --------------------------------------------------------

    st.subheader(
        "6️⃣ Which region performs best?"
    )


    if region_col:

        region_sales = (
            work_df
            .groupby("region")["sales"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        best_region = (
            region_sales.index[0]
        )


        st.success(
            f"🌍 Highest-sales region: "
            f"**{best_region}** "
            f"with "
            f"{money(region_sales.iloc[0])}"
        )


    else:

        st.info(
            "Region information is not available."
        )


    # --------------------------------------------------------
    # DISCOUNT CORRELATION
    # --------------------------------------------------------

    st.subheader(
        "7️⃣ Does discount appear related to profit?"
    )


    if (
        discount_col
        and not work_df["profit"].isna().all()
    ):

        correlation_df = (
            work_df[
                [
                    "discount",
                    "profit"
                ]
            ]
            .dropna()
        )


        if len(correlation_df) > 1:

            correlation = (
                correlation_df["discount"]
                .corr(
                    correlation_df["profit"]
                )
            )


            st.write(
                f"Correlation between discount "
                f"and profit: "
                f"**{correlation:.2f}**"
            )


            st.caption(
                "Correlation shows association, "
                "not causation."
            )


    else:

        st.info(
            "Discount and Profit are required "
            "for this analysis."
        )


# ============================================================
# TAB 3 - BUSINESS INSIGHTS
# ============================================================

with tab3:

    st.header(
        "💡 Business Insights"
    )


    st.write(
        "These insights are generated from "
        "the uploaded data."
    )


    # --------------------------------------------------------
    # PRODUCT INSIGHT
    # --------------------------------------------------------

    product_sales = (
        work_df
        .groupby("product")["sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    if not product_sales.empty:

        top_product = (
            product_sales.index[0]
        )

        top_product_value = (
            product_sales.iloc[0]
        )


        percentage = (
            top_product_value
            / total_sales
            * 100
        )


        st.info(
            f"📦 **Product Insight:** "
            f"{top_product} generated "
            f"{money(top_product_value)}, "
            f"which represents approximately "
            f"**{percentage:.1f}%** of total sales."
        )


    # --------------------------------------------------------
    # PROFIT INSIGHT
    # --------------------------------------------------------

    if not work_df["profit"].isna().all():

        product_profit = (
            work_df
            .groupby("product")["profit"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        best_profit_product = (
            product_profit.index[0]
        )

        best_profit_value = (
            product_profit.iloc[0]
        )


        st.info(
            f"💰 **Profit Insight:** "
            f"{best_profit_product} generated "
            f"the highest total profit of "
            f"{money(best_profit_value)}."
        )


        negative_products = (
            product_profit[
                product_profit < 0
            ]
        )


        if not negative_products.empty:

            st.warning(
                f"⚠️ **Attention:** "
                f"{len(negative_products)} "
                f"product(s) have negative total profit."
            )


    # --------------------------------------------------------
    # CATEGORY INSIGHT
    # --------------------------------------------------------

    if category_col:

        category_sales = (
            work_df
            .groupby("category")["sales"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        if not category_sales.empty:

            best_category = (
                category_sales.index[0]
            )


            st.info(
                f"🏷️ **Category Insight:** "
                f"{best_category} has the highest "
                f"total sales."
            )


    # --------------------------------------------------------
    # REGION INSIGHT
    # --------------------------------------------------------

    if region_col:

        region_sales = (
            work_df
            .groupby("region")["sales"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        if not region_sales.empty:

            best_region = (
                region_sales.index[0]
            )


            st.info(
                f"🌍 **Regional Insight:** "
                f"{best_region} generated the "
                f"highest sales."
            )


    # --------------------------------------------------------
    # DISCOUNT INSIGHT
    # --------------------------------------------------------

    if (
        discount_col
        and not work_df["profit"].isna().all()
    ):

        discount_profit = (
            work_df[
                [
                    "discount",
                    "profit"
                ]
            ]
            .dropna()
        )


        if len(discount_profit) > 1:

            correlation = (
                discount_profit["discount"]
                .corr(
                    discount_profit["profit"]
                )
            )


            if correlation < -0.3:

                st.warning(
                    "🏷️ **Discount Insight:** "
                    "Higher discounts show a negative "
                    "association with profit in this dataset."
                )


            elif correlation > 0.3:

                st.info(
                    "🏷️ **Discount Insight:** "
                    "Discount and profit show a positive "
                    "association in this dataset."
                )


            else:

                st.info(
                    "🏷️ **Discount Insight:** "
                    "The relationship between discount "
                    "and profit appears relatively weak."
                )


            st.caption(
                "This is an observed statistical relationship, "
                "not proof that discounts caused the change."
            )


# ============================================================
# TAB 4 - SALES FORECAST
# ============================================================

with tab4:

    st.header(
        "🔮 Sales Forecast"
    )

    st.write(
        
        "History, used to project sales for the months ahead."
    )


    # --------------------------------------------------------
    # BUILD MONTHLY HISTORY
    # --------------------------------------------------------

    monthly_sales = (
        work_df
        .groupby("year_month")["sales"]
        .sum()
        .sort_index()
    )


    if len(monthly_sales) < 6:

        st.info(
            "Not enough monthly history to build a forecast "
            "(need at least 6 months of data)."
        )

    else:

        # ----------------------------------------------------
        # FEATURE ENGINEERING
        # ----------------------------------------------------
        # t = a simple time index (0, 1, 2, ...) that captures
        # the overall trend.
        # month_sin / month_cos = a cyclical encoding of the
        # calendar month, so the model can learn seasonal
        # patterns (e.g. a December spike) without treating
        # month "12" and month "1" as far apart.

        history = pd.DataFrame(
            {
                "year_month": monthly_sales.index,
                "sales": monthly_sales.values
            }
        )

        history["t"] = range(len(history))

        history["month_num"] = (
            history["year_month"]
            .apply(lambda ym: pd.Period(ym, freq="M").month)
        )

        history["month_sin"] = np.sin(
            2 * np.pi * history["month_num"] / 12
        )

        history["month_cos"] = np.cos(
            2 * np.pi * history["month_num"] / 12
        )

        feature_columns = [
            "t",
            "month_sin",
            "month_cos"
        ]


        # ----------------------------------------------------
        # TRAIN / TEST SPLIT (for an honest accuracy check)
        # ----------------------------------------------------

        test_size = max(
            3,
            int(len(history) * 0.2)
        )

        test_size = min(
            test_size,
            len(history) - 3
        )

        train_history = history.iloc[:-test_size]
        test_history = history.iloc[-test_size:]

        eval_model = LinearRegression()

        eval_model.fit(
            train_history[feature_columns],
            train_history["sales"]
        )

        test_predictions = eval_model.predict(
            test_history[feature_columns]
        )

        mae = mean_absolute_error(
            test_history["sales"],
            test_predictions
        )

        r2 = r2_score(
            test_history["sales"],
            test_predictions
        )


        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Avg. Monthly Error (MAE)",
                money(mae)
            )

        with col2:
            st.metric(
                "R² on Recent Months",
                f"{r2:.2f}"
            )

        st.caption(
            f"Measured by predicting the last {test_size} months "
            "using only the months before them — this is how "
            "accurate the forecast below is likely to be, not "
            "how well it fits data it already saw."
        )

        st.divider()


        # ----------------------------------------------------
        # FORECAST HORIZON
        # ----------------------------------------------------

        horizon = st.slider(
            "Months to forecast ahead",
            min_value=1,
            max_value=12,
            value=3
        )


        # Refit on the FULL history for the actual forecast,
        # now that accuracy has already been measured honestly
        # above.

        final_model = LinearRegression()

        final_model.fit(
            history[feature_columns],
            history["sales"]
        )

        last_period = pd.Period(
            history["year_month"].iloc[-1],
            freq="M"
        )

        future_periods = [
            last_period + i
            for i in range(1, horizon + 1)
        ]

        future_df = pd.DataFrame(
            {
                "year_month": [str(p) for p in future_periods],
                "t": range(
                    len(history),
                    len(history) + horizon
                ),
                "month_num": [p.month for p in future_periods]
            }
        )

        future_df["month_sin"] = np.sin(
            2 * np.pi * future_df["month_num"] / 12
        )

        future_df["month_cos"] = np.cos(
            2 * np.pi * future_df["month_num"] / 12
        )

        future_df["predicted_sales"] = final_model.predict(
            future_df[feature_columns]
        )

        # A simple trend model can dip below zero for a
        # declining series - sales can't actually be negative.
        future_df["predicted_sales"] = future_df["predicted_sales"].clip(lower=0)


        # ----------------------------------------------------
        # CHART: HISTORY + FORECAST
        # ----------------------------------------------------

        fig, ax = plt.subplots(
            figsize=(12, 5)
        )

        ax.plot(
            history["year_month"],
            history["sales"],
            marker="o",
            label="Actual Sales"
        )

        ax.plot(
            future_df["year_month"],
            future_df["predicted_sales"],
            marker="o",
            linestyle="--",
            color="orange",
            label="Forecast"
        )

        ax.set_xlabel(
            "Month"
        )

        ax.set_ylabel(
            "Sales"
        )

        ax.set_title(
            "Monthly Sales: Actual vs Forecast"
        )

        ax.tick_params(
            axis="x",
            rotation=45
        )

        ax.legend()

        plt.tight_layout()

        st.pyplot(fig)


        # ----------------------------------------------------
        # FORECAST TABLE
        # ----------------------------------------------------

        st.subheader(
            "📋 Forecasted Values"
        )

        display_forecast = future_df[
            [
                "year_month",
                "predicted_sales"
            ]
        ].rename(
            columns={
                "year_month": "Month",
                "predicted_sales": "Predicted Sales"
            }
        )

        display_forecast["Predicted Sales"] = (
            display_forecast["Predicted Sales"]
            .apply(money)
        )

        st.dataframe(
            display_forecast,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
          "This is a simple Trend  +It can be wrong, so use it as a rough guide, not a guarantee."
        )


# ============================================================
# CLEANED DATA
# ============================================================

st.divider()


with st.expander("📄 View cleaned data"):

    st.dataframe(
        work_df,
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Business Sales & Profit Analytics | "
    "Developed by Sumit Das | 2026|"
)
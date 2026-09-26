import pandas as pd


def clean_column_names(df):
    """Remove unnecessary spaces and hidden characters from column names."""

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
        .str.replace("\xa0", " ", regex=False)
    )

    return df


def clean_data(df):
    """
    Convert raw business data into the standard format
    used by the project.
    """

    df = clean_column_names(df)

    # Map common business/Superstore column names
    column_mapping = {
        "Order Date": "date",
        "Product Name": "product",
        "Category": "category",
        "Quantity": "quantity",
        "Sales": "sales",
        "Profit": "profit",
        "Discount": "discount",
        "Region": "region",
    }

    # Rename only columns that actually exist
    df = df.rename(
        columns={
            old: new
            for old, new in column_mapping.items()
            if old in df.columns
        }
    )

    # Convert numeric columns
    numeric_columns = [
        "quantity",
        "sales",
        "profit",
        "discount"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Convert date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Remove rows missing essential business information
    required_columns = [
        "date",
        "product",
        "sales"
    ]

    existing_required = [
        col for col in required_columns
        if col in df.columns
    ]

    if existing_required:
        df = df.dropna(
            subset=existing_required
        )

    return df
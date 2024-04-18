import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm

# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="SRR Anlaytics Tool",
    layout="wide"
)

# Establish communication between PygWalker and Streamlit
init_streamlit_comm()

# Main Header
st.title("EDA Tool for Data Analytics 📊")
st.write("---")

# Function to load data
@st.cache_data(ttl=120, show_spinner=True)
def load_data(url):
    df = pd.read_csv(url)
    df['Date Created'] = pd.to_datetime(df['Date Created'], errors='coerce')  # set 'Date Created' as datetime
    df.rename(columns={'In process (On It SME)': 'SME (On It)'}, inplace=True)  # Renaming column
    return df

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSQVnfH-edbXqAXxlCb2FrhxxpsOHJhtqKMYsHWxf5SyLVpAPTSIWQeIGrBAGa16dE4CA59o2wyz59G/pub?gid=0&single=true&output=csv'
dataframe = load_data(url).copy()

# Display PygWalker interface
renderer = StreamlitRenderer(dataframe, spec="./gw_config.json", spec_io_mode="rw")
renderer.render_explore()

# Function to perform EDA
def perform_eda(dataframe):
    st.markdown("***Dataset Shape:***")
    st.write(dataframe.shape)
    st.divider()
    st.markdown("***First 5 Rows:***")
    st.write(dataframe.head())
    st.markdown("***Last 5 Rows:***")
    st.write(dataframe.tail())
    st.divider()

    # Display columns and their data types
    column_types = pd.DataFrame(dataframe.dtypes, columns=["Data Type"])
    column_types.index.name = "Column"
    st.markdown("***Dataset Columns and Data Types:***")
    st.table(column_types)
    st.divider()

    # Display summary statistics
    st.markdown("***Summary Statistics***")
    st.write(dataframe.describe(include='all'))
    
    st.divider()
    unique_values = dataframe.nunique()
    unique_values_df = pd.DataFrame({"Columns": unique_values.index, "Count of Unique Values": unique_values.values})
    unique_values_df.index += 1
    st.markdown("***Unique Value Count***")
    st.table(unique_values_df)
    
    # Get columns with missing values
    null_columns = dataframe.columns[dataframe.isnull().any()].tolist()
    null_counts = dataframe.isnull().sum()

    if null_columns:
        st.divider()
        st.markdown("***Columns With Null Values:***")
        null_columns_df = pd.DataFrame({"Columns with Null": null_columns, "Number of Nulls": [null_counts[col] for col in null_columns]})
        null_columns_df = null_columns_df.reset_index(drop=True, inplace=False)
        null_columns_df.index += 1
        st.table(null_columns_df)
        
        # Selectbox for choosing column to view Nulls
        selected_column = st.selectbox("Select a column to view Nulls:", null_columns)
        
        # Display Nulls for the selected column
        null_rows = dataframe[dataframe[selected_column].isnull()]
        st.write(f"Rows with Nulls in '{selected_column}':")
        st.dataframe(null_rows)
    else:
        st.write("No missing values found in the dataset.")

    st.divider()

    # Identify columns with duplicates
    duplicates_info = {col: dataframe.duplicated(subset=[col]).sum() for col in dataframe.columns if dataframe.duplicated(subset=[col]).sum() > 0}
    
    if duplicates_info:
        st.write("Columns With Duplicates:")
        st.table(pd.DataFrame.from_dict(duplicates_info, orient='index', columns=['Count of Duplicates']))
        
        # Selection for detailed duplicate view
        column_to_view = st.selectbox("Select a column to view duplicates:", options=list(duplicates_info.keys()))
        
        # Display duplicates for the selected column
        duplicates = dataframe[dataframe.duplicated(subset=[column_to_view], keep=False)].sort_values(by=[column_to_view])
        st.write(f"Duplicates in '{column_to_view}':")
        st.dataframe(duplicates)
    else:
        st.write("No columns with duplicates found.")

# Display EDA
if dataframe is not None:
    perform_eda(dataframe)
else:
    st.header("Error Reading Data")

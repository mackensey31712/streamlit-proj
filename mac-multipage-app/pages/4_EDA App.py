import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm

# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="PygWalker in Streamlit",
    layout="wide"
)

# Establish communication between PygWalker and Streamlit
init_streamlit_comm()

# Main Header
st.header("Welcome To My EDA Tool")

# Sidebar for file upload
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")

# Function to perform EDA
def perform_eda(dataframe):
    st.write("Dataset Shape:", dataframe.shape)
    st.write("First 5 Rows:", dataframe.head())
    st.write("Last 5 Rows:", dataframe.tail())
    dataframe.info(verbose=True)
    st.write("Unique Values in Each Column:", dataframe.nunique())
    st.write("Summary Statistics:", dataframe.describe(include='all'))

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

# Function to initialize PygWalker with uploaded DataFrame
@st.cache_resource
def get_pyg_renderer(dataframe) -> "StreamlitRenderer":
    return StreamlitRenderer(dataframe, spec="./gw_config.json", debug=False)

if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)

    # Display EDA
    perform_eda(dataframe)
    
    # Initialize and render PygWalker exploration interface
    renderer = get_pyg_renderer(dataframe)
    renderer.render_explore()
else:
    # If no file is uploaded, prompt the user to upload a CSV file
    st.title(":point_left: Please upload a CSV file to get started")

import streamlit as st
import pandas as pd
import pygwalker as pyg
from pygwalker.api.streamlit  import StreamlitRenderer, init_streamlit_comm
import matplotlib.pyplot as plt
import altair as alt


# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="PygWalker in Streamlit",
    layout="wide"
)

# Establish communication between PygWalker and Streamlit
init_streamlit_comm()

# Main Header
st.title("EDA Tool for Data Analytics 📊")
st.write("---")
# Sidebar for file upload
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")

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
    # unique_values_df = pd.DataFrame(dataframe.nunique(), columns=["Count of Unique Values"])
    st.markdown("***Unique Value Count***")
    st.table(unique_values_df)
    # st.write("Unique Values in Each Column:", dataframe.nunique()

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

    # Add the new code to create the SME summary table
    def seconds_to_hms(seconds):
        if pd.notnull(seconds):
            hours = int(seconds) // 3600
            minutes = (int(seconds) % 3600) // 60
            seconds = int(seconds) % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return "N/A"

    df_grouped = dataframe.groupby('SME (On It)').agg(
        Avg_On_It_Sec=pd.NamedAgg(column='TimeTo: On It Sec', aggfunc='mean'),
        Avg_Attended_Sec=pd.NamedAgg(column='TimeTo: Attended Sec', aggfunc='mean'),
        Number_of_Interactions=pd.NamedAgg(column='SME (On It)', aggfunc='count')
    ).reset_index()
    df_grouped['Total_Avg_Sec'] = df_grouped['Avg_On_It_Sec'] + df_grouped['Avg_Attended_Sec']
    df_sorted = df_grouped.sort_values(by=['Total_Avg_Sec', 'Number_of_Interactions'], ascending=[True, False])
    df_sorted['Avg_On_It'] = df_sorted['Avg_On_It_Sec'].apply(seconds_to_hms)
    df_sorted['Avg_Attended'] = df_sorted['Avg_Attended_Sec'].apply(seconds_to_hms)
    df_sorted.rename(columns={'SME (On It)': 'SME'}, inplace=True)

    st.subheader("SME Handle Time Table")
    st.dataframe(df_sorted[['SME', 'Avg_On_It', 'Avg_Attended']].set_index('SME'))
    # st.dataframe(df_sorted[['SME', 'Avg_On_It', 'Avg_Attended', 'Number_of_Interactions']].set_index('SME'))

    # Convert the 'Avg_On_It_Sec' and 'Avg_Attended_Sec' columns to minutes
    df_sorted['Avg_On_It_Min'] = df_sorted['Avg_On_It_Sec'] / 60
    df_sorted['Avg_Attended_Min'] = df_sorted['Avg_Attended_Sec'] / 60

    # # Sort the DataFrame by 'Avg_On_It' in descending order
    # df_sorted = df_sorted.sort_values('Avg_On_It_Min', ascending=False)

    ## Simple pyplot chart------------------
    # fig, ax = plt.subplots()
    # df_sorted.plot(x='SME', y=['Avg_On_It_Min', 'Avg_Attended_Min'], kind='bar', ax=ax)
    # st.pyplot(fig)
    ## ------------------------------------

    # Define the Altair chart for Avg_On_It_Min
    chart_on_it = alt.Chart(df_sorted).mark_bar().encode(
        x=alt.X('SME', title='SME', sort='-y'),
        y=alt.Y('Avg_On_It_Min:Q', title='Average Time On It (Minutes)'),
        color=alt.condition(
            alt.datum.Avg_On_It_Min > 5,
            alt.value('red'),
            alt.value('steelblue')
        ),
        tooltip=['SME', alt.Tooltip('Avg_On_It_Min:Q', title='Average Time On It (Minutes)')]
    ).properties(
        width=600,
        height=400,
        title='Average Time On It by SME'
    )

    # Define the Altair chart for Avg_Attended_Min
    chart_attended = alt.Chart(df_sorted).mark_bar().encode(
        x=alt.X('SME', title='SME', sort='-y'),
        y=alt.Y('Avg_Attended_Min:Q', title='Average Time Attended (Minutes)'),
        tooltip=['SME', alt.Tooltip('Avg_Attended_Min:Q', title='Average Time Attended (Minutes)')]
    ).properties(
        width=600,
        height=400,
        title='Average Time Attended by SME'
    )

    # Display the charts using Altair's interactive renderer
    st.altair_chart(chart_on_it, use_container_width=True)
    st.altair_chart(chart_attended, use_container_width=True)


# Function to initialize PygWalker with uploaded DataFrame
@st.cache_resource
def get_pyg_renderer(dataframe) -> "StreamlitRenderer":
    return StreamlitRenderer(dataframe, spec="./gw_config.json", spec_io_mode="rw")

if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)

    # Display EDA
    perform_eda(dataframe)
    
    # Initialize and render PygWalker exploration interface
    renderer = get_pyg_renderer(dataframe)
    renderer.render_explore()
else:
    # If no file is uploaded, prompt the user to upload a CSV file
    st.header(":point_left: Please upload a CSV file to get started")

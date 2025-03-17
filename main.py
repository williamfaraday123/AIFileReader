import streamlit as st 
import pandas as pd

st.title("Hiring- FullStack Challenge")

# function to read the file into a dataframe and return as a dataframe
def load_file(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xls') or file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        st.error('Unsupported file type. Only allow CSV or Excel files')
        return None

# allow user to upload file
uploaded_files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xls", "xlsx"], accept_multiple_files=True)

# system will convert file to dataframe and append to dataframes object
dataframes = {}
if uploaded_files:
    for uploaded_file in uploaded_files:
        dataframe = load_file(uploaded_file)
        if dataframe is not None:
            dataframes[uploaded_file.name] = dataframe

if dataframes:
    # allow user to select a file
    selected_file_display = st.selectbox("Select a file to display", list(dataframes.keys()))
    # allow user to select number of rows N to display
    n_rows = st.number_input("Enter number of rows of the file to display", min_value=1, step=1)
    # display top N rows of selected file
    st.dataframe(data=dataframes[selected_file_display].head(n_rows))

    # allow user to select a file
    selected_file_query = st.selectbox("Select a file to query", list(dataframes.keys()))
    # allow user to enter queries on the selected file
    query = st.chat_input("Enter your question")


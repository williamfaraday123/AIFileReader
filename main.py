import streamlit as st 
import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
openapi_key = os.getenv("OPENAPI_KEY")
if not openapi_key:
    st.error("OpenAPI key is missing. Please add it to your .env file.")

if "history" not in st.session_state:
    st.session_state.history = []
    
st.title("Isaac: Hiring- FullStack Challenge")

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

    st.subheader("Display")
    # allow user to select a file
    selected_file_display = st.selectbox("Select a file to display", list(dataframes.keys()))
    # allow user to select number of rows N to display
    n_rows = st.number_input("Enter number of rows of the file to display", min_value=1, step=1)
    # display top N rows of selected file
    st.dataframe(data=dataframes[selected_file_display].head(n_rows))

    st.subheader("Query")
    # allow user to select a file
    selected_files_query = []
    st.write("Select files to query")    
    for file in dataframes.keys():
        if st.checkbox(file, key=file):
            selected_files_query.append(file)

    # allow user to enter queries on the selected file
    query = st.text_input("Enter your query", key="query_input")
    
    feedback = None

    if query and query.strip() and len(selected_files_query) > 0:
        # instantiate llm
        llm = OpenAI(api_token = openapi_key)
        pandas_ai = PandasAI(llm, conversational=False)
        try:
            response = pandas_ai([dataframes[selected_file_query] for selected_file_query in selected_files_query], prompt = query)
            #st.write("response type:", type(response)) #for debugging
            
            if response is not None and not (isinstance(response, pd.DataFrame) and response.empty) and not (isinstance(response, list) and len(response) == 0) and not (isinstance(response, dict) and len(response) == 0):
                if isinstance(response, pd.DataFrame):
                    st.dataframe(response)
                elif isinstance(response, list):
                    response = pd.DataFrame(response)
                    st.table(response)
                elif isinstance(response, dict):
                    response = pd.DataFrame(list(response.items()), columns=["Key", "Value"])
                    st.table(response)
                elif isinstance(response, bool):
                    response = "Yes" if response else "No"
                    st.write(response)
                else:
                    st.write(response)
            else:
                response = "No results found"
                st.write(response)

            #collect user feedback
            if query and response is not None and not (isinstance(response, pd.DataFrame) and response.empty):
                feedback = st.radio(
                    "Rate the response",
                    ["Excellent", "Good", "Acceptable", "Bad", "Very bad"],
                    index=None
                )
                #store query, responses and feedback in session state
                if feedback is not None:
                    for item in st.session_state.history:
                        if item["query"] == query:
                            item["feedback"] = feedback
                            break
                    else:
                        st.session_state.history.append({
                            "query": query,
                            "response": response,
                            "feedback": feedback
                        })
                else:
                    st.session_state.history.append({
                        "query": query,
                        "response": response,
                        "feedback": "None"
                    })

                if feedback is not None:
                    st.write(f"Thank you for your feedback! You selected: {feedback}")

        except Exception as e:
            st.error(f"An error occurred while processing your query: {str(e)}")
            response = None

    #display prompt history
    if len(st.session_state.history) > 0:
        st.subheader("Prompt History:")
        for item in st.session_state.history:
            st.write(f"**Query:**")
            st.write(f"{item['query']}")
            st.write(f"**Response:**")
            if isinstance(item['response'], pd.DataFrame):
                st.dataframe(item['response'])
            else:
                st.write(item['response'])
            st.write(f"**Response Feedback:**")
            st.write(f"{item['feedback']}")
            st.divider()

# for debugging 
#    else:
#        st.write('Query:', query)
#        st.write('Selected files:', selected_files_query)       
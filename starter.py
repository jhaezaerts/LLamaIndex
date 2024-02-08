from data_connectors.data_connectors import load_rdf, load_sdd, df_reader
from models.models import get_model
from prompt_engineering.pydantic_output import RdfData, SddData
from prompt_engineering.prompt import get_user_response

from llama_index import (
    ServiceContext,
    VectorStoreIndex
)


RDF_FOLDER_PATH = "./data/turtle docs"
SDD_FOLDER_PATH = "./data/sdd docs"


import streamlit as st

col01, col02, col03 = st.columns([0.25, 0.5, 0.25])
with col02:
    st.image("https://www.hda.belgium.be/themes/custom/hda/logo.svg")

user_request = st.text_input("Search", label_visibility='hidden')
st.write("")

col11, col12, col13 = st.columns([0.425, 0.15, 0.425])
with col12:
    search_button = st.button("Search")

if search_button or user_request:

    # RDF section
    rdf_docs = load_rdf(RDF_FOLDER_PATH)
    sdd_docs = load_sdd(SDD_FOLDER_PATH)
    docs = rdf_docs + sdd_docs

    service_context = ServiceContext.from_defaults(llm=get_model("gpt-4"))
    index = VectorStoreIndex.from_documents(docs, service_context=service_context)
    query_engine = index.as_query_engine(output_cls=RdfData) # response_mode = [refine, compact, tree_summarize, simple_summarize, accumulate, compact_accumulate]

    rdf_response = query_engine.query(user_request)


    # SDD section
    sdd_df_list = df_reader(SDD_FOLDER_PATH)
    datasets = rdf_response.datasets

    relevant_dfs = [df for df in sdd_df_list if df["dataset"].isin(datasets).any()]
    sdd_dict = {}
    columns = []
    pii = False

    for df in relevant_dfs:
        columns.append(list(zip(df["Column"], df["Label"]))) # keeping track of columns and column descriptions in case of joining datasets
        if "Column_sensitive_personal_data" in df:
            if (df["Column_sensitive_personal_data"] == "Yes").any():
                pii = True

    sdd_dict["columns"] = columns
    sdd_dict["pii"] = pii

    sdd_response = SddData(**sdd_dict)


    # Get user response in streamlit

    user_response = get_user_response(user_request, rdf_response, sdd_response)
    st.write(user_response)


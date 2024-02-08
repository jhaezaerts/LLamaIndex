from llama_index import (
    VectorStoreIndex, 
    ServiceContext,
)

from data_connectors.data_connectors import rdf_loader, sdd_loader, df_reader, df_loader
from prompt_engineering.pydantic_output import DataRequest, RdfData, SddData
from models.models import get_model

import pandas as pd
from llama_index.query_engine import PandasQueryEngine


sdd_path = "./data/sdd docs"
rdf_path = "./data/turtle docs"


if __name__ == "__main__":

    service_context = ServiceContext.from_defaults(llm=get_model("gpt-4"))


    # DATA CONNECTORS

    # load json representations of csv and ttl as Documents
    sdd_json_docs = sdd_loader(sdd_path)
    rdf_json_docs = rdf_loader(rdf_path)
    json_docs = sdd_json_docs + rdf_json_docs

    # read a list of dataframes
    sdd_df_list = df_reader(sdd_path)
    rdf_df_list = df_reader(rdf_path)
 

    # load dataframe representations of csv and ttl as Documents
    sdd_df_docs = df_loader(sdd_df_list, concat_df=False)
    rdf_df_docs = df_loader(rdf_df_list, concat_df=False)
    df_docs = sdd_df_docs + rdf_df_docs


    # INDEXING

    sdd_json_index = VectorStoreIndex.from_documents(sdd_json_docs, service_context=service_context)
    rdf_json_index = VectorStoreIndex.from_documents(rdf_json_docs, service_context=service_context)
    json_index = VectorStoreIndex.from_documents(json_docs, service_context=service_context)

    sdd_df_index = VectorStoreIndex.from_documents(sdd_df_docs, service_context=service_context)
    rdf_df_index = VectorStoreIndex.from_documents(rdf_df_docs, service_context=service_context)
    df_index = VectorStoreIndex.from_documents(df_docs, service_context=service_context)


    # STORAGE
    # TODO


    # QUERY ENGINES
    sdd_json_engine = sdd_json_index.as_query_engine(output_cls=SddData, response_mode="compact")
    rdf_json_engine = rdf_json_index.as_query_engine(output_cls=RdfData, response_mode="compact")

    json_engine = json_index.as_query_engine(output_cls=DataRequest, response_mode="compact")

    sdd_df_engine = sdd_df_index.as_query_engine(output_cls=SddData, response_mode="compact")
    rdf_df_engine = rdf_df_index.as_query_engine(output_cls=RdfData, response_mode="compact")

    df_engine = df_index.as_query_engine(output_cls=DataRequest, response_mode="compact")


    pandas_query_engine = PandasQueryEngine(df=pd.concat(sdd_df_list), verbose=True)


    # PROMPT ENGINEERING
    full_query = '''

    You are presented with the following query:

    -----
    "I am looking for a dataset that contains information related to medication classification using the
    Anatomical Therapeutic Classification (ATC) system. I want to track ATC code updates"
    -----

    Given the context information, retrieve the following information:
    - dataset: the name of the dataset
    - columns: all the columns that are present in this dataset
    - label: the description of the dataset
    - publisher: the publisher of the dataset
    - pii: whether or not the dataset contains sensitive personal data, 
      this is True if at least one value of Column_sensitive_personal_data is Yes

    '''

    sdd_query = '''

    You are presented with the following query:

    -----
    "I am looking for a dataset that that identifies when a product has become available on the Belgian market."
    -----

    Given the context information, retrieve the following information:
    - df[file_name][0]


    '''
    q= " - pii: does the relevant dataframe contain a column named 'Column_sensitive_personal_data' with at least one value 'Yes'?"

    rdf_query = '''

    You are presented with the following query:

    -----
    "I am looking for a dataset that contains information related to medication classification using the
    Anatomical Therapeutic Classification (ATC) system. I want to track ATC code updates"
    -----

    Given the context information, retrieve the following information:
    - dataset: the name of the dataset
    - label: the description of the dataset
    - publisher: the publisher of the dataset

    '''


    # QUERYING / CHAINING RESPONSES

    # json_response = json_engine.query(sdd_query) # ok
    # df_response = df_engine.query(full_query) # great

    # sdd_json_response = sdd_json_engine.query(sdd_query) # very good, correct response to PII
    # rdf_json_response = rdf_json_engine.query(rdf_query) # bad

    # sdd_df_response = sdd_df_engine.query(sdd_query) # less bad
    # rdf_df_response = rdf_df_engine.query(rdf_query) # bad

    # print(f"json response: {json_response}")
    # print(f"df response: {df_response}")

    # print(f"sdd_json_response: {sdd_json_response}")
    # print(f"rdf_json_response: {rdf_json_response}")

    # print(f"sdd_df_response: {sdd_df_response}")
    # print(f"rdf_df_response: {rdf_df_response}")


    pandas_response = pandas_query_engine.query(sdd_query)


    # EVALUATION



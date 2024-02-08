from rdflib import Graph
from llama_index import Document
import os
import json
import csv
import re
import pandas as pd
from typing import List


def load_sdd(folder_path):
    sdd_df_list = df_reader(folder_path)
    documents = []

    get_columns = []
    for df in sdd_df_list:
        get_columns.append(list(zip(df["Column"], df["Label"], df["dataset"])))

    for columns in get_columns:
        sdd_text = []
        for tuple in columns:
            sdd_text.append(f"The column name is '{tuple[0]}', its description is '{tuple[1]}' and the corresponding dataset is {tuple[2]}.")

        documents.append(
            Document(
                text=' '.join(sdd_text)
            )
        )

    return documents



def transform_rdf_to_natural_language(g, filename):
    """
    helper function to parse ttl files and transform it to natural language.

    Parameters:
    - g (RDF Graph)
    - filename: the filename of the dataset

    Returns:
    - a list containing a natural language description of an rdf dataset.
    """

    text = []
    for s, p, o in g:

        predicate = re.split(r'#|/', str(p))[-1]
        object = 'unknown' if str(o) == "?" else str(o)

        rdf = f"The {predicate} of {str(s)} is {object}. The corresponding dataset is {filename}."

        text.append(rdf)

    return text


def load_rdf(folder_path):
    """
    Read parsed ttl files from a specified folder and return Document objects.

    Parameters:
    - folder_path (str): the folder path that contains all relevant turtle files

    Returns:
    list[Document]: Document objects
    """

    documents = []
    
    for filename in os.listdir(folder_path):
        g = Graph()
        file_path = os.path.join(folder_path, filename)
        g = g.parse(file_path, format="turtle")

        dataset = filename[:-8]
        text = transform_rdf_to_natural_language(g, dataset)

        documents.append(
            Document(
                doc_id=dataset,
                text=' '.join(text)
            )
        )
    return documents



def transform_csv_to_json(csv_input):
    
    csv_data = csv.DictReader(csv_input)
    sdd_data = [row for row in csv_data]

    return json.dumps(sdd_data)



def transform_rdf_to_json(g):
    """
    helper function to parse ttl files and store them in a structured json format.

    Parameters:
    - g (RDF Graph)

    Returns:
    - json string representation of rdf data
    - rdf metadata in a dict
    """

    rdf_data = []
    rdf_metadata = {}

    for s, p, o in g:
        text = {
            "subject": str(s),
            "predicate": str(p),
            "object": str(o)
        }
        rdf_data.append(text)

        if 'altLabel' in text["predicate"]:
            rdf_metadata["label"] = text["object"]

        if 'publisher' in text["predicate"]:
            rdf_metadata["publisher"] = text["object"]

        if 'description' in text["predicate"]:
            rdf_metadata["description"] = text["object"]
    
    return json.dumps(rdf_data, indent=4), rdf_metadata



def rdf_loader(folder_path) -> list[Document]:
    """
    Read parsed ttl files from a specified folder and return Document objects.

    Parameters:
    - folder_path (str): the folder path that contains all relevant turtle files

    Returns:
    list[Document]: Document objects
    """

    # Define output
    documents = []


    # Parse ttl files
    for filename in os.listdir(folder_path):
        g = Graph()
        file_path = os.path.join(folder_path, filename)
        g = g.parse(file_path, format="turtle")
        rdf_data, rdf_metadata = transform_rdf_to_json(g)

        # Create a list of documents from rdf data in each ttl file
        documents.append(
            Document(
                doc_id=filename,
                text=rdf_data,
                extra_info=rdf_metadata
            )
        )
    return documents



def sdd_loader(folder_path) -> list[Document]:
    documents = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as csv_input:
            sdd_data = transform_csv_to_json(csv_input)

                # Create a list of documents from sdd data
            documents.append(
                Document(
                    doc_id=filename,
                    text=sdd_data
                )
            )

    return documents 
    


def transform_sdd_to_df(file_path, file_name):
    with open(file_path, 'r') as csv:
        df = pd.read_csv(csv)
        df["dataset"] = file_name

    return df



def transform_turtle_to_df(file_path, file_name):
    g = Graph()
    g = g.parse(file_path, format="turtle")

    rdf_data = [{"subject": str(s), "predicate": str(p), "object": str(o)} for s, p, o in g]

    df = pd.DataFrame(rdf_data)
    df["file_name"] = file_name

    return df



def df_reader(folder_path):
    df_list = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        file_name = filename[:-8]

        if ".csv" in filename:
            df_list.append(transform_sdd_to_df(file_path, file_name))

        if ".ttl" in filename:
            df_list.append(transform_turtle_to_df(file_path, file_name))

    return df_list



def df_loader(df_list, concat_df: bool = False) -> List[Document]:

    text_list = []
    
    if concat_df:
        df = pd.concat(df_list)
        text_list = df.apply(
            lambda row: ", ".join(row.astype(str).tolist()), axis=1
        ).tolist()
        return [Document(text="\n".join(text_list))]
    
    else:
        for df in df_list:
            text_list.append(
                df.apply(
                    lambda row: ", ".join(row.astype(str)), axis=1).to_string(index=False))
        return [Document(text=text) for text in text_list]

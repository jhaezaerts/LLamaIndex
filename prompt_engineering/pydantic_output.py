from pydantic import BaseModel
from typing import List, Tuple


class RdfData(BaseModel):
    """
    Given the context information, retrieve the following details:

    - publisher: The publisher of the dataset.
    - label: The label describing the dataset.
    - description: The English language description of the dataset.
    - dataset: The name of the dataset.
    """
    publishers: List[str]
    labels: List[str]
    descriptions: List[str]
    datasets: List[str]



class SddData(BaseModel):
    """
    Given the context information, retrieve the following details:

    - columns: The column names of the dataset and their label.
    - pii: Column_sensitive_personal_data as indicator for pii.
    """
    columns: List[List[Tuple[str,str]]]
    pii: bool
    
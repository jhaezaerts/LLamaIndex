from llama_index import Document
from data_connectors.data_connectors import df_reader


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
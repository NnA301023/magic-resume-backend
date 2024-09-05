import os
import json
import typesense
import pandas as pd
from tqdm import tqdm
import typesense.exceptions
from dotenv import load_dotenv
from utils.search import search_similar_jobs

pd.set_option("display.max_columns", None)
load_dotenv()

TS_HOST = os.getenv("TYPESENSE_HOST", None)
TS_PORT = os.getenv("TYPESENSE_PORT", None)
TS_KEY  = os.getenv("TYPESENSE_API_KEY", None)
TS_COL  = os.getenv("TYPESENSE_COLLECTION", None)


# Running on Root Directory.
# $ python core/ingest.py
if __name__ == "__main__":

    filename_dw = "dataset/dw_job.csv"
    available = os.path.isfile(filename_dw)
    client = typesense.Client({
        "nodes": [{
            "host": TS_HOST,
            "port": TS_PORT,
            "protocol": "http"
        }],
        "api_key": TS_KEY,
        "connection_timeout": 5
    })

    if not available:

        column_rename = ["url", "company_name", "title", "location", "description", "budget"]
        used_columns = ["jobUrl", "companyName", "jobTitle", "locations", "description"]
        used_columns_upwork = ["link", "title", "country", "description"]

        dfs = []
        for file in os.listdir("dataset"):
            if "jobstreet" in file:
                dfs.append(pd.read_csv("dataset/" + file, usecols=used_columns))
        df_job_street = pd.concat(dfs).dropna().reset_index(drop=True)
        df_job_street = df_job_street[used_columns]
        df_job_street["budget"] = None
        df_job_street.columns = column_rename

        df_job_upwork = pd.read_csv("dataset/upwork-jobs.csv", usecols=used_columns_upwork + ["is_hourly", "hourly_high", "budget"] )
        df_job_upwork = df_job_upwork.dropna(subset=["is_hourly"]).reset_index()
        df_job_upwork["estimate_budget"] = df_job_upwork.apply(lambda i: i["hourly_high"] if pd.isnull(i["budget"]) else i["budget"], axis=1)
        df_job_upwork = df_job_upwork[used_columns_upwork + ["estimate_budget"]]
        df_job_upwork.insert(1, "companyName", "Freelance")
        df_job_upwork.columns = column_rename

        df_job = pd.concat([df_job_street, df_job_upwork]).dropna(subset=["title", "description"]).reset_index(drop=True)
        df_job["title"] = df_job["title"].str.capitalize()
        df_job.to_csv(filename_dw, index=False)

    else:

        df_job = pd.read_csv(filename_dw)
        df_job["budget"] = df_job["budget"].fillna(0).astype("float")

    # client.collections[TS_COL].delete()
    try:
        retrieved_docs = client.collections[TS_COL].retrieve()
        print("Collection is exists.")
        print(len(retrieved_docs))
    except (typesense.exceptions.ObjectNotFound, typesense.exceptions.ObjectAlreadyExists):
        print("Collection does not exist.")
        schema_col = {
            "name": TS_COL,
            "fields": [
                {'name': 'id', 'type': 'string'},
                {'name': 'company_name', 'type': 'string'},
                {'name': 'title', 'type': 'string'},
                {'name': 'location', 'type': 'string'},
                {'name': 'description', 'type': 'string'},
                {'name': 'budget', 'type': 'float', 'optional': True}
        ]}
        client.collections.create(schema_col)
        job_documents = df_job.to_dict(orient="records")
        for document in tqdm(job_documents, desc="Uploading documents into typesense..."):
            client.collections[TS_COL].documents.upsert(document)
        assert len(retrieved_docs) == len(df_job)

    result = search_similar_jobs(
        client=client.collections[TS_COL],
        title="Data Scientist", skill=["python", "sql"],
        location="Jakarta"
    )
    print(json.dumps(result, indent=4))
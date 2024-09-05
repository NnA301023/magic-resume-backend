import os
import ast
import typesense
from typing import List
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from googleapiclient.discovery import build
from core.utils.schema import ResponseSchema
from fastapi import FastAPI, File, UploadFile
from core.utils.search import search_similar_jobs
from fastapi.middleware.cors import CORSMiddleware

from core.utils.prompt import (
    prompt_extract, 
    prompt_skill_required
)

load_dotenv()

TS_HOST = os.getenv("TYPESENSE_HOST", None)
TS_PORT = os.getenv("TYPESENSE_PORT", None)
TS_KEY  = os.getenv("TYPESENSE_API_KEY", None)
TS_COL  = os.getenv("TYPESENSE_COLLECTION", None)

API_KEY = os.getenv("GROQ_API_KEY", None)
MODEL_NAME = os.getenv("MODEL_NAME", None)
YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY", None)

llm = Groq(model=MODEL_NAME, api_key=API_KEY)
youtube = build('youtube','v3', developerKey=YOUTUBE_KEY)

origins = ["*"]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=origins,
)

client = typesense.Client({
    "nodes": [{
        "host": TS_HOST,
        "port": TS_PORT,
        "protocol": "http"
    }],
    "api_key": TS_KEY,
    "connection_timeout": 5
})
client = client.collections[TS_COL]


def youtube_search(query: str, max_results: int = 1, identifier: str = 'youtube#video') -> List[str]:
    videos = None
    base_url = "https://www.youtube.com/watch?v="
    search_response = youtube.search().list(
        q=query, part='id,snippet', maxResults=max_results
    ).execute()
    for item in search_response['items']:
        if item['id']['kind'] == identifier:
            video_data = {
                'url': base_url + item["id"]["videoId"],
                'title': item['snippet']['title'],
                'channel_title': item['snippet']["channelTitle"],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['high']['url']
            }
            videos = video_data
    return videos
 
def extract_skill(text_resume: str) -> List[str]:
    
    # TODO: Leverage Json Schema Parsing to prevent Out-of-Format Error.
    response = llm.complete(prompt=prompt_extract.format(text=text_resume))
    response = response.text.split("\n")
    if len(response) == 4:
        skills = ast.literal_eval(response[0].replace("skill_extracted: ", "").strip())
        location = response[1].replace("location: ", "").strip().split(",")[0].strip()
        year_of_experience = response[2].replace("year_of_experience: ", "").strip()
        job_title_relevan = response[3].replace("job_title_relevan: ", "").strip()
        return skills, location, year_of_experience, job_title_relevan
    else:
        print(response)
        return "Failed to Parsing Entity from Resume..."
    
def suggest_skill(skills: List[str], year_of_exp: str, job_title: str) -> List[str]:

    # TODO: Leverage Json Schema Parsing to prevent Out-of-Format Error.
    prompt_input = prompt_skill_required.format(
        skills=skills,
        year_of_experience=year_of_exp,
        job_title_relevan=job_title
    )
    response = llm.complete(prompt=prompt_input)
    response = response.text
    response = ast.literal_eval(response)
    return response

@app.get("/")
async def root():
    response = ResponseSchema(message="Success")
    return response

@app.post("/get-recommendation")
async def get_recommendation(file: UploadFile = File(...)):

    # TODO: Budget Estimation
    # TODO: Cover Letter Generator

    file_path = os.path.join("core/temporary", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    skills, location, year_of_experience, job_title_relevan = extract_skill(text)
    job_suggestion = search_similar_jobs(
        client=client, 
        title=job_title_relevan, 
        skill=skills, location=location
    )
    skill_suggest = suggest_skill(skills, year_of_experience, job_title_relevan)
    course_suggests = {}
    for skill in skill_suggest:
        result = youtube_search(skill)
        course_suggests[skill] = result
    
    # TODO: Remove uploaded PDF.
    # os.remove(file_path)
    
    response = ResponseSchema(
        message="Success", 
        result=[
            {
                "personal_information": {
                    "skills": skills, 
                    "location": location, 
                    "year_of_experience": year_of_experience, 
                    "job_title_relevan": job_title_relevan
                }, 
                "job_suggestion": job_suggestion,
                "course_suggestion": course_suggests
            }
        ]
    )
    
    return response
import os
import ast
import uuid
import typesense
import instructor
from typing import List
import instructor.exceptions
from PyPDF2 import PdfReader
from groq import Groq as GroqClient
from llama_index.llms.groq import Groq
from googleapiclient.discovery import build
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException

from core.config import settings
from core.utils.parser import PersonalInfo
from core.utils.schema import ResponseSchema
from core.utils.search import search_similar_jobs
from core.utils.prompt import (
    prompt_skill_required, 
    prompt_cover_letter, 
    prompt_salary_estimation
)

# =============================================================
# NOTE: Temporary Database for Store Session and CV Required.
TEMP_DB = {}

# =============================================================


llm = Groq(model=settings.MODEL_NAME, api_key=settings.API_KEY)
llm_parser = instructor.from_groq(
    client=GroqClient(api_key=settings.API_KEY),
    mode=instructor.Mode.JSON
)
youtube = build('youtube','v3', developerKey=settings.YOUTUBE_KEY)

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
        "host": settings.TS_HOST,
        "port": settings.TS_PORT,
        "protocol": "http"
    }],
    "api_key": settings.TS_KEY,
    "connection_timeout": 5
})
client = client.collections[settings.TS_COL]


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
    while True:
        try:
            response: PersonalInfo = llm_parser.chat.completions.create(
                model=settings.MODEL_NAME, response_model=PersonalInfo,
                messages=[{"role": "user", "content": text_resume}]
            )
            break
        except instructor.exceptions.InstructorRetryException:
            continue
    response = response.__dict__
    return response

def salary_estimation(
    skills: List[str], 
    year_of_exp: str, job_title: str
    ) -> str:
    prompt_input = prompt_salary_estimation.format(
        skills=skills,
        year_of_experience=year_of_exp,
        job_title_relevan=job_title
    )
    response = llm.complete(prompt=prompt_input)
    response = response.text
    response = response.split(":")[-1].replace("\n", "").strip()
    return response
    
def suggest_skill(
    skills: List[str], 
    year_of_exp: str, job_title: str
    ) -> List[str]:
    prompt_input = prompt_skill_required.format(
        skills=skills,
        year_of_experience=year_of_exp,
        job_title_relevan=job_title
    )
    response = llm.complete(prompt=prompt_input)
    response = response.text
    response = response.replace("skill_suggest: ", "")
    try:
        response = ast.literal_eval(response)
    except Exception:
        response = response.split(", ")
    return response

@app.get("/")
async def root():
    response = ResponseSchema(message="Success")
    return response

@app.get("/set-session")
async def set_session():
    response = ResponseSchema(message="Suceess", result=[{"session": str(uuid.uuid4())}])
    return response

@app.post("/get-recommendation")
async def get_recommendation(session: str, file: UploadFile = File(...)):

    file_path = os.path.join("core/temporary", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    resp_skill = extract_skill(text)
    skills = resp_skill["skill_extracted"]
    location = resp_skill["location"]
    location = location.split(",")[0].strip()
    year_of_experience = resp_skill["year_of_experience"]
    job_title_relevan = resp_skill["job_title_relevan"]
    salary = salary_estimation(
        skills=skills, 
        year_of_exp=year_of_experience, 
        job_title=job_title_relevan
    )
    job_suggestion = search_similar_jobs(
        client=client, 
        title=job_title_relevan, 
        skill=skills, location=location
    )
    skill_suggest = suggest_skill(
        skills=skills, 
        year_of_exp=year_of_experience, 
        job_title=job_title_relevan
    )
    course_suggests = {}
    for skill in skill_suggest:
        result = youtube_search(skill)
        course_suggests[skill] = result
    
    # TODO: Remove uploaded PDF.
    # os.remove(file_path)

    TEMP_DB[session] = {"personal_cv": text}
    
    response = ResponseSchema(
        message="Success", 
        result=[
            {
                "personal_information": {
                    "skills": skills, 
                    "location": location, 
                    "year_of_experience": year_of_experience, 
                    "job_title_relevan": job_title_relevan,
                    "salary_estimation": salary,
                }, 
                "job_suggestion": job_suggestion,
                "course_suggestion": course_suggests
            }
        ]
    )
    
    return response

@app.post("/letter-generator")
async def letter_generator(session: str, company_name: str, job_title: str, job_desc: str):
    if session in TEMP_DB:
        personal_information = TEMP_DB.get(session).get("personal_cv")
    else:
        return HTTPException(status_code=404, detail="Session Not Found")

    response = llm.complete(
        prompt=prompt_cover_letter.format(
            text_resume=personal_information,
            company_name=company_name,
            job_title=job_title,
            job_description=job_desc
    ))
    response = response.text
    result = ResponseSchema(message="Success", result=[{"cover_letter": response}])
    return result
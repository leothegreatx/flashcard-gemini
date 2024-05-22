from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi.middleware.cors import CORSMiddleware
from servicess.generativeai import (YoutubeProcessor, GeminiProcessor)

class VideoAnalysisRequest(BaseModel):
    youtube_link: HttpUrl

app = FastAPI()

app.add_middleware(
    
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Video Analysis API!"}

genai_processor = GeminiProcessor(model_name ='gemini-pro', project ='dynamo-422010')

@app.post("/analyze_video")
def analyze_video(request: VideoAnalysisRequest):
    
    # Doing the analysis
    processor = YoutubeProcessor(genai_processor = genai_processor)
    result = processor.retrieve_youtube_documents(str(request.youtube_link), verbose =True)
    
    #summary = genai_processor.generate_document_summary(result, verbose =True)
    #return {"summary": summary}
    
    # find key concepts
    key_concepts = processor.find_key_concepts(result, group_size=15,verbose=True)
    
    return {"key_concepts": key_concepts}
    
    gemini_processor = GeminiProcessor(model_name ='gemini-pro', project ='dynamo-422010')

    count_tokens = gemini_processor.count_tokens(result)
    
    return {"count_tokens": count_tokens}

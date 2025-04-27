from dotenv import load_dotenv
import os
from typing import List, Tuple
from google import genai
from google.genai import types
import base64
import os
from pathlib import Path
import tempfile
from config import GEMINI_MODEL, GEMINI_LIGHT_MODEL, SYSTEM_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def combine_transcripts(transcripts: List[str]) -> str:
    response = client.models.generate_content(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            contents=[f"""
            These are 5 consecutive transcripts for the last 5 minutes of the ongoing student lecture split by the semi-colon: {";".join(transcripts)}. There might be less than 5 if it's the beginning of the lecture. Combine these transcripts into a single coherent transcript.
            """]
    )
    return response.text

async def process_image(img) -> str:
    return "Not implemented"

async def process_audio(audio) -> str:
    try:
        # For debugging - print the first few bytes
        if audio is None:
            return ""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            audio_path = temp_file.name
            myfile = client.files.upload(file=audio_path)
            print(f"Audio saved at: {audio_path}")
            
            # Seek back to start of file for later processing
            await audio.seek(0)
                
        response = client.models.generate_content(
            model=GEMINI_LIGHT_MODEL, contents=["Translate the audio to the english language. Do not use any other language", myfile]
        )

        return response.text
        
    except Exception as e:
        print(f"Error in process_audio: {str(e)}")
        return f"Error transcribing audio: {str(e)}"
    
async def generate_summary(transcript: str, previous_summary: str = "") -> str:
    try:
        context = f"Previous summary: {previous_summary}\n\n" if previous_summary else ""
        prompt = f"""
        {context}Please provide a concise summary of the following university lecture transcript, integrating it with any previous summary if provided:
        {transcript}
        Focus on the main concepts and key takeaways. Keep the summary coherent and flowing naturally.
        
        Don't try to use markdown. Lenses don't support it.
        
        Don't try to keep it too short - keep it as long as needed.
        
        Try to keep the summary well structured - try to use new lines and bullet points. 
        
        Avoid using the word "summary" in the response. Don't start the response with "Summary, Here is the summary...".
        """
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        print(f"Error in generate_summary: {str(e)}")
        return previous_summary  # Return previous summary if error occurs

async def generate_questions(
    transcript: str,
    current_questions: List[str] = None,
    num_questions: int = 3  
) -> List[Tuple[str, str]]:
    # Prepare content for the model
    content = []
    
    # Add transcript
    prompt = f"""
    Based on the following lecture content, generate 3-5 relevant questions
    that could help clarify or deepen understanding of the material, along with suggested answers.
    
    Example questions and directions:
    
    {"Here are the existing questions from oldest to newest to consider and build upon:" if current_questions else ""}
    {chr(10).join(f"- {q}" for q in current_questions) if current_questions else "No questions yes"}
    
    Lecture content of the last 5 minutes:
    {transcript}
    
    Make sure that each question is targeted to a different concept inside the lecture. Avoid questions that are too similar or overlap. Suggest only the questions THAT ARE NOT ALREADY ANSWERED in the existing questions or in the lecture.
    
    
    TASK: Return 2-3 questions if the are no questions. If there are already al least 3 than feel free to discard the oldest 2. Never return more than 5 questions. Keep each question and answer short and concise.
    """
    
    content.append(prompt)
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction=SYSTEM_PROMPT,
        response_schema=types.Schema(
            type = types.Type.OBJECT,
            properties = {
                "qa-pair": types.Schema(
                    type = types.Type.ARRAY,
                    items = types.Schema(
                        type = types.Type.OBJECT,
                        properties = {
                            "question": types.Schema(
                                type = types.Type.STRING,
                            ),
                            "answer": types.Schema(
                                type = types.Type.STRING,
                            ),
                        },
                        required = ["question", "answer"]
                    ),
                ),
            },
        ),
    )
    
    response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=generate_content_config
    )
    
    # Extract qa-pairs from the response
    return response.text
from dotenv import load_dotenv
import os
from typing import List, Tuple
from google import genai
from google.genai import types
import base64
import os
from pathlib import Path
import tempfile

load_dotenv()

client = genai.Client(api_key="AIzaSyDUOee4gefkOjFBawcuKNhq8SEEVljOtAQ")
# Configure Gemini API
#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def process_audio(audio) -> str:
    try:
        # For debugging - print the first few bytes
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            audio_path = temp_file.name
            myfile = client.files.upload(file=audio_path)
            print(f"Audio saved at: {audio_path}")
            
            # Seek back to start of file for later processing
            await audio.seek(0)
                
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=["Do the exact transcription of the audio in the english languange only", myfile]
        )

        print(response.text)
        
    except Exception as e:
        print(f"Error in process_audio: {str(e)}")
        return f"Error transcribing audio: {str(e)}"

    # async def generate_summary(transcript: str) -> str:
    # prompt = f"""
    # Please provide a concise summary of the following lecture transcript:
    # {transcript}
    # Focus on the main concepts and key takeaways.
    # """
    # response = await model.generate_content_async(prompt)
    # return response.text

# async def generate_questions(
#     transcript: str,
#     current_questions: List[str] = None,
#     images: List[str] = None,
#     num_questions: int = 3  
# ) -> List[Tuple[str, str]]:
#     # Prepare content for the model
#     content = []
    
#     # Add transcript
#     prompt = f"""
#     Based on the following lecture content, generate {num_questions} relevant questions
#     that could help clarify or deepen understanding of the material, along with suggested answers.
    
#     Example questions and directions:
    
#     {"Here are the existing questions to consider and build upon:" if current_questions else ""}
#     {chr(10).join(f"- {q}" for q in current_questions) if current_questions else ""}
    
#     Lecture content:
#     {transcript}
    
#     Format: Return exactly {num_questions} questions and their answers.
#     Each question-answer pair should be separated by two newlines.
#     """
    
#     content.append(prompt)
    
#     # Add images if provided
#     if images:
#         for image_path in images:
#             try:
#                 image = genai.types.Image.from_file(image_path)
#                 content.append(image)
#             except Exception as e:
#                 print(f"Error loading image {image_path}: {e}")
    
#     # Generate response
#     response = await model.generate_content_async(content)
    
#     # Parse response
#     questions_and_answers = []
#     qa_pairs = response.text.split("\n\n")
#     for qa in qa_pairs[:num_questions]:
#         if "?" in qa:
#             question = qa.split("?")[0] + "?"
#             answer = qa.split("?")[1].strip()
#             questions_and_answers.append((question, answer))
    
#     return questions_and_answers 
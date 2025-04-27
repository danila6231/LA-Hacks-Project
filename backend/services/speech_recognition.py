import json
import os
import wave
import numpy as np
from vosk import Model, KaldiRecognizer
from typing import Optional
import logging
import audioop

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simplified format
)
logger = logging.getLogger(__name__)

class SpeechRecognizer:
    def __init__(self, model_path: str = "models/vosk-model-small-en-us-0.15"):
        """
        Initialize the speech recognizer with a Vosk model.
        
        Args:
            model_path: Path to the Vosk model directory
        """
        logger.debug(f"Initializing SpeechRecognizer with model path: {model_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        try:
            self.model = Model(model_path)
            # Initialize recognizer with optimized parameters
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.recognizer.SetWords(True)
            # Set more aggressive decoding parameters
            self.recognizer.SetMaxAlternatives(0)
            logger.info(f"Speech recognizer initialized with model: {model_path}")
        except Exception as e:
            logger.error(f"Error initializing SpeechRecognizer: {e}")
            raise
        
    def process_audio_chunk(self, audio_data: bytes) -> Optional[str]:
        """
        Process a chunk of audio data and return the recognized text.
        
        Args:
            audio_data: Raw audio data in bytes
            
        Returns:
            Recognized text if available, None otherwise
        """
        try:
            # Convert audio data to numpy array for validation
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Validate audio data
            if len(audio_array) == 0:
                return None
                
            # Process the audio chunk
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                if "text" in result and result["text"]:
                    print(f"Complete result: {result['text']}")  # Debug print
                    return result["text"]
            else:
                # Get partial result
                partial = json.loads(self.recognizer.PartialResult())
                if "partial" in partial and partial["partial"]:
                    # COMMENTING OUT FOR NOW
                    # print(f"Partial result: {partial['partial']}")  # Debug print
                    pass
            
            return None
            
        except Exception as e:
            print(f"Error processing audio: {str(e)}")  # Debug print
            return None
    
    def get_partial_result(self) -> Optional[str]:
        """
        Get the current partial recognition result.
        
        Returns:
            Partial recognition text if available, None otherwise
        """
        try:
            logger.debug("Getting partial result")
            result = json.loads(self.recognizer.PartialResult())
            logger.debug(f"Raw partial result: {result}")
            partial = result.get("partial", "")
            if partial:
                logger.debug(f"Partial transcription: {partial}")
            else:
                logger.debug("No partial text in result")
            return partial
        except Exception as e:
            logger.error(f"Error getting partial result: {e}")
            return None 
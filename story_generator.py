import os
import tempfile
from google import genai
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from typing import Optional, Dict, List


class StoryGenerator:
    """Handles story generation from words and emotional text-to-speech"""
    
    def __init__(self, gemini_api_key: str, elevenlabs_api_key: str):
        """Initialize story generator with Gemini and ElevenLabs APIs"""
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
        self.last_error: Optional[str] = None
        
        self.voice_mapping = {
            'english': {
                'emotional': 'EXAVITQu4vr4xnSDxMaL',
                'narrative': '21m00Tcm4TlvDq8ikWAM'
            },
            'hindi': {
                'emotional': 'pNInz6obpgDQGcFmaJgB',
                'narrative': 'EXAVITQu4vr4xnSDxMaL'
            }
        }
    
    def generate_story(self, words: List[str], theme: str, word_count: int, language: str) -> Optional[str]:
        """
        Generate a story from input words with specified theme, word count, and language
        """
        try:
            self.last_error = None
            words_str = ', '.join(words)
            
            language_instruction = ""
            if language.lower() == 'hindi':
                language_instruction = "Write the story in Hindi language."
            else:
                language_instruction = "Write the story in English language."
            
            prompt = f"""
            Create an engaging and emotional story based on the following:
            
            Words to include: {words_str}
            Theme: {theme}
            Target word count: {word_count} words
            Language: {language}
            
            Instructions:
            - {language_instruction}
            - Create a narrative that naturally incorporates all the given words
            - Follow the theme: {theme}
            - Make the story emotionally engaging with vivid descriptions
            - Include dialogue if appropriate
            - Aim for approximately {word_count} words
            - Make it suitable for audio narration with natural pacing
            
            Write the complete story below:
            """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                self.last_error = "Gemini returned an empty response while generating the story."
                return None
                
        except Exception as e:
            self.last_error = f"Story generation error: {e}"
            print(self.last_error)
            return None
    
    def generate_emotional_audio(self, story_text: str, language: str) -> Optional[str]:
        """
        Convert story text to emotional speech using ElevenLabs
        Uses voices with better emotional expression
        """
        try:
            lang_key = 'hindi' if language.lower() == 'hindi' else 'english'
            voice_id = self.voice_mapping[lang_key]['emotional']

            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                text=story_text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.6,
                    use_speaker_boost=True
                )
            )
            
            audio_bytes = b''.join(audio_generator)
            
            audio_path = tempfile.mktemp(suffix='.mp3')
            with open(audio_path, 'wb') as f:
                f.write(audio_bytes)
            
            return audio_path
            
        except Exception as e:
            self.last_error = f"Audio generation error: {e}"
            print(self.last_error)
            return None
    
    def create_story_with_audio(self, words: List[str], theme: str, word_count: int, language: str) -> Optional[Dict]:
        """
        Complete pipeline: generate story and create emotional audio
        Returns: {'story': text, 'audio_path': path, 'audio_bytes': bytes}
        """
        try:
            story = self.generate_story(words, theme, word_count, language)
            if not story:
                return None
            
            audio_path = self.generate_emotional_audio(story, language)
            if not audio_path:
                return {'story': story, 'audio_path': None, 'audio_bytes': None}
            
            with open(audio_path, 'rb') as f:
                audio_bytes = f.read()
            
            return {
                'story': story,
                'audio_path': audio_path,
                'audio_bytes': audio_bytes
            }
            
        except Exception as e:
            self.last_error = f"Error creating story with audio: {e}"
            print(self.last_error)
            return None

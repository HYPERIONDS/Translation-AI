import os
import tempfile
import subprocess
from typing import Optional, Dict, Callable
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from google import genai

class ArticleToPodcast:
    """Handles conversion of articles to multi-speaker podcast audio"""
    
    def __init__(self, gemini_api_key: str, elevenlabs_api_key: str):
        """Initialize article to podcast service with Gemini and ElevenLabs APIs"""
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
        self.last_error: str = ""
        
        # Voice mapping for different speakers
        self.host_voice_id = "pNInz6obpgDQGcFmaJgB"    # Adam - Host voice
        self.expert_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - Expert voice
    
    def generate_podcast_script(self, article_text: str, word_count: int = 300) -> Optional[str]:
        """
        Generate a podcast script from article text using Gemini
        Returns: Formatted script with Host: and Expert: labels
        """
        try:
            prompt = f"""
Summarize the following article into a detailed podcast script (~{word_count} words) as a conversation:
- Include a "Host" and an "Expert".
- Each line should start with "Host:" or "Expert:".
- Make it engaging, explanatory, and conversational.
- The Host should introduce the topic and ask questions.
- The Expert should provide insights and explanations.
- Make it sound natural and informative.

Article:
---
{article_text}
---

Generate the podcast script:
"""
            
            response = self.gemini_client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                # Fallback script
                return self._generate_fallback_script(article_text)
                
        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating podcast script: {e}")
            return self._generate_fallback_script(article_text)
    
    def _generate_fallback_script(self, article_text: str) -> str:
        """Generate a simple fallback script if AI generation fails"""
        words = article_text.split()[:100]
        summary = ' '.join(words)
        
        return f"""Host: Welcome to our podcast. Today, we're discussing an important article.
Expert: {summary}
Host: That's very interesting. Can you tell us more about this?
Expert: Certainly. This article highlights several key points that deserve attention.
Host: Thank you for sharing these insights with us today.
Expert: My pleasure. It's important to stay informed about these developments."""
    
    def generate_speaker_audio(self, text: str, voice_id: str, output_file: str) -> bool:
        """
        Generate audio for a single speaker line using ElevenLabs
        Returns: True if successful, False otherwise
        """
        try:
            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75
                )
            )
            
            with open(output_file, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating audio: {e}")
            return False
    
    def merge_audio_files(self, audio_files: list, output_file: str) -> bool:
        """
        Merge multiple audio files into a single file using FFmpeg
        Returns: True if successful, False otherwise
        """
        try:
            # Create a temporary file list for FFmpeg
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
                file_list_path = f.name
            
            # Use FFmpeg to concatenate audio files
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", file_list_path, "-c", "copy", output_file
            ], check=True, capture_output=True)
            
            # Clean up the file list
            os.unlink(file_list_path)
            return True
            
        except Exception as e:
            self.last_error = str(e)
            print(f"Error merging audio files: {e}")
            return False
    
    def create_podcast_from_article(self, article_text: str, script_word_count: int = 300, 
                                   progress_callback: Optional[Callable] = None) -> Optional[bytes]:
        """
        Complete workflow to convert article to podcast audio
        Returns: Audio bytes if successful, None otherwise
        """
        try:
            # Step 1: Generate script
            if progress_callback:
                progress_callback("Generating podcast script...", 20)
            
            script = self.generate_podcast_script(article_text, script_word_count)
            if not script:
                self.last_error = "Podcast script generation returned empty output."
                return None
            
            # Step 2: Parse script and generate audio for each line
            if progress_callback:
                progress_callback("Generating audio for speakers...", 40)

            def _parse_script_to_segments(script_text: str):
                """Parse Gemini script output into (speaker, text) segments."""
                import re

                # Match lines like:
                # - Host: ...
                # - Expert - ...
                # - **Host:** ...
                # - Speaker 1: ...
                # Accept lines like:
                # - Host: ...
                # - Expert - ...
                # - **Host:** ...
                # - **Expert**: ...
                # - Speaker 1: ...
                line_pattern = re.compile(
                    r"^\s*\*{0,2}\s*(Host|Expert|Speaker\s*\d+|Speaker)\s*[:\-–—]\s*\*{0,2}\s*(.*)$",
                    re.IGNORECASE
                )

                segments = []
                last_role = 'host'

                for raw_line in script_text.splitlines():
                    line = raw_line.strip()
                    if not line:
                        continue

                    m = line_pattern.match(line)
                    if m:
                        role = m.group(1).strip().lower()
                        text = m.group(2).strip()

                        if 'expert' in role:
                            last_role = 'expert'
                        else:
                            last_role = 'host'

                        segments.append((last_role, text))
                    else:
                        # Treat as continuation of prior segment
                        if segments:
                            prev_role, prev_text = segments[-1]
                            segments[-1] = (prev_role, prev_text + ' ' + line)
                        else:
                            segments.append((last_role, line))

                return segments

            segments = _parse_script_to_segments(script)
            audio_files = []
            temp_files = []

            for i, (speaker, text) in enumerate(segments):
                if not text.strip():
                    continue

                voice_id = self.host_voice_id if speaker == 'host' else self.expert_voice_id

                # Generate audio file
                temp_audio = tempfile.mktemp(suffix=f'_speaker_{i}.mp3')
                temp_files.append(temp_audio)

                if self.generate_speaker_audio(text, voice_id, temp_audio):
                    audio_files.append(temp_audio)

                # Update progress
                if progress_callback:
                    progress = 40 + int((i / len(segments)) * 40)
                    progress_callback(f"Processing speaker {i+1}/{len(segments)}...", progress)

            if not audio_files:
                self.last_error = (
                    "No audio files were generated. "
                    "This usually happens when the generated script doesn't include identifiable speaker lines (e.g. 'Host:'/'Expert:').\n"
                    f"Generated script output:\n{script}\n"
                )
                return None
            
            # Step 3: Merge audio files
            if progress_callback:
                progress_callback("Merging audio segments...", 85)
            
            final_output = tempfile.mktemp(suffix='_podcast.mp3')
            temp_files.append(final_output)
            
            if not self.merge_audio_files(audio_files, final_output):
                self.last_error = self.last_error or "Failed to merge audio segments into final podcast file."
                return None
            
            # Step 4: Read the final audio file
            if progress_callback:
                progress_callback("Finalizing podcast...", 95)
            
            with open(final_output, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
            
            if progress_callback:
                progress_callback("Complete!", 100)
            
            return audio_bytes
            
        except Exception as e:
            self.last_error = str(e)
            print(f"Error creating podcast: {e}")
            return None

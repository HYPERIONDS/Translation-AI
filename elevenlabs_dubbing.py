import os
import time
import tempfile
from elevenlabs.client import ElevenLabs
from typing import Optional, Dict
import json
import urllib.request

class ElevenLabsDubbing:
    """Handles video dubbing using ElevenLabs Dubbing API"""
    
    def __init__(self, api_key: str):
        """Initialize ElevenLabs dubbing service"""
        self.api_key = api_key
        self.client = ElevenLabs(api_key=api_key)
        self.last_error: Optional[str] = None
        
        # Language code mapping
        self.language_codes = {
            'en': 'en',
            'hi': 'hi',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'it': 'it',
            'pt': 'pt',
            'ja': 'ja',
            'ko': 'ko',
            'zh': 'zh'
        }
    
    def create_dubbing_project(self, video_path: str, source_lang: str, 
                              target_lang: str, project_name: str = "Dubbing Project") -> Optional[str]:
        """
        Upload video and create dubbing project on ElevenLabs
        Returns: dubbing_id if successful
        """
        try:
            self.last_error = None
            source_code = self.language_codes.get(source_lang, 'en')
            target_code = self.language_codes.get(target_lang, 'hi')
            
            # Upload video to ElevenLabs for dubbing
            with open(video_path, 'rb') as video_file:
                # SDK method name (v1.0.0): dub_a_video_or_an_audio_file
                response = self.client.dubbing.dub_a_video_or_an_audio_file(
                    target_lang=target_code,
                    file=video_file,
                    mode="automatic",
                    source_lang=source_code,
                    num_speakers=1,
                    name=project_name,
                    watermark=True,
                )
            
            dubbing_id = response.dubbing_id
            print(f"Created dubbing project: {dubbing_id}")
            return dubbing_id
            
        except Exception as e:
            self.last_error = str(e)
            print(f"Error creating dubbing project: {self.last_error}")
            return None
    
    def get_dubbing_status(self, dubbing_id: str) -> Dict:
        """
        Check the status of a dubbing project
        Returns: {'status': 'dubbing'|'dubbed'|'failed', 'metadata': ...}
        """
        try:
            metadata = self.client.dubbing.get_dubbing_project_metadata(dubbing_id=dubbing_id)
            raw_status = metadata.get('status') if isinstance(metadata, dict) else getattr(metadata, 'status', None)
            status = self._normalize_status(raw_status)

            return {
                'status': status,
                'raw_status': raw_status,
                'metadata': metadata,
                'name': metadata.get('name') if isinstance(metadata, dict) else getattr(metadata, 'name', None),
            }
            
        except Exception as e:
            print(f"Error getting dubbing status: {e}")
            return {'status': 'error', 'raw_status': None, 'metadata': None, 'error': str(e)}

    def _normalize_status(self, raw_status: Optional[str]) -> str:
        """
        Normalize ElevenLabs statuses to what the frontend expects.
        Frontend logic assumes: dubbing | dubbed | failed | error
        """
        if not raw_status:
            return "dubbing"

        s = str(raw_status).strip().lower()

        if s in {"dubbed", "completed", "complete", "done", "success", "succeeded"}:
            return "dubbed"
        if s in {"failed", "failure", "error"}:
            return "failed"

        # Treat all other/unknown values as "still processing" to avoid UI getting stuck.
        return "dubbing"
    
    def wait_for_dubbing_completion(self, dubbing_id: str, 
                                   callback=None, max_wait_seconds: int = 600) -> bool:
        """
        Wait for dubbing to complete with optional progress callback
        callback: function(status, elapsed_time) called periodically
        Returns: True if successful, False otherwise
        """
        try:
            start_time = time.time()
            
            while True:
                elapsed = time.time() - start_time
                
                # Check timeout
                if elapsed > max_wait_seconds:
                    print(f"Dubbing timed out after {max_wait_seconds} seconds")
                    return False
                
                # Get status
                status_result = self.get_dubbing_status(dubbing_id)
                status = status_result.get("status")
                raw_status = status_result.get("raw_status")
                
                # Call progress callback
                if callback:
                    callback(raw_status or status, int(elapsed))
                
                # Check completion
                if status == "dubbed":
                    print("Dubbing completed successfully!")
                    return True
                elif status == "dubbing":
                    print(f"Still processing... ({int(elapsed)}s elapsed)")
                    time.sleep(5)  # Poll every 5 seconds
                else:
                    print(f"Dubbing failed with status: {raw_status or status}")
                    return False
                    
        except Exception as e:
            print(f"Error waiting for dubbing: {e}")
            return False
    
    def download_dubbed_video(self, dubbing_id: str, target_lang: str) -> Optional[str]:
        """
        Download the dubbed video from ElevenLabs
        Returns: Path to downloaded video file
        """
        try:
            target_code = self.language_codes.get(target_lang, 'hi')

            # Save to temporary file
            output_path = tempfile.mktemp(suffix='.mp4')

            # Prefer direct REST download to avoid SDK decoding issues.
            # Docs: GET /v1/dubbing/{dubbing_id}/audio/{language_code}
            url = f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}/audio/{target_code}"
            req = urllib.request.Request(url, headers={"xi-api-key": self.api_key})

            try:
                with urllib.request.urlopen(req) as resp, open(output_path, "wb") as f:
                    f.write(resp.read())
                print(f"Downloaded dubbed video to: {output_path}")
                return output_path
            except Exception as rest_err:
                # Fall back to SDK if REST fails for any reason.
                print(f"REST download failed, falling back to SDK: {rest_err}")

            dubbed = self.client.dubbing.get_dubbed_file(
                dubbing_id=dubbing_id,
                language_code=target_code
            )

            with open(output_path, 'wb') as f:
                if isinstance(dubbed, (bytes, bytearray)):
                    f.write(dubbed)
                elif hasattr(dubbed, "content"):
                    # httpx.Response-like
                    f.write(getattr(dubbed, "content"))
                elif hasattr(dubbed, "read"):
                    # file-like
                    f.write(dubbed.read())
                elif isinstance(dubbed, str):
                    s = dubbed.strip()
                    if s.startswith("http://") or s.startswith("https://"):
                        with urllib.request.urlopen(s) as resp:
                            f.write(resp.read())
                    elif s.startswith("{") and s.endswith("}"):
                        data = json.loads(s)
                        dl_url = data.get("url") or data.get("download_url")
                        if not dl_url:
                            raise ValueError("Dubbed file JSON missing url/download_url")
                        with urllib.request.urlopen(dl_url) as resp:
                            f.write(resp.read())
                    else:
                        import base64
                        try:
                            f.write(base64.b64decode(dubbed))
                        except Exception:
                            f.write(dubbed.encode("utf-8"))
                elif isinstance(dubbed, dict) and "audio" in dubbed:
                    import base64
                    f.write(base64.b64decode(dubbed["audio"]))
                elif isinstance(dubbed, dict) and ("url" in dubbed or "download_url" in dubbed):
                    dl_url = dubbed.get("url") or dubbed.get("download_url")
                    with urllib.request.urlopen(dl_url) as resp:
                        f.write(resp.read())
                else:
                    raise ValueError(f"Unexpected dubbed file response type: {type(dubbed)}")

            print(f"Downloaded dubbed video to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error downloading dubbed video: {e}")
            return None
    
    def dub_video_complete(self, video_path: str, source_lang: str, 
                          target_lang: str, progress_callback=None) -> Optional[str]:
        """
        Complete dubbing workflow: upload, wait, download
        Returns: Path to dubbed video or None if failed
        """
        try:
            # Step 1: Create dubbing project
            if progress_callback:
                progress_callback("Uploading video to ElevenLabs...", 10)
            
            dubbing_id = self.create_dubbing_project(
                video_path, 
                source_lang, 
                target_lang,
                project_name=f"Dub {source_lang} to {target_lang}"
            )
            
            if not dubbing_id:
                return None
            
            # Step 2: Wait for completion
            if progress_callback:
                progress_callback("Processing on ElevenLabs servers...", 30)
            
            def status_callback(status, elapsed):
                if progress_callback:
                    progress = min(30 + (elapsed // 2), 80)  # Progress from 30% to 80%
                    progress_callback(f"Dubbing in progress... ({elapsed}s)", progress)
            
            success = self.wait_for_dubbing_completion(
                dubbing_id,
                callback=status_callback,
                max_wait_seconds=600
            )
            
            if not success:
                return None
            
            # Step 3: Download result
            if progress_callback:
                progress_callback("Downloading dubbed video...", 90)
            
            dubbed_video_path = self.download_dubbed_video(dubbing_id, target_lang)
            
            if progress_callback:
                progress_callback("Complete!", 100)
            
            return dubbed_video_path
            
        except Exception as e:
            print(f"Error in complete dubbing workflow: {e}")
            return None
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }

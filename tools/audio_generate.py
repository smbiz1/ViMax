import os
import json
from typing import List, Dict, Optional
from IPython.display import Audio

# OpenAI SDK import
import openai

# Optional Google Cloud imports
try:
    from google.api_core.client_options import ClientOptions
    from google.cloud import texttospeech_v1beta1 as texttospeech
    from vertexai.generative_models import GenerationConfig, GenerativeModel, Part
    import vertexai

    GOOGLE_AND_VERTEX_AVAILABLE = True
except ImportError:
    GOOGLE_AND_VERTEX_AVAILABLE = False


class PodcastGenerator:
    def __init__(
        self,
        # OpenAI fields
        openai_api_key: str = None,
        openai_model_name: str = "gpt-4-1106-preview",
        # Google/Vertex fields
        project_id: str = None,
        tts_location: str = "us",
        vertexai_location: str = "us-central1",
        vertex_model_name: str = "gemini-1.5-pro",
        # TTS settings
        language_code: str = "en-US",
        openai_voice_name: str = "echo",
        google_voice_name: str = "en-US-Studio-MultiSpeaker",
        # General
        llm_backend: str = "openai",  # "openai" or "vertexai"
        tts_backend: str = "openai",  # "openai" or "google"
    ):
        # Backend selectors
        self.llm_backend = llm_backend
        self.tts_backend = tts_backend

        # OPENAI SETUP
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_model_name = openai_model_name
        self.openai_voice_name = openai_voice_name
        if self.llm_backend == "openai" or self.tts_backend == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "OpenAI API key must be provided via argument or OPENAI_API_KEY env var."
                )
            openai.api_key = self.openai_api_key

        # GOOGLE/VertexAI SETUP
        self.project_id = project_id or os.getenv("PROJECT_ID")
        self.tts_location = tts_location
        self.vertexai_location = vertexai_location
        self.vertex_model_name = vertex_model_name
        self.google_voice_name = google_voice_name
        self.language_code = language_code

        # For later initialization
        self.vertex_model = None
        self.vertex_response_schema = None
        self.tts_client = None

        # Set up Google/Vertex specifics if requested and available
        if self.llm_backend == "vertexai" or self.tts_backend == "google":
            if not GOOGLE_AND_VERTEX_AVAILABLE:
                raise ImportError("Google Vertex AI and TTS SDK not installed.")
        if self.llm_backend == "vertexai":
            # Vertex AI Init
            vertexai.init(project=self.project_id, location=self.vertexai_location)
            # set up response schema for controlled JSON generation
            self.vertex_response_schema = {
                "type": "object",
                "properties": {
                    "dialogue": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "speaker": {"type": "string"},
                                "line": {"type": "string"},
                            },
                            "required": ["speaker", "line"],
                        },
                    }
                },
                "required": ["dialogue"],
            }
            self.vertex_model = GenerativeModel(
                self.vertex_model_name,
                system_instruction=(
                    "You are a podcast writer. Your task is to generate a short podcast-style dialogue between two speakers, Speaker R and Speaker S"
                ),
                generation_config=GenerationConfig(
                    temperature=1,
                    top_p=0.95,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                    response_schema=self.vertex_response_schema,
                ),
            )
        if self.tts_backend == "google":
            self.tts_client = texttospeech.TextToSpeechClient(
                client_options=ClientOptions(
                    api_endpoint=f"{tts_location}-texttospeech.googleapis.com"
                )
            )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts plain text from PDF file (local file path)."""
        try:
            import PyPDF2

            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    def generate_podcast_script(self, content_path: str) -> List[Dict[str, str]]:
        """
        Generates a podcast script using either OpenAI or VertexAI with controlled JSON output.
        `content_path`: local file path to a PDF.
        """
        source_text = self.extract_text_from_pdf(content_path)
        if not source_text:
            print("No source text extracted from PDF.")
            return []

        # Compose prompt
        prompt = (
            "You are a podcast writer. Your task is to generate a short podcast-style dialogue between two speakers, Speaker R and Speaker S.\n"
            "The dialogue should be engaging and natural, with each speaker contributing roughly equal amounts. "
            "Return the dialogue as a JSON array of objects, where each object has a 'speaker' (either 'R' or 'S') and a 'line' property.\n"
            "Use the following information to create the content for the podcast dialogue:\n\n"
            f"{source_text[:6000]}"
        )

        # --- OpenAI approach ---
        if self.llm_backend == "openai":
            try:
                response = openai.chat.completions.create(
                    model=self.openai_model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You output ONLY valid JSON, structured as per instructions.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=1500,
                    temperature=1,
                    response_format={"type": "json_object"},
                )
                raw_content = response.choices[0].message.content
                generated_json = json.loads(raw_content)
                return generated_json["dialogue"]
            except Exception as e:
                print(
                    f"Error generating or parsing JSON script: {e}. Returning empty list."
                )
                print(
                    f"OpenAI LLM content: {locals().get('raw_content', '<no content>')}"
                )
                return []
        # --- VertexAI approach ---
        if self.llm_backend == "vertexai":
            try:
                response = self.vertex_model.generate_content([prompt])
                generated_json = json.loads(response.text)
                return generated_json["dialogue"]
            except Exception as e:
                print(
                    f"Error generating or parsing VertexAI JSON script: {e}. Returning empty list."
                )
                return []
        print("No supported LLM backend configured.")
        return []

    def synthesize_podcast_openai(
        self, dialogue: List[Dict[str, str]], output_file: str
    ) -> None:
        """
        Synthesizes speech using OpenAI TTS, concatenating audio for each speaker's line.
        """
        audio_data = b""
        for turn in dialogue:
            # Assign `echo` or another OpenAI voice; in advanced scenarios, map per-speaker voices here.
            voice = self.openai_voice_name
            try:
                tts_response = openai.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=turn["line"],
                    response_format="mp3",
                )
                chunk = (
                    tts_response
                    if isinstance(tts_response, bytes)
                    else tts_response.read()
                )
                audio_data += chunk
            except Exception as e:
                print(f"Error with OpenAI TTS on line: {turn['line']}\n{e}")
        with open(output_file, "wb") as out:
            out.write(audio_data)
        print(f'Audio content written to file "{output_file}" using OpenAI TTS.')

    def synthesize_podcast_google(
        self, dialogue: List[Dict[str, str]], output_file: str
    ) -> None:
        """
        Synthesizes speech for a podcast using Google TTS MultiSpeakerMarkup.
        """
        if not self.tts_client:
            print("Google TTS client is not initialized.")
            return

        multi_speaker_markup = texttospeech.MultiSpeakerMarkup()
        for turn_data in dialogue:
            multi_speaker_markup.turns.append(
                texttospeech.MultiSpeakerMarkup.Turn(
                    text=turn_data["line"], speaker=turn_data["speaker"]
                )
            )

        response = self.tts_client.synthesize_speech(
            input=texttospeech.SynthesisInput(
                multi_speaker_markup=multi_speaker_markup
            ),
            voice=texttospeech.VoiceSelectionParams(
                language_code=self.language_code, name=self.google_voice_name
            ),
            audio_config=texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            ),
        )

        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        print(f'Audio content written to file "{output_file}" using Google TTS.')

    def synthesize_podcast(
        self, dialogue: List[Dict[str, str]], output_file: str
    ) -> None:
        """Choose TTS backend to synthesize final audio."""
        if self.tts_backend == "google":
            self.synthesize_podcast_google(dialogue, output_file)
        else:
            self.synthesize_podcast_openai(dialogue, output_file)

    def create_podcast(
        self, content_path: str, output_file: str = "podcast_output.mp3"
    ) -> Optional[str]:
        """Generate and synthesize a complete podcast from content (PDF file)."""
        dialogue = self.generate_podcast_script(content_path)
        if dialogue:
            self.synthesize_podcast(dialogue, output_file)
            return output_file
        else:
            print("No dialogue generated. Skipping audio synthesis.")
            return None


# Example usage:
if __name__ == "__main__":
    # Select backends via env or code
    LLM_BACKEND = os.getenv("LLM_BACKEND", "openai")  # "openai" or "vertexai"
    TTS_BACKEND = os.getenv("TTS_BACKEND", "openai")  # "openai" or "google"
    PROJECT_ID = os.getenv("PROJECT_ID")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    podcast_gen = PodcastGenerator(
        llm_backend=LLM_BACKEND,
        tts_backend=TTS_BACKEND,
        project_id=PROJECT_ID,
        openai_api_key=OPENAI_API_KEY,
    )
    # Path to local PDF with content for podcast
    source_pdf = "sample_content.pdf"
    output_file = podcast_gen.create_podcast(source_pdf)
    if output_file:
        # For notebook environments
        Audio(output_file)

# -----------------------------------------------------------------------
# Apache 2.0 License -- Original code based on Google Gemini/Vertex AI sample.

# CHANGES MADE (documentation for compliance with Apache 2.0):
# - Script supports both OpenAI and Google/Vertex AI as selectable backends for LLM and TTS, via `llm_backend` and `tts_backend`.
# - When using OpenAI: calls OpenAI Chat Completions to generate podcast dialogue in JSON, and OpenAI TTS for synthesis.
# - When using VertexAI: calls Gemini/vertexai GenerativeModel with response schema for controlled dialogue JSON.
# - For TTS, Google MultiSpeakerMarkup and VoiceSelectionParams are used if `tts_backend="google"`.
# - PDF extraction added (`extract_text_from_pdf`) using PyPDF2 for local PDF inputs (cloud URI support is omitted for wider compatibility).
# - Docstrings and usage adjusted to clarify backend choices and requirements.
# - Example at bottom demonstrates runtime backend selection with env vars.
# - All approaches remain modular and eligible for extension or further parameterization. All Google/Vertex features and options retained if the appropriate backend is selected.

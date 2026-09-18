import os
import base64
import json
from http.server import BaseHTTPRequestHandler
from sarvamai import SarvamAI


class handler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_data = self.rfile.read(content_length)
            data = json.loads(raw_data.decode("utf-8"))

            text = data.get("text", "").strip()
            language = data.get("language", "hi-IN")
            speaker = data.get("speaker", "shubh")

            if not text:
                self.send_json(400, {"error": "Text is required"})
                return

            if len(text) > 2500:
                self.send_json(
                    400,
                    {"error": "Text is too long. Keep it under 2500 characters."}
                )
                return

            api_key = os.environ.get("SARVAM_API_KEY")

            if not api_key:
                self.send_json(
                    500,
                    {"error": "SARVAM_API_KEY is not configured"}
                )
                return

            client = SarvamAI(
                api_subscription_key=api_key
            )

            response = client.text_to_speech.convert(
                model="bulbul:v3",
                text=text,
                target_language_code=language,
                speaker=speaker
            )

            audio_base64 = response.audios[0]
            audio_bytes = base64.b64decode(audio_base64)

            audio_data = base64.b64encode(audio_bytes).decode("utf-8")

            self.send_json(
                200,
                {
                    "success": True,
                    "audio": audio_data,
                    "mime_type": "audio/wav"
                }
            )

        except Exception as error:
            self.send_json(
                500,
                {
                    "success": False,
                    "error": str(error)
                }
            )
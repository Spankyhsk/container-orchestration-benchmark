import requests
import os

WEBHOOK_URL = "https://discordapp.com/api/webhooks/1504898730246279348/W0Ci2IqI2XDq7qTUcchTrd3Td5pEUu63jru0rzkfRykOP4ZAOpB8KoBQ0QxQDGWZa3D-"


# =================================================
# TEXT MESSAGE
# =================================================
def send_message(text: str):
    try:
        requests.post(
            WEBHOOK_URL,
            json={"content": text}
        )
    except Exception as e:
        print("Discord error:", e)


# =================================================
# FILE UPLOAD (PDF, PNG, etc.)
# =================================================
def send_file(file_path: str, message: str = ""):
    try:
        with open(file_path, "rb") as f:

            filename = os.path.basename(file_path)

            requests.post(
                WEBHOOK_URL,
                data={"content": message},
                files={
                    "file": (filename, f)
                }
            )

    except Exception as e:
        print("Discord file error:", e)
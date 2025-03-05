from azure.communication.email import EmailClient
from dotenv import load_dotenv
from django.conf import settings
import os
load_dotenv()

# Fetch credentials from environment
AZURE_EMAIL_ENDPOINT = os.getenv("AZURE_EMAIL_ENDPOINT")
AZURE_EMAIL_ACCESS_KEY = os.getenv("AZURE_EMAIL_ACCESS_KEY")
AZURE_SENDER_EMAIL = os.getenv("AZURE_SENDER_EMAIL")



def send_email(to_email, subject, body):
    try:
        client = EmailClient.from_connection_string(
            f"endpoint={AZURE_EMAIL_ENDPOINT};accesskey={AZURE_EMAIL_ACCESS_KEY}"
        )

        message = {
            "senderAddress": AZURE_SENDER_EMAIL,
            "recipients": {"to": [{"address": to_email}]},
            "content": {
                "subject": subject,
                "plainText": body
            }
        }

        response = client.begin_send(message)
        result = response.result()

        if result.get("error"):  # Check if Azure returned an error
            return {"success": False, "error": result["error"]}

        return {"success": True, "messageId": result.get("id", "Unknown ID")}

    except Exception as e:
        return {"success": False, "error": str(e)}


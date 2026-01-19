def extract_clean_email(email_obj):
    payload = email_obj.get("payload", {})
    parts = payload.get("parts", [])

    text = ""

    for part in parts:
        if part.get("mimeType") == "text/plain":
            import base64
            data = part.get("body", {}).get("data", "")
            decoded = base64.urlsafe_b64decode(data).decode("utf-8")
            text += decoded

    return " ".join(text.split())

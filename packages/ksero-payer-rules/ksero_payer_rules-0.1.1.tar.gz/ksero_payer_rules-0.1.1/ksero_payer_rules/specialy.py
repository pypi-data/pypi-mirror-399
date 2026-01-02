def detect_specialty(text: str) -> str:
    if "Dental" in text:
        return "dental"
    elif "Vision" in text or "VSP" in text or "EyeMed" in text:
        return "vision"
    else:
        return "medical"
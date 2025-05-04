def classify_file_path(filename: str) -> str:
    if filename.endswith(".mp3") or filename.endswith(".wav"):
        return "LanguageTest/Audio"
    elif filename.endswith(".md") or filename.endswith(".txt"):
        return "Room127/Markdown"
    else:
        return "General/Uploads"

def load_text_file(full_path):
    with open(full_path, "r", encoding="utf-8") as file:
        return file.read().strip()

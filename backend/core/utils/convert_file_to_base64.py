import base64


def convert_file_to_base64(file):
    try:
        path = file.path
        with open(path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except (ValueError, FileNotFoundError):
        return None

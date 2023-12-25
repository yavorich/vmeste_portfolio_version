import base64


def convert_file_to_base64(file):
    try:
        path = file.path
        extension = path.split(".")[-1]
        with open(path, "rb") as f:
            data = f.read()
            return "data:image/%s;base64,%s" % (extension, base64.b64encode(data))
    except (ValueError, FileNotFoundError):
        return None

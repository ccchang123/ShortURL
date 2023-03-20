import hashlib

class Hash:
    def ChechValue(self, file: str, value: str) -> bool:
        sha256 = hashlib.sha256()
        with open(file, "rb") as f:
            while True:
                data = f.read(65535)
                if not data:
                    break
                sha256.update(data)
        if sha256.hexdigest() == value:
            return True
        else:
            return False
import hashlib
import json
import logging
import os

from mistralai import Mistral

from mcp_ocrai.services.file_type import FileType, read_document

cache_folder = os.path.expanduser("~/.ocrai")
logger = logging.getLogger()


def obtainhash(path: str) -> str:
    sha256_hash = hashlib.md5()
    with open(path, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class DocumentMCP:
    def __init__(self, path: str):
        self.path: str = path
        self.hash: str = obtainhash(path)
        self.markdown: list[str] | None = None

    def _execute_ocr(self) -> list[str]:
        mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY", None))
        type, url = read_document(self.path)

        match type:
            case FileType.Document:
                mistral_type = "document_url"
            case FileType.Image:
                mistral_type = "image_url"
            case _:
                raise Exception("Incompatible file type")

        response = mistral_client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": f"{mistral_type}", f"{mistral_type}": url},
            include_image_base64=False,
        )

        self.markdown = [page.markdown for page in response.pages]

        # Save markdown to cache
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
        with open(os.path.join(cache_folder, self.hash), "w") as file:
            json.dump(self.markdown, file)

        return self.markdown

    def getOCR(self, pages: set | None = None) -> list[str]:
        # Load from cache
        if self.markdown is None:
            try:
                with open(os.path.join(cache_folder, self.hash)) as file:
                    self.markdown = json.load(file)
                logger.debug("Load from cache")
            except FileNotFoundError:
                logger.debug("File not found on cache")
                pass

        # If not exists on cache, handle OCR
        if self.markdown is None:
            self._execute_ocr()

        if self.markdown is None:
            raise Exception("Imposible to compute the OCR")

        if pages is None:
            return self.markdown

        list_pages = []
        for i in pages:
            if i >= len(self.markdown) or i <= 0:
                raise Exception(
                    f"The document has {len(self.markdown)} pages, so page {i} cannot be displayed"
                )
            list_pages.append(self.markdown[i - 1])

        return list_pages

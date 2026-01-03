import argparse
import os

from fastmcp import FastMCP

from mcp_ocrai.services.document import DocumentMCP
from mcp_ocrai.utils.parse_pages import parse_pages


def startMCP():
    mcp = FastMCP("OCRai!")

    @mcp.tool
    def ocr_over_file(path: str, pages: str | None = None) -> list[str]:
        """Read files with the following extensions:
        Documents: PDF (.pdf), Word Documents (.docx), PowerPoint (.pptx), Text Files (.txt),
        EPUB (.epub), XML/DocBook (.xml), RTF (.rtf), OpenDocument Text (.odt),
        BibTeX/BibLaTeX (.bib), FictionBook (.fb2), Jupyter Notebooks (.ipynb),
        JATS XML (.xml), LaTeX (.tex), OPML (.opml), Troff (.1, .man)
        Images: JPEG (.jpg, .jpeg), PNG (.png), AVIF (.avif), TIFF (.tiff), GIF (.gif),
        HEIC/HEIF (.heic, .heif), BMP (.bmp), WebP (.webp)

        Args:
            path (str): The path to the file to be read
            pages (str | None): Optional. Specifies the pages to extract from the document.
                Format can be a single page number (e.g., "5"), a range of pages (e.g., "1-5"),
                or a combination of both separated by commas (e.g., "1,3,5-7").
                If None, all pages are extracted.
        Returns:
            list[str]: A list of strings, where each string represents the text content of a page.
        """

        document = DocumentMCP(path)

        pages_set = None
        if pages:
            pages_set = parse_pages(pages)

        return document.getOCR(pages=pages_set)

    return mcp


def main():
    parser = argparse.ArgumentParser(description="MCP OCR AI Server")
    parser.add_argument(
        "--api-key",
        type=str,
        help="Mistral API key (overrides MISTRAL_API_KEY environment variable)",
    )
    args = parser.parse_args()

    if args.api_key:
        os.environ["MISTRAL_API_KEY"] = args.api_key

    mcp = startMCP()
    mcp.run()


if __name__ == "__main__":
    main()

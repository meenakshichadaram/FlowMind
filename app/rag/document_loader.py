import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from pathlib import Path
from app.utils.ocr_helper import extract_text_with_ocr
from app.utils.logger import logger

class DocumentLoader:
    """Multi-format document loader supporting PDFs, Web pages, Markdown, TXT & OCR."""

    @staticmethod
    def load_pdf(file_path: str) -> List[Dict[str, Any]]:
        """Extracts text per page from PDF using PyMuPDF with OCR fallback."""
        pages_content = []
        doc = fitz.open(file_path)
        filename = Path(file_path).name

        for page_num, page in enumerate(doc):
            text = page.get_text("text").strip()
            # If text is nearly empty, attempt OCR on page image
            if len(text) < 30:
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                from io import BytesIO
                from PIL import Image
                img = Image.open(BytesIO(img_data))
                ocr_text = extract_text_with_ocr(img)
                if len(ocr_text) > 10:
                    text = f"[OCR Extracted Page {page_num + 1}]\n" + ocr_text

            if text:
                pages_content.append({
                    "content": text,
                    "metadata": {
                        "source": filename,
                        "file_path": str(file_path),
                        "source_type": "PDF",
                        "page": page_num + 1,
                        "total_pages": len(doc)
                    }
                })
        doc.close()
        logger.info(f"Loaded PDF '{filename}' with {len(pages_content)} pages.")
        return pages_content

    @staticmethod
    def load_html(html_content_or_file: str, url_or_name: str = "webpage.html") -> List[Dict[str, Any]]:
        """Parses HTML document or web clip into structured text using BeautifulSoup."""
        if Path(html_content_or_file).exists():
            with open(html_content_or_file, "r", encoding="utf-8", errors="ignore") as f:
                raw_html = f.read()
        else:
            raw_html = html_content_or_file

        soup = BeautifulSoup(raw_html, "html.parser")
        # Remove script and style tags
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        text = soup.get_text(separator="\n").strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        return [{
            "content": clean_text,
            "metadata": {
                "source": url_or_name,
                "source_type": "WebPage",
                "length": len(clean_text)
            }
        }]

    @staticmethod
    def load_text(file_path: str) -> List[Dict[str, Any]]:
        """Loads plaintext or markdown files."""
        path = Path(file_path)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()

        source_type = "Markdown" if path.suffix.lower() in [".md", ".markdown"] else "TXT"
        return [{
            "content": content,
            "metadata": {
                "source": path.name,
                "file_path": str(file_path),
                "source_type": source_type,
                "length": len(content)
            }
        }]

    @classmethod
    def load_auto(cls, file_path: str) -> List[Dict[str, Any]]:
        """Auto-detects file extension and dispatches appropriate loader."""
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return cls.load_pdf(file_path)
        elif ext in [".html", ".htm"]:
            return cls.load_html(file_path, url_or_name=Path(file_path).name)
        elif ext in [".txt", ".md", ".py", ".json"]:
            return cls.load_text(file_path)
        else:
            logger.warning(f"Unsupported file type '{ext}'. Using generic text loader.")
            return cls.load_text(file_path)

from pypdf import PdfReader


class PDFService:

    @staticmethod
    def extract_text(file_path: str) -> str:
        reader = PdfReader(file_path)
        full_text = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        return full_text

from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:

    @staticmethod
    def split_text(text: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        return splitter.split_text(text)

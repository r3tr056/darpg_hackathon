import os
from django.core.management.base import BaseCommand, CommandParser

from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_index(pdf_file_path, index_path):
    loader = PyPDFLoader(file_path=pdf_file_path)
    pdf_docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"],
        chunk_size=1000,
        chunk_overlap=200, 
    )
    chunked_docs = text_splitter.split_documents(pdf_docs)

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunked_docs, embedding=embeddings)
    vector_store.save_local(index_path)


class Command(BaseCommand):
    help = 'Create a FAISS index for the Guide PDFS'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('file', type=str, help='Path to PDF file')
        parser.add_argument('index_path', type=str, help='Path to put the Index in')

    def handle(self, *args, **kwargs):
        pdf_file_path = kwargs['file']
        index_path = kwargs['index_path']
        create_index(pdf_file_path, index_path)
        os.environ['FAISS_INDEX_PATH'] = index_path
        self.stdout.write(self.style.SUCCESS(f'FAISS index created successfully at {index_path}'))
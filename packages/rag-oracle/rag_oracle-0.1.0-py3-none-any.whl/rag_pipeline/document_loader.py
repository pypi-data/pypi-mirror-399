"""
Step 1.1 - Document Loader
Load documents from various sources (PDFs, text files, etc.)
"""

import os
from pathlib import Path
from typing import List, Union
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document


class DocumentLoader:
    """Load documents from various file formats."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt', '.md'}
    
    def load_file(self, file_path: Union[str, Path]) -> List[Document]:
        """
        Load a single file and return Document objects.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            List of Document objects
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {extension}. Supported: {self.supported_extensions}")
        
        # Load based on file type
        if extension == '.pdf':
            loader = PyPDFLoader(str(file_path))
        elif extension in {'.txt', '.md'}:
            loader = TextLoader(str(file_path), encoding='utf-8')
        else:
            raise ValueError(f"Loader not implemented for: {extension}")
        
        documents = loader.load()
        return documents
    
    def load_directory(self, directory_path: Union[str, Path]) -> List[Document]:
        """
        Load all supported files from a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of Document objects from all files
        """
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")
        
        all_documents = []
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    documents = self.load_file(file_path)
                    all_documents.extend(documents)
                except Exception as e:
                    print(f"Warning: Failed to load {file_path}: {e}")
                    continue
        
        return all_documents
    
    def load(self, source: Union[str, Path]) -> List[Document]:
        """
        Load documents from a file or directory.
        
        Args:
            source: Path to file or directory
            
        Returns:
            List of Document objects
        """
        source = Path(source)
        
        if source.is_file():
            return self.load_file(source)
        elif source.is_dir():
            return self.load_directory(source)
        else:
            raise ValueError(f"Source must be a file or directory: {source}")


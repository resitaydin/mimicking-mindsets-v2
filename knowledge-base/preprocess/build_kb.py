import os
import re
import uuid
from typing import List, Dict, Any

import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from tqdm import tqdm
import torch
import re
import unicodedata # For Unicode normalization

# --- Configuration ---
BASE_WORKS_DIR = "../works" # Relative path to the 'works' folder
PERSONAS = [
    {
        "name": "Cemil Meriç",
        "folder_name": "cemil-meric",
        "qdrant_collection_name": "cemil_meric_kb"
    },
    {
        "name": "Erol Güngör",
        "folder_name": "erol-gungor",
        "qdrant_collection_name": "erol_gungor_kb"
    }
]

# Embedding Model
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
# bge-m3 has 1024 dimensions.
EMBEDDING_DIMENSION = 1024

# Qdrant Configuration
QDRANT_HOST = "my-qdrant-instance"
QDRANT_PORT = 6333

# Text Splitting Configuration
CHUNK_SIZE = 1000  # Characters
CHUNK_OVERLAP = 200 # Characters

# --- Helper Functions ---

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a single PDF file using PyMuPDF."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text() + "\n"  # Add newline to separate page contents
        doc.close()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

def preprocess_turkish_text(text: str) -> str:
    """
    Improved preprocessing for Turkish text, focusing on low-risk cleanup
    while preserving essential structure like paragraphs.
    """
    if not text:
        return ""

    # 1. Unicode Normalization (NFC)
    #    Ensures consistent representation of characters (e.g., accented chars).
    #    'NFC' (Normalization Form C) composes characters.
    text = unicodedata.normalize('NFC', text)

    # 2. Normalize various newline characters to a single standard newline (\n)
    text = re.sub(r'\r\n|\r', '\n', text)

    # 3. De-hyphenation: Rejoin words broken at the end of lines.

    text = re.sub(r'-\n([a-zçğıöşü])', r'\1', text)

    # 4. Replace multiple spaces with a single space (but preserve newlines)
    text = re.sub(r'[ \t]+', ' ', text)

    # 5. Clean up spaces around newlines
    #    Remove spaces at the beginning of a line after a newline
    text = re.sub(r'\n +', '\n', text)
    #    Remove spaces at the end of a line before a newline
    text = re.sub(r' +\n', '\n', text)

    # 6. Normalize multiple newlines to a maximum of two (for paragraph separation)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 7. Remove leading/trailing whitespace from the whole text
    text = text.strip()

    # 9. Optional: Remove non-printable control characters (except tab, newline, carriage return)
    #    This can remove garbage characters from faulty PDF extractions.
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    return text

def get_pdf_files(folder_path: str) -> List[str]:
    """Gets all PDF file paths from a given folder."""
    pdf_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

# --- Main Processing Logic ---

def build_knowledge_base_for_persona(
    persona_config: Dict[str, Any],
    qdrant_client: QdrantClient,
    embedding_model: SentenceTransformer,
    text_splitter: RecursiveCharacterTextSplitter
):
    """Builds the knowledge base for a single persona."""
    persona_name = persona_config["name"]
    persona_folder = os.path.join(BASE_WORKS_DIR, persona_config["folder_name"])
    collection_name = persona_config["qdrant_collection_name"]

    print(f"\n--- Processing Persona: {persona_name} ---")
    print(f"Source folder: {persona_folder}")
    print(f"Qdrant collection: {collection_name}")

    # 1. Create Qdrant collection (if it doesn't exist)
    try:
        # Check if collection exists and delete it if it does (to replicate recreate_collection behavior)
        if qdrant_client.collection_exists(collection_name=collection_name):
            qdrant_client.delete_collection(collection_name=collection_name)
            print(f"Existing collection '{collection_name}' deleted.")
        
        # Create new collection
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=EMBEDDING_DIMENSION, distance=models.Distance.COSINE)
        )
        print(f"Collection '{collection_name}' created successfully.")
    except Exception as e:
        print(f"Error creating Qdrant collection '{collection_name}': {e}")
        # Check if collection already exists with compatible config
        try:
            qdrant_client.get_collection(collection_name=collection_name)
            print(f"Collection '{collection_name}' already exists. Proceeding...")
        except Exception as e_get:
            print(f"Failed to get collection info for '{collection_name}': {e_get}. Aborting for this persona.")
            return


    # 2. Text Collection & Digitization (PDF reading)
    pdf_files = get_pdf_files(persona_folder)
    if not pdf_files:
        print(f"No PDF files found in {persona_folder}. Skipping persona.")
        return
    print(f"Found {len(pdf_files)} PDF files for {persona_name}.")

    all_chunks_with_metadata = []

    for pdf_path in tqdm(pdf_files, desc=f"Processing PDFs for {persona_name}"):
        raw_text = extract_text_from_pdf(pdf_path)

        if not raw_text.strip():
            print(f"    No text extracted from {os.path.basename(pdf_path)}. Skipping.")
            continue

        # 3. Text Cleaning & Preprocessing
        cleaned_text = preprocess_turkish_text(raw_text)

        # 4. Chunking
        chunks = text_splitter.split_text(cleaned_text)
        print(f"    Split into {len(chunks)} chunks.")

        for i, chunk_text in enumerate(chunks):
            all_chunks_with_metadata.append({
                "text": chunk_text,
                "source_pdf": os.path.basename(pdf_path),
                "chunk_index": i
            })

    if not all_chunks_with_metadata:
        print(f"No text chunks generated for {persona_name}. Nothing to embed or store.")
        return

    print(f"Generated a total of {len(all_chunks_with_metadata)} text chunks for {persona_name}.")

    # 5. Embedding Generation (in batches for efficiency)
    print("Generating embeddings...")
    texts_to_embed = [item["text"] for item in all_chunks_with_metadata]
    
    embeddings = embedding_model.encode(texts_to_embed, show_progress_bar=True, batch_size=16)
    print(f"Generated {len(embeddings)} embeddings.")

    # 6. Vector Database (Knowledge Base) Storage
    print(f"Storing chunks and embeddings in Qdrant collection '{collection_name}'...")
    points_to_upsert = []
    for i, item in enumerate(all_chunks_with_metadata):
        points_to_upsert.append(
            models.PointStruct(
                id=str(uuid.uuid4()), # Unique ID for each chunk
                vector=embeddings[i].tolist(),
                payload={
                    "text": item["text"],
                    "source": item["source_pdf"],
                    "persona": persona_name,
                    "chunk_index": item["chunk_index"]
                }
            )
        )

    # Upsert in batches to Qdrant
    batch_size = 100 # Qdrant batch size
    for i in tqdm(range(0, len(points_to_upsert), batch_size), desc="Upserting to Qdrant"):
        batch = points_to_upsert[i:i + batch_size]
        try:
            qdrant_client.upsert(collection_name=collection_name, points=batch, wait=True)
        except Exception as e:
            print(f"Error upserting batch to Qdrant: {e}")
            # Optionally, add retry logic or save failed batches

    print(f"Successfully stored {len(points_to_upsert)} items in '{collection_name}'.")
    print(f"--- Finished processing Persona: {persona_name} ---")


if __name__ == "__main__":
    print("Starting Phase 1: Knowledge Base Construction...")
    
    # Initialize Qdrant Client
    try:
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        qdrant_client.get_collections() # Check connection
        print(f"Successfully connected to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
    except Exception as e:
        print(f"Could not connect to Qdrant: {e}")
        print("Please ensure Qdrant is running and accessible.")
        exit(1)

    # Initialize Embedding Model
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    try:
        if torch.cuda.is_available():
            device = 'cuda'
            print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = 'cpu'
            print("CUDA is not available. Using CPU.")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
        print("Embedding model loaded successfully.")
    except Exception as e:
        print(f"Error loading embedding model '{EMBEDDING_MODEL_NAME}': {e}")
        print("Make sure you have an internet connection to download the model for the first time,")
        print("and that 'sentence-transformers' and its dependencies (like PyTorch) are correctly installed.")
        exit(1)


    # Initialize Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    # Process each persona
    for persona_config in PERSONAS:
        build_knowledge_base_for_persona(
            persona_config,
            qdrant_client,
            embedding_model,
            text_splitter
        )

    print("\nPhase 1: Knowledge Base Construction completed for all personas.")
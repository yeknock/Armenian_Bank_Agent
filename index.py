from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import chromadb
import uuid
import os

load_dotenv()
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client_chromadb = chromadb.PersistentClient(path="./chroma_db")
collection = client_chromadb.get_or_create_collection(name="banks_info")

# All the paths of .md files that need to be embedded
dirs = [
    "acba/branches", "acba/credits", "acba/deposits",
    "ameria/branches", "ameria/credits", "ameria/deposits",
    "converse/branches", "converse/credits", "converse/deposits"
    ]


def embed_chunks(dirs):
    all_chunks_data = []

    for dir in dirs:
        directory = Path("knowledge/" + dir)

        if not directory.exists():
            print("No such Directory:")
            continue

        for filepath in directory.glob('*.md'):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                words = content.split()

                i = 0
                while i < len(words):
                    chunk_list = words[i:i + 200]
                    chunk_str = ' '.join(chunk_list)

                    response = client_openai.embeddings.create(
                        input = chunk_str,
                        model = "text-embedding-3-small"
                    )

                    all_chunks_data.append({
                        "id": str(uuid.uuid4()), # chromaDB requires unique IDs
                        "embedding": response.data[0].embedding,
                        "document": chunk_str,
                        "metadata": {
                            "source": str(filepath),
                            "bank": dir.split('/')[0],
                            "topic": dir.split('/')[1],
                            "sub_topic": filepath.stem
                        }
                    })
                    
                    i += 200
    return all_chunks_data

chunks = embed_chunks(dirs)

collection.add(
    ids=[item["id"] for item in chunks],
    embeddings=[item["embedding"] for item in chunks],
    documents=[item["document"] for item in chunks],
    metadatas=[item["metadata"] for item in chunks]
)

print(f"Total chunks - {collection.count()}")
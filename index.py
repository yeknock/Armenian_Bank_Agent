from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

dirs = [
    "acba/branches", #, "acba/credits", "acba/deposits",
    "ameria/branches" #, "ameria/credits", "ameria/deposits",
    #"converse/branches", "converse/credits", "converse/deposits"
    ]

for dir in dirs:
    directory = Path("knowledge/" + dir)
    for filepath in directory.glob('*.md'):
        with open(filepath, "r", encoding="utf-8") as f:
            words = f.read().split()
            i = 0
            while i < len(words):
                chunk_list = words[i:i + 200]
                chunk_str = ' '.join(chunk_list)

                response = client.embeddings.create(
                    input = chunk_str,
                    model = "text-embedding-3-small"
                )

                print(response.data[0].embedding)
                i += 200

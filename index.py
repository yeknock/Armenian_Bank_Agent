from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

dirs = [
    "acba/branches", "acba/credits", "acba/deposits",
    "ameria/branches", "ameria/credits", "ameria/deposits",
    "converse/branches", "converse/credits", "converse/deposits"
    ]

for dir in dirs:
    directory = Path("knowledge/" + dir)
    for filepath in directory.glob('*.md'):
        with open(filepath, "r", encoding="utf-8") as f:
            response = client.embeddings.create(
                input = f.read(),
                model = "text-embedding-3-small"
            )

            print(response.data[0].embedding)

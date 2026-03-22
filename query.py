from dotenv import load_dotenv
from openai import OpenAI
import chromadb
import os
import json

load_dotenv()
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client_chromadb = chromadb.PersistentClient(path="./chroma_db")
collection = client_chromadb.get_or_create_collection(name="banks_info")

question = "ես ուզում եմ մանկական ավանդ ներդնել ամերիա բանկում։ Կարո՞ղ ես ասել պայմանները"


def embed_query(query):
    response = client_openai.embeddings.create(
        input = query,
        model = "text-embedding-3-small"
    )

    return response.data[0].embedding


def detect_intent(question):
    completion = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": """You are an intent classifier for an Armenian banking assistant.
                Available banks: acba, ameria, converse
                Available topics: credits, deposits, branches

                Rules:
                1. Return ONLY a valid JSON object.
                2. If the user asks a broad question (e.g., "վարկերի մասին", "tell me about loans") set sub_topic to "general".
                3. If the user specifies a type, use: mortgage, car_loan, consumer_loan, student_loan, etc.

                Return format: {"bank": "ameria", "topic": "credits", "sub_topic": "general"}"""},
            {"role": "user", "content": question}
        ]
    )

    response_text = completion.choices[0].message.content
    try:
        intent = json.loads(response_text)
        return intent.get("topic"), intent.get("bank"), intent.get("sub_topic")
    except:
        return None, None, None
    


def get_context(question):
    topic, bank, sub_topic = detect_intent(question)
    
    search_query = f"{question} {sub_topic}" if sub_topic else question
    embedded_query = embed_query(search_query)

    filters = []
    if bank:
        filters.append({"bank": {"$eq": bank}})
    if topic:
        filters.append({"topic": {"$eq": topic}})
    

    where_filter = {}
    if len(filters) > 1:
        where_filter = {"$and": filters}
    elif len(filters) == 1:
        where_filter = filters[0]
    else:
        where_filter = None

    # If sub_topic is found use 10, if not we want more data
    num_results = 10 if sub_topic else 20

    query = collection.query(
        query_embeddings=[embedded_query],
        n_results=num_results,
        where=where_filter
    )
    
    return "\n\n".join(query['documents'][0])
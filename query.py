from dotenv import load_dotenv
from openai import OpenAI
import chromadb
import os
import json

load_dotenv()
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client_chromadb = chromadb.PersistentClient(path="./chroma_db")
collection = client_chromadb.get_or_create_collection(name="banks_info")

question = "Որքան է Ամերիա բանկում վարկային տոկոսադրույքյը"



def embed_query(query):
    response = client_openai.embeddings.create(
        input = query,
        model = "text-embedding-3-small"
    )

    return response.data[0].embedding


def detect_intent(question):
    completion = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """You are an intent classifier for an Armenian banking assistant.
                Given a user question in Armenian or English, identify:
                1. Which bank they are asking about
                2. Which topic they are asking about

                Available banks: acba, ameria, converse
                Available topics: credits, deposits, branches

                Rules:
                - Return ONLY a valid JSON object, nothing else
                - No explanation, no extra text, just JSON
                - If bank is not mentioned or unclear → use null
                - If topic is not clear → use null
                - Armenian bank name variations:
                acba = ակբա, Ակբա, ԱԿԲԱ, Ակբա Բանկ, ակբա բանկ, acba, Acba, ACBA, acbabank, acba bank
                ameria = ամերիա, Ամերիա, ամերիաբանկ, Ամերիաբանկ, Ամերիա Բանկ, ameria, Ameria, ameriabank, AmeriaBank, ameria bank
                converse = կոնվերս, Կոնվերս, կոնվերս բանկ, Կոնվերս Բանկ, converse, Converse, conversebank, converse bank

                - Topics:
                - credits = վարկ, վարկեր, վարկավորում, վարկային, վարկավորման, տոկոս, տոկոսադրույք, տոկոսներ, հիփոթեք, հիփոթեքային, հիպոտեկ, ավտովարկ, ավտո վարկ, մեքենայի վարկ, սպառողական վարկ
                - deposits = ավանդ, ավանդներ, ավանդային, դեպոզիտ, կուտակել, կուտակային, խնայողական, խնայել, խնայողություն, ներդրում, ներդրումային, վանդ, ավանտ։
                - branches = մասնաճյուղ, մասնաճյուղեր, բանկոմատ, բանկոմատներ, տերմինալ, տերմինալներ, հասցե, հասցեներ, քարտեզ, մոտակա, գրասենյակ, սպասարկման սրահ                


                Sub-topics (return as sub_topic field):
                - If topic is credits, identify the specific loan type:
                mortgage = հիփոթեք, հիփոթեքային, բնակարան, բնակարանի ձեռքբերում, տուն, անշարժ գույք, դիասպորա, կառուցապատում, վերանորոգում, hipotek, tun, bnakaran, ansharj guyq
                car_loan = ավտովարկ, ավտո վարկ, մեքենայի վարկ, ավտոսրահ, տրանսպորտային, avtovark, meqena, meqenayi vark
                consumer_loan = սպառողական, անձնական, առանց գրավի, կանխիկ վարկ, sparoxakan, andznakan, kanxik vark
                credit_line = վարկային գիծ, օվերդրաֆտ, քարտային վարկ, varkayin gic, overdraft
                student_loan = ուսումնական, ուսանող, ուսանողական վարկ, կրթական, usumnakan, usanoxakan, usanox
                investment_loan = ներդրումային, էներգետիկ, բիզնես վարկ, nerdrumayin, biznes vark
                - If topic is deposits, identify:
                savings = խնայել, խնայողություն, կուտակել, կուտակային, խնայողական հաշիվ, xnayel, xnayoxutyun, kutakel
                kids_deposit = երեխա, երեխաների, մանկական ավանդ, erexa, erexaneri, mankakan avand
                bonds = պարտատոմս, պարտատոմսեր, արժեթղթեր, partatomser, bonds
                investment = ներդրում, ներդրումներ, ակցիաներ, nerdrum, nerdrumner
                - If topic is branches, sub_topic = հասցե, որտեղ է գտնվում, քարտեզ, մոտակա, քաղաք, մասնաճյուղ, փողոց, hasce, location, qartez, motaka, ժամերը, երբ է բացվում, մինչև քանիսն է աշխատում, շաբաթ օրը աշխատում է, գրաֆիկ, jamery, ashxatanqayin jamer, grafik,բանկոմատ, տերմինալ, կանխիկացում, գումար մուտքագրել, cash-in, bankomat, atm, terminal, kanxikacum, 24/7, շուրջօրյա, պրեմիում սպասարկում, հաճախորդների սպասարկում, սրահ, shurjorya, premium

                Return format:
                {"bank": "ameria", "topic": "credits", "sub_topic": "mortgage"}
                Return format:
                {"bank": "ameria", "topic": "branches"}"""},
            {"role": "user", "content": question}
        ]
    )

    response_text = completion.choices[0].message.content
    try:
        intent = json.loads(response_text)
        bank = intent["bank"]
        topic = intent["topic"]
        sub_topic = intent.get("sub_topic") # .get() is for case, when it won't be
    except:
        bank = None
        topic = None
        sub_topic = None

    print(f"Detected bank: {bank}, topic: {topic}")
    print("\n\n")
    return topic, bank, sub_topic
    


def searchInDB(embedded_query, where_filter=None):
    if where_filter:
        return collection.query(
            query_embeddings=[embedded_query],
            n_results=10,
            where=where_filter
        )
    else:
        return collection.query(
            query_embeddings=[embedded_query],
            n_results=10
        )



def get_context(question):
    topic, bank, sub_topic = detect_intent(question)

    # enhance query with sub_topic
    if sub_topic:
        enhanced_query = f"{question} {sub_topic}"
    else:
        enhanced_query = question
    
    embedded_query = embed_query(enhanced_query)


    if topic and bank:
        where_filter = {
            "$and": [
                {"bank": {"$eq": bank}},
                {"topic": {"$eq": topic}}
            ]
        }
    elif topic and not bank:
        where_filter = {"topic": {"$eq": topic}}
    elif bank and not topic:
        where_filter = {"bank": {"$eq": bank}}
    else:
        where_filter = None


    query = searchInDB(embedded_query, where_filter)
    extraction = "\n\n".join(query['documents'][0])

    return extraction





def ask_llm(question):
    context = get_context(question)
    print("CONTEXT SENT TO LLM:")
    print(context[:500])
    print("\n\n")

    completion = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"""You are a voice banking assistant for Armenian banks.
            Answer ONLY about credits, deposits and branches.
            Use ONLY the context below.
            Answer in Armenian.
            If answer not in context say: Այդ մասին տեղեկատվություն չունեմ

            Context:
            {context}"""},
            {"role": "user", "content": question}
        ]
    )

    return completion.choices[0].message.content


answer = ask_llm(question)
print(answer)
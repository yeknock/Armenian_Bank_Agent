# Armenian_Bank_Agent
This project is an AI-powered voice assistant specifically designed for the Armenian banking sector. It uses a Retrieval-Augmented Generation (RAG) architecture to provide accurate information about interest rates, mortgage terms, and branch locations for banks like Converse Bank, Ameriabank, and Acba.

!["image-url-or-path"](https://cdn.prod.website-files.com/65a7d326e810bc36dae1978f/68405224a17261084ff56357_best_ai_voice_agents_that_.webp)

## Architecture & Decisions:

#### Core Pipeline

Voice Framework - LiveKit

STT (OpenAI Whisper): Whisper is among the most robust models for Armenian speech recognition. It handles the unique phonetics of the language with high accuracy, which is critical for a banking application.I utilized Whisper's initial_prompt capability to "prime" the model with specific Armenian banking terminology (e.g., տոկոսադրույք, հիփոթեք, Ամերիաբանկ).I chose the Whisper-1 because they offer a superior balance of speed and "reasoning" and also optimal cost.

TTS (OpenAI Nova): After testing multiple voices, Nova was selected for its high clarity and energy, which performs better than deeper voices (of course still it can do some mistakes, but it continues to stay the best one among openAI's models).

STT (OpenAI Whisper): Specifically configured with a custom Armenian banking prompt. This acts as a phonetic guide to ensure brand names like "Ակբա" and technical terms like "տարեկան տոկոսադրույք" are transcribed accurately even in noisy environments.


#### Data Retrieval (RAG)

Intent Classifier (GPT-4o-mini): Before searching the database, the system performs a "Reasoning Step" to extract the specific Bank, Topic, and Sub-topic. This allows us to apply strict metadata filters in ChromaDB, preventing the model from accidentally giving Ameria Bank's rates when the user asked about ACBA.

Vector Database (ChromaDB): I used a persistent local instance for fast, offline-capable retrieval. I implemented a Sliding Window Chunking method (150 words with a 50-word overlap). This ensures that mathematical figures and interest rate tables are never cut in half, preserving the context for the LLM.


## Setup Instructions


Python 3.10 or higher

LiveKit Server - I used local server (my laptop)

#### Clone the repository
`git clone <your-repo-link>`
`cd armenian-banking-ai`

#### Create and activate virtual environment
`python -m venv venv`
`source venv/bin/activate  # Windows: venv\Scripts\activate`

#### Install dependencies
`pip install -r requirements.txt`


## Configuration

Create a .env file in the root directory:


`OPENAI_API_KEY=your_openai_key` <br>
`LIVEKIT_URL=ws://localhost:7880` <br>
`LIVEKIT_API_KEY=devkey` <br>
`LIVEKIT_API_SECRET=secret` <br>


## Initialize the Knowledge Base

`python index.py`


## Running the Agent

`python agent.py dev`


## Launch in Development Mode:

`livekit-server --dev`









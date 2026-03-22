import asyncio
from dotenv import load_dotenv

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli, llm
from livekit.plugins import openai, silero

from query import get_context

load_dotenv()

SYSTEM_INSTRUCTIONS = """You are a helpful voice banking assistant for Armenian banks (ACBA, Ameria, Converse).
Always respond in Armenian.

GUIDELINES:
1. Answer ONLY questions about credits, deposits and branch locations.
2. Use the retrieved context to answer. 
3. If the context has partial information, use what you have and ask the user to clarify.
4. Only say "Այդ մասին տեղեկատվություն չունեմ" if the question is completely unrelated to banking.
5. Keep responses SHORT — maximum 2-3 sentences — this is a voice call.
6. Be polite and formal.
7. If the user asks about a specific bank, focus on that bank's information."""


class BankingAssistant(Agent):
    def __init__(self):
        super().__init__(instructions=SYSTEM_INSTRUCTIONS)

    async def on_user_turn_completed(self, turn_ctx, new_message):
        user_query = new_message.text_content
        print(f"User said: {user_query}")
        
        context = await asyncio.get_running_loop().run_in_executor(
            None, get_context, user_query
        
        )
        # print(f"Context found: {context[:200]}")  # see what context was retrieved
        
        turn_ctx.add_message(
            role="system",
            content=f"Retrieved context:\n{context}"
        )


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        stt=openai.STT(
            language="hy-AM",
            prompt = "Բանկ, վարկ, ավանդ, տոկոս, հիփոթեք, մասնաճյուղ, Ամերիաբանկ, Ակբա, Կոնվերս, վարկային գիծ, օվերդրաֆտ, կանխավճար, տարեկան տոկոսադրույք, հաշվի քաղվածք, քարտի սպասարկում, դրամարկղ, վարկունակություն, գրավադրում, հերթագրում, առցանց բանկինգ"
        ),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        vad=silero.VAD.load(
            min_silence_duration=1.0,
            activation_threshold=0.4,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=BankingAssistant(),
    )

    await session.generate_reply(
        instructions="Greet the user in Armenian as a banking assistant."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
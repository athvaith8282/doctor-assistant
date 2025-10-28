from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)

from dotenv import load_dotenv
load_dotenv()


from livekit.plugins import deepgram, elevenlabs, openai, silero
from livekit.plugins import langchain
from agent import agent

from langfuse.langchain import CallbackHandler
 
langfuse_handler = CallbackHandler()


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    # Create a minimal Agent wrapper (instructions handled by LangChain agent)
    agent_wrapper = Agent(instructions="You are a friendly voice assistant for Dr.Paul's Clinic, helping patients schedule appointments with Dr.Paul.")
    
    session = AgentSession(
        vad=silero.VAD.load(),
        # any combination of STT, LLM, TTS, or realtime API can be used
        stt=deepgram.STT(model="nova-3"),
        llm=langchain.LLMAdapter( 
            graph=agent,
            config = {
                "callbacks": [langfuse_handler],
            }
        ),
        tts=elevenlabs.TTS(),
    )

    await session.start(agent=agent_wrapper, room=ctx.room)
    await session.generate_reply(instructions="Greet the user and Tell Welcome to Dr.Paul's Clinic, How can I help you today?")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
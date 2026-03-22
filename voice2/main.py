import os
import asyncio
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import silero, deepgram
from livekit.plugins.groq import STT as GroqSTT
from groq import Groq

for key in list(os.environ.keys()):
    if "LIVEKIT" in key:
        del os.environ[key]

os.environ["LIVEKIT_URL"] = "ws://localhost:7880"
os.environ["LIVEKIT_API_KEY"] = "devkey"
os.environ["LIVEKIT_API_SECRET"] = "secret"

load_dotenv()

class ArmenianBankAgent(Agent):
    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise ValueError("Missing API keys")
        super().__init__(
            instructions="You are an Armenian bank assistant.",
            stt=GroqSTT(
                model="whisper-large-v3",
                language="hy",
                prompt="Բանկային հարցեր, վարկեր, ավանդներ, մասնաճյուղեր",
            ),
            tts=deepgram.TTS(
                model="aura-asteria-en",
                api_key=os.getenv("DEEPGRAM_API_KEY"),
            ),
        )
        self.groq_client = Groq(api_key=groq_key)
        self.model = "llama-3.3-70b-versatile"
        self.system_prompt = """Դուք Հայաստանի բանկային օգնական եք:

ԿԱՐԵՎՈՐ ԿԱՆՈՆՆԵՐ:
1. ՊԱՏԱՍԽԱՆԵԼ ՄԻԱՅՆ հետևյալ թեմաներով:
   - Վարկեր (սպառողական, հիփոթեք, ավտովարկ)
   - Ավանդներ (ժամկետային, ընթացիկ)
   - Մասնաճյուղերի հասցեներ և աշխատանքային ժամեր

2. ԵԹԵ հարցը ԱՅԼ ԹԵՄԱՅԻՑ Է, պատասխանել:
   "Ներողություն, ես կարող եմ օգնել միայն վարկերի, ավանդների և մասնաճյուղերի հարցերով:"

3. Պատասխանել հայերեն լեզվով:
4. Պատասխանները լինեն հակիրճ և օգտակար:"""

    async def on_enter(self):
        await self.session.say("Բարև ձեզ, ես ձեր բանկային օգնականն եմ:", allow_interruptions=False)

    async def on_user_turn_completed(self, turn_ctx, new_message):
        if hasattr(new_message, 'content'):
            if isinstance(new_message.content, str):
                text = new_message.content
            elif isinstance(new_message.content, list):
                text = " ".join(
                    part.text if hasattr(part, 'text') else str(part)
                    for part in new_message.content
                )
            else:
                text = str(new_message.content)
        else:
            text = str(new_message)
        if not text.strip():
            return
        try:
            print(f"🎤 You: {text}")
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=500
            )
            answer = response.choices[0].message.content
            print(f"🤖 Agent: {answer}")
            await self.session.say(answer)
        except Exception as e:
            print(f"❌ Groq error: {e}")
            await self.session.say("Ներողություն, սխալ տեղի ունեցավ:")

async def entrypoint(ctx: JobContext):
    print(f"🎯 Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    session = AgentSession(vad=silero.VAD.load())
    await session.start(agent=ArmenianBankAgent(), room=ctx.room)
    print("✅ Agent is running!")
    await asyncio.sleep(999999)

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting LOCAL LiveKit Agent")
    print(f"📡 Connecting to: ws://localhost:7880")
    print("=" * 50)
    options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        ws_url="ws://localhost:7880",
        api_key="devkey",
        api_secret="secret",
    )
    cli.run_app(options)
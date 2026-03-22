[README.md](https://github.com/user-attachments/files/26168679/README.md)
# 🏦 Armenian Bank Voice Agent

A voice AI agent that answers questions about Armenian banks (Ameriabank, Ardshinbank, ACBA Bank) in Armenian language. Built with LiveKit Agents framework.

## What it does
- Understands spoken Armenian
- Answers questions about **loans**, **deposits**, and **branch locations**
- Uses real data scraped from Ameriabank, Ardshinbank, and ACBA Bank websites
- Refuses to answer questions outside these topics

---

## Requirements
- Python 3.11
- LiveKit server binary

---

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Install dependencies
```bash
py -3.11 -m pip install -r requirements.txt
```

### 3. Create `.env` file
Create a file named `.env` in the project folder:
```
GROQ_API_KEY=your_groq_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

Get your free API keys here:
- Groq: https://console.groq.com
- Deepgram: https://console.deepgram.com

---

## Running the Agent

### Step 1 — Download LiveKit server
Download LiveKit server for Windows:
https://github.com/livekit/livekit/releases

### Step 2 — Start LiveKit server
Open a terminal, navigate to the LiveKit folder and run:
```bash
cd C:\Users\<your-username>\Downloads\livekit_1.9.12_windows_amd64
.\livekit-server.exe --dev --bind 0.0.0.0
```

### Step 3 — Run the agent
Open a new terminal in the project folder:
```bash
py -3.11 o.py dev
```

### Step 4 — Generate access token
Open another new terminal in the project folder:
```bash
py -3.11 forToken.py
```
Copy the generated token from the output.

### Step 5 — Connect to Playground
Open LiveKit Playground: https://agents-playground.livekit.io
- Server URL: `ws://localhost:7880`
- Paste the token from Step 4
- Click Connect and start speaking in Armenian

---

## Terminal Mode (without LiveKit)

There is also a standalone terminal-based version of the agent that works without LiveKit.
It listens to your microphone, understands Armenian speech and responds in the terminal.

To run it:
```bash
py -3.11 test.py
```

> Note: This version speaks responses out loud .

---

## Project Structure
```
├── o.py                    # Main agent (LiveKit)
├── test.py                 # Standalone terminal agent (no LiveKit)
├── retriever.py            # Bank data retrieval (RAG)
├── forToken.py             # Generates LiveKit access token
├── bank_faiss_index/       # Vector database with bank data
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not in repo)
└── README.md
```

---

## Architecture

| Component | Technology |
|---|---|
| Framework | LiveKit Agents 1.5.0 |
| STT (Speech to Text) | Groq Whisper Large V3 |
| LLM | Groq LLaMA 3.3 70B |
| TTS (Text to Speech) | Deepgram Aura |
| VAD (Voice Activity) | Silero VAD |
| Knowledge Base | FAISS + HuggingFace Embeddings |

---

## Banks Covered
- Ameriabank
- Ardshinbank
- ACBA Bank

## Topics the agent handles
- Loans (consumer, mortgage, auto)
- Deposits (term, current)
- Branch addresses and working hours

---

## Note on Armenian TTS
All high-quality native Armenian Text-to-Speech models (Google Cloud, ElevenLabs)
require a paid account. This project uses Deepgram Aura as a free alternative,
which speaks Armenian text with an English accent.

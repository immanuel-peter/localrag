# LocalRAG

**LocalRAG** is a terminal-based LLM chat tool with infinite memory through local vector search.
It turns your terminal into a Claude/ChatGPT/OpenAI/Gemini/Ollama-style interface with persistent, searchable conversation memory.

---

## Features

- ✨ Interactive chat with leading OpenAI, Anthropic, Gemini, xAI, and local Ollama models
- 🧠 Infinite chat memory via local FAISS vectorstore (Retrieval-Augmented Generation)
- 📂 Save and continue favorite chats at any time (across all models)
- 🏷️ Automatic, smart conversation titling for easy recall
- 🔄 Switch models live (config and CLI) including local/proprietary
- 🖼️ Send images directly in chat with `\image <path>` (for vision-capable models)
- 🔑 New, unified config: supports OpenAI/Anthropic/Gemini/xAI/Ollama in one flow
- 🍃 Local LLM support via Ollama: Run Llama, Gemma, DeepSeek, Phi, and more on your machine!
- 📜 Expanded model list (`localrag models`), returns both proprietary and local models with context window size
- ⭐ Update checker: easily update to the latest version via the CLI
- 🚫 100% local & privacy-respecting. Your chat memory never leaves your device.

---

## Installation

```bash
pip install git+https://github.com/immanuel-peter/localrag.git
```

Requires Python 3.8 or higher.

Optional for Local LLMs:
Install [Ollama](https://ollama.com/download). It is recommended to pull all of the models you want to use first and then use LocalRAG for a much more rich experience.

---

## Quickstart

### 1. Configure API Keys and Providers

```bash
localrag config
```

You'll be prompted to set OpenAI, Anthropic, Google Gemini, and xAI API keys. You may also configure Ollama if installed.
Also set your default model!

---

### 2. Start a Chat (with ANY Supported Model)

```bash
localrag run gpt-4.1
localrag run claude-3.7
localrag run gemini-2.5-pro
localrag run llama-4-scout
```

Use `localrag models` to see all valid aliases!

---

### 3. Chat Commands

| Command           | Action                                          |
| :---------------- | :---------------------------------------------- |
| `\save`           | Save chat as favorite                           |
| `\clear`          | Clear current chat                              |
| `\switch <model>` | Switch LLM/model if no messages sent            |
| `\image <path>`   | Attach image to next user message (vision LLMs) |
| `\quit`           | Exit LocalRAG                                   |
| `\help`           | Show available commands                         |

---

### 4. View and Continue Saved Chats

```bash
localrag saved
localrag saved -c 2
```

---

### 5. Update LocalRAG

```bash
localrag update
```

---

## Persistent Storage

Everything is local:

```
~/.localrag/
├── chats/             # Individual chat JSON files
├── vector_store.faiss # FAISS index (chat context memory)
├── vector_store.json  # Metadata (chat IDs)
├── config.json        # API keys and default model
```

**Your chat memory never leaves your device.**

---

## How It Works

- Each message (user and assistant) is embedded via sentence-transformers into a FAISS vector DB
- Every new user message is contextually enriched by searching all past chats for relevant history
- Context is added to your model prompt (no cloud API sees your full memory)
- Smarter, more personalized and contextual conversations—across models/providers
- You can use both local and proprietary LLMs in same CLI

---

## Supported Models (Proprietary & Local)

See full live list with:

```bash
localrag models
```

Examples of currently supported:

**Proprietary:**

- `gpt-4.1`, `gpt-4o-mini`, `o4-mini`, `o3` (OpenAI)
- `claude-3.7`, `claude-3.5` (Anthropic)
- `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0` (Google)
- `grok-3` (xAI)

**Local/Ollama:**

- `llama-4-scout`, `llama-4-maverick`, `llama-3.3` (Meta)
- `gemma3` (Google), `deepseek-r1` (DeepSeek), `phi-4-mini` (Microsoft), and more!

---

## Contributing

Contributions are very welcome! 🚀

Want to:

- Add support for new LLMs/providers/local models?
- Improve vector search/RAG logic?
- Add slash commands, CLI features, or file support?
- Enhance performance or UX?

Please fork, branch, and submit a pull request with your improvements.
Keep PRs focused and modular!

---

## License

MIT License.
Made by Immanuel Peter.

---

## Future Ideas

- Chat with files
- Session-based summaries
- Custom/plug-in RAG pipelines
- Usage of custom models

Stay tuned!

---

**Breaking change:**
If you have used previous versions, please re-run `localrag config` to refresh your keys and set up new provider options!

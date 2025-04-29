# LocalRAG

**LocalRAG** is a terminal-based LLM chat tool with infinite memory through local vector search.
It turns your terminal into a Claude/ChatGPT-style interface with persistent, searchable conversation memory.

---

## Features

- ✨ Interactive chat experience with LLMs
- 📅 Infinite memory via FAISS vectorstore
- 📂 Save and continue favorite chats
- 🔄 Switch models mid-session (when possible)
- 💡 Context retrieval for smarter conversations
- ⚖️ Supported models:
  - GPT-4.1 ("gpt-4.1")
  - GPT-4o-mini ("gpt-4o-mini")
  - Claude 3.7 Sonnet ("claude-3.7")
  - Claude 3.5 Haiku ("claude-3.5")
- ⭐ Update checker built-in
- ⚖️ 100% local and privacy-respecting

---

## Installation

```bash
pip install git+https://github.com/immanuel-peter/localrag.git
```

Make sure you have Python 3.8+ installed.

---

## Quickstart

### 1. Configure API Keys

```bash
localrag config
```

You'll be prompted to set your OpenAI and Anthropic API keys.

### 2. Start a New Chat

```bash
localrag run gpt-4.1
```

or use a supported alias like `gpt-4o-mini`.

```bash
localrag run claude-3.7
```

### 3. Chat Commands

Inside a chat session, you can type:

| Command           | Action                           |
| :---------------- | :------------------------------- |
| `\save`           | Save chat as favorite            |
| `\clear`          | Clear current chat               |
| `\switch <model>` | Switch model if no messages sent |
| `\quit`           | Exit LocalRAG                    |
| `\help`           | Show available commands          |

### 4. View Saved Chats

```bash
localrag saved
```

Continue chatting by selecting the chat number:

```bash
localrag saved -c 2
```

### 5. Update LocalRAG

```bash
localrag update
```

---

## Persistent Storage

Everything is stored locally at:

```
~/.localrag/
├── chats/             # Individual chat JSON files
├── vector_store.faiss # FAISS index
├── vector_store.json  # Metadata (chat IDs)
├── config.json        # API keys and default model
```

**LocalRAG never sends chat history to any server.**

---

## How It Works

- 🔹 Each message (user and assistant) is embedded into a vector database (FAISS).
- 🔹 When a user types a new message, LocalRAG queries past messages for relevant context.
- 🔹 The retrieved context is prepended into the new prompt to the LLM.
- 🔹 Infinite memory means smarter conversations over time.

---

## Supported Models

Run:

```bash
localrag models
```

Currently supported:

| Alias         | Full Name                | Provider  |
| :------------ | :----------------------- | :-------- |
| `gpt-4.1`     | gpt-4.1                  | OpenAI    |
| `gpt-4o-mini` | gpt-4o-mini              | OpenAI    |
| `claude-3.7`  | claude-3-7-sonnet-latest | Anthropic |
| `claude-3.5`  | claude-3-5-haiku-latest  | Anthropic |

---

## Contributing

Contributions are welcome! 🚀

If you want to:

- Add support for more LLMs
- Improve vector search and RAG
- Add CLI features or slash commands
- Enhance performance and UX

please submit a Pull Request.

### How to Contribute

1. Fork this repo
2. Create a new branch: `git checkout -b my-feature`
3. Make your changes
4. Submit a PR describing what you added or improved
5. Keep PRs focused and modular!

## License

MIT License.

Made by Immanuel Peter.

---

## Future Ideas

- Smarter context window sizing
- Session-based summaries
- Custom RAG pipelines
- Plugin system

Stay tuned!

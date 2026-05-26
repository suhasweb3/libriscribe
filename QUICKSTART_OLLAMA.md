# 🚀 Quick Start with Ollama (5 Minutes to Free AI Writing!)

Get LibriScribe running with free local AI in just 5 minutes!

## Step 1: Install Ollama (2 minutes)

### Windows
Download and run: https://ollama.com/download/windows

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Step 2: Download a Model (2 minutes)

```bash
# Recommended for most users (2GB download)
ollama pull llama3.2

# Or for better quality if you have 16GB+ RAM (4.7GB download)
ollama pull llama3.1:8b
```

## Step 3: Install LibriScribe (1 minute)

```bash
git clone https://github.com/guerra2fernando/libriscribe.git
cd libriscribe
pip install -e .
```

## Step 4: Configure (30 seconds)

Create a `.env` file:

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Step 5: Start Writing! (Now!)

```bash
libriscribe start
```

When prompted, select **ollama** as your AI model.

## 🎉 That's It!

You now have a completely free, unlimited AI writing assistant running locally on your computer!

### What's Next?

1. **Create your first book**: Follow the interactive prompts
2. **Try different models**: `ollama pull mistral` for creative writing
3. **Read the full guide**: Check out [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for advanced tips

### Need Help?

- **Ollama not working?** Run `ollama serve` in a terminal
- **Model not found?** Run `ollama list` to see installed models
- **Slow generation?** Try a smaller model like `llama3.2`

---

**Happy Writing! 📚✨**

No API keys. No costs. No limits. Just you and your creativity!

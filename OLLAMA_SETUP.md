# 🦙 Using Ollama with LibriScribe (FREE Local AI!)

LibriScribe now supports **Ollama**, allowing you to run powerful AI models locally on your computer **completely free** - no API keys required!

## 🌟 Why Use Ollama?

- ✅ **100% Free** - No API costs or subscriptions
- ✅ **Privacy** - Your data never leaves your computer
- ✅ **No Rate Limits** - Generate as much content as you want
- ✅ **Offline Capable** - Works without internet (after model download)
- ✅ **Fast** - Local inference can be faster than API calls

## 📋 Prerequisites

- **RAM**: At least 8GB (16GB+ recommended for larger models)
- **Storage**: 4-10GB per model
- **OS**: Windows, macOS, or Linux

## 🚀 Installation Steps

### 1. Install Ollama

#### Windows
```bash
# Download and run the installer from:
https://ollama.com/download/windows
```

#### macOS
```bash
# Download and run the installer from:
https://ollama.com/download/mac

# Or use Homebrew:
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Start Ollama Service

After installation, Ollama runs as a background service automatically. You can verify it's running:

```bash
ollama --version
```

### 3. Download a Model

Choose a model based on your hardware:

#### Recommended Models for LibriScribe

**For 8GB RAM:**
```bash
ollama pull llama3.2
```

**For 16GB+ RAM (Better Quality):**
```bash
ollama pull llama3.1:8b
# or
ollama pull mistral
```

**For 32GB+ RAM (Best Quality):**
```bash
ollama pull llama3.1:70b
# or
ollama pull mixtral:8x7b
```

**Specialized Models:**
```bash
# For creative writing
ollama pull neural-chat

# For technical/factual content
ollama pull codellama
```

### 4. Configure LibriScribe

Create or edit your `.env` file in the LibriScribe root directory:

```bash
# Ollama Configuration (Local, Free - No API Key Required!)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

**Change `OLLAMA_MODEL` to match the model you downloaded.**

### 5. Test Your Setup

```bash
# Test Ollama directly
ollama run llama3.2 "Write a short story opening."

# If that works, you're ready to use LibriScribe!
```

## 🎯 Using Ollama with LibriScribe

### Start LibriScribe

```bash
libriscribe start
```

### Select Ollama

When prompted to select an AI model, choose **ollama** from the list. It will always be available since it doesn't require an API key!

```
🤖 Select your preferred AI model:
1. ollama
2. openai
3. claude
...
```

## ⚙️ Advanced Configuration

### Change the Model

You can switch models anytime by editing your `.env` file:

```bash
# Use a different model
OLLAMA_MODEL=mistral

# Or use a specific version
OLLAMA_MODEL=llama3.1:8b
```

### Custom Ollama Server

If you're running Ollama on a different machine or port:

```bash
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

### Performance Tuning

For better performance, you can adjust Ollama's settings:

```bash
# Set GPU layers (if you have a GPU)
ollama run llama3.2 --gpu-layers 35

# Adjust context window
ollama run llama3.2 --ctx-size 4096
```

## 📊 Model Comparison

| Model | Size | RAM Needed | Speed | Quality | Best For |
|-------|------|------------|-------|---------|----------|
| llama3.2 | 2GB | 8GB | ⚡⚡⚡ | ⭐⭐⭐ | Quick drafts |
| llama3.1:8b | 4.7GB | 16GB | ⚡⚡ | ⭐⭐⭐⭐ | Balanced |
| mistral | 4.1GB | 16GB | ⚡⚡ | ⭐⭐⭐⭐ | Creative writing |
| llama3.1:70b | 40GB | 64GB | ⚡ | ⭐⭐⭐⭐⭐ | Best quality |
| mixtral:8x7b | 26GB | 48GB | ⚡ | ⭐⭐⭐⭐⭐ | Technical content |

## 🔧 Troubleshooting

### Ollama Not Found

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it manually (Linux/Mac)
ollama serve

# Windows: Restart the Ollama service from Services
```

### Model Not Found Error

```bash
# List installed models
ollama list

# Pull the model if missing
ollama pull llama3.2
```

### Out of Memory

- Try a smaller model (llama3.2 instead of llama3.1:70b)
- Close other applications
- Reduce context window in Ollama settings

### Slow Generation

- Use a smaller model
- Enable GPU acceleration if available
- Increase RAM allocation

### Connection Refused

```bash
# Check if Ollama is running
ollama ps

# Restart Ollama service
# Windows: Services → Ollama → Restart
# Mac/Linux: killall ollama && ollama serve
```

## 💡 Tips for Best Results

1. **Start Small**: Begin with `llama3.2` to test, then upgrade to larger models
2. **Be Patient**: First generation after starting Ollama may be slower
3. **Use Specific Prompts**: More detailed descriptions = better output
4. **Iterate**: Generate multiple versions and pick the best
5. **Mix Models**: Use Ollama for drafts, then polish with cloud APIs if needed

## 🆚 Ollama vs Cloud APIs

### Ollama Advantages
- ✅ Free unlimited usage
- ✅ Complete privacy
- ✅ No internet required
- ✅ No rate limits

### Cloud API Advantages
- ✅ No local hardware requirements
- ✅ Access to latest models immediately
- ✅ Consistent performance
- ✅ No setup needed

**Recommendation**: Use Ollama for drafting and experimentation, then optionally use cloud APIs for final polish if needed.

## 📚 Additional Resources

- [Ollama Official Documentation](https://github.com/ollama/ollama)
- [Ollama Model Library](https://ollama.com/library)
- [LibriScribe Documentation](https://guerra2fernando.github.io/libriscribe/)

## 🤝 Community Models

Explore community-created models optimized for specific tasks:

```bash
# Browse available models
ollama list

# Search for models
ollama search writing
```

---

**Happy Writing! 📚✨**

If you encounter any issues, please open an issue on the [LibriScribe GitHub repository](https://github.com/guerra2fernando/libriscribe/issues).

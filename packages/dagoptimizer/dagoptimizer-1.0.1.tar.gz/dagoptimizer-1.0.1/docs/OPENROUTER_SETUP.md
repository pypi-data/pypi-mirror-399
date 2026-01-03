# 🚀 OpenRouter Setup Guide

## ✨ What is OpenRouter?

OpenRouter gives you access to **multiple AI vision models** via one simple API, including:
- **FREE** models (Google Gemini 2.0 Flash)
- Premium models (Claude, GPT-4, etc.)

## 🎯 Quick Setup (5 minutes)

### Step 1: Get Your FREE API Key

1. Go to: **https://openrouter.ai/keys**
2. Sign up (free, no credit card required)
3. Click "Create Key"
4. Copy your API key (starts with `sk-or-v1-...`)

### Step 2: Set Environment Variable

**Windows (cmd):**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

**For permanent setup (Windows):**
1. Search "Environment Variables" in Start menu
2. Click "Environment Variables"
3. Under "User variables", click "New"
4. Variable name: `OPENROUTER_API_KEY`
5. Variable value: `sk-or-v1-your-key-here`
6. Click OK

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Add to `.bashrc` or `.zshrc` for permanent:**
```bash
echo 'export OPENROUTER_API_KEY=sk-or-v1-your-key-here' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: (Optional) Choose Model

**Default:** `google/gemini-2.0-flash-exp:free` (FREE!)

**To use different model:**
```cmd
set OPENROUTER_MODEL=google/gemini-flash-1.5
```

### Step 4: Restart Backend

```cmd
cd backend
python main.py
```

### Step 5: Test It!

1. Open app: http://localhost:5173
2. Click "Upload Image" tab
3. Drop your DAG image
4. Watch it extract! ✨

---

## 🤖 Available Models

### FREE Tier (Recommended!)

| Model | Cost | Speed | Quality |
|-------|------|-------|---------|
| `google/gemini-2.0-flash-exp:free` | **FREE** | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Excellent |

### Paid Tier (Better Quality)

| Model | Cost/Image | Speed | Quality |
|-------|------------|-------|---------|
| `google/gemini-flash-1.5` | $0.000019 | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ Best |
| `anthropic/claude-3-haiku` | $0.0004 | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Excellent |
| `openai/gpt-4o-mini` | $0.0015 | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Best |
| `openai/gpt-4o` | $0.005 | ⚡ Slower | ⭐⭐⭐⭐⭐ Ultimate |

### How to Change Model

```cmd
# Set model before starting backend
set OPENROUTER_MODEL=anthropic/claude-3-haiku

# Start backend
cd backend
python main.py
```

---

## 🔍 Verify Setup

### Check if API key is set:

**Windows (cmd):**
```cmd
echo %OPENROUTER_API_KEY%
```

**Windows (PowerShell):**
```powershell
echo $env:OPENROUTER_API_KEY
```

**Linux/Mac:**
```bash
echo $OPENROUTER_API_KEY
```

### Check backend status:

1. Start backend: `python main.py`
2. Visit: http://localhost:8000/api/image-extraction/status
3. Should see: `"image_extraction_available": true`

---

## 📊 What You Get

### With FREE tier:
- ✅ Unlimited image analysis
- ✅ Google Gemini 2.0 Flash model
- ✅ Fast processing (2-5 seconds)
- ✅ No credit card required
- ✅ No expiration

### If you upgrade:
- ⭐ Access to Claude, GPT-4, and more
- ⭐ Better accuracy on complex graphs
- ⭐ Priority processing
- ⭐ Pay-as-you-go pricing

---

## ❓ Troubleshooting

### Error: "OpenRouter API key required"

**Solution:**
```cmd
# 1. Set the API key
set OPENROUTER_API_KEY=your-key-here

# 2. Restart backend
cd backend
python main.py
```

### Error: "API returned 401 Unauthorized"

**Cause:** Invalid API key

**Solution:**
1. Check your key at: https://openrouter.ai/keys
2. Copy the full key (including `sk-or-v1-`)
3. Set it again:
```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-full-key
```

### Error: "API returned 429 Too Many Requests"

**Cause:** Rate limit exceeded (rare on free tier)

**Solution:**
- Wait 1 minute and try again
- Or upgrade to paid tier for higher limits

### Backend doesn't see the API key

**Solution for Windows:**
```cmd
# Set in current session
set OPENROUTER_API_KEY=your-key

# Verify
echo %OPENROUTER_API_KEY%

# Start backend in SAME terminal
cd backend
python main.py
```

**Important:** The backend must be started in the same terminal where you set the variable!

---

## 💡 Pro Tips

### 1. Start with FREE model

Use `google/gemini-2.0-flash-exp:free` first - it's great for most use cases!

### 2. Test with simple images first

Upload a clear, simple DAG drawing to test the setup.

### 3. Check terminal output

Backend shows detailed logs of the extraction process:
```
🤖 Starting AI extraction with OpenRouter...
🔑 OpenRouter API key found
🤖 Using model: google/gemini-2.0-flash-exp:free
✅ Extraction completed!
📊 Extracted: Nodes: ['A', 'B', 'C'], Edges: 2
```

### 4. Monitor usage

Check your usage at: https://openrouter.ai/usage

### 5. Try different models

If extraction quality isn't good, try:
```cmd
set OPENROUTER_MODEL=anthropic/claude-3-haiku
```

---

## 🎉 You're All Set!

Now you can:
1. ✅ Upload any DAG image
2. ✅ AI extracts nodes and edges automatically
3. ✅ Preview interactive graph
4. ✅ Optimize the DAG
5. ✅ Export to Neo4j

**Happy graphing!** 📊✨

---

## 📚 More Info

- **OpenRouter Docs:** https://openrouter.ai/docs
- **Available Models:** https://openrouter.ai/models
- **Pricing:** https://openrouter.ai/pricing
- **Dashboard:** https://openrouter.ai/dashboard

---

## 🆘 Still Need Help?

1. Check backend terminal for error messages
2. Check browser console (F12) for frontend errors
3. Verify API key is set: `echo %OPENROUTER_API_KEY%`
4. Make sure backend is running
5. Try the FREE model first

**Common Issue Checklist:**
- [ ] API key is set in environment
- [ ] Backend restarted after setting key
- [ ] Terminal shows "OpenRouter API key found"
- [ ] Model name is correct
- [ ] Internet connection is working


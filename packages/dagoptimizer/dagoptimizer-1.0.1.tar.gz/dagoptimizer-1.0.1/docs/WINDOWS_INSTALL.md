# 🪟 Windows Installation Guide

Quick guide for installing the DAG Optimizer on Windows.

## ⚡ Quick Install (No C++ Compiler Needed)

The app now works **without** requiring Visual Studio Build Tools!

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

✅ **If you see warnings about `pygraphviz`, that's OK!** The app will work fine without it.

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 3: Start the Application

Open two terminals and run:

**Terminal 1:**
```bash
cd backend
python main.py
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```

Then open: **http://localhost:5173**

---

## 🎯 About pygraphviz (Optional)

### What is it?
`pygraphviz` is an optional package that provides better graph layouts using Graphviz.

### Do I need it?
**No!** The app works perfectly without it. It will use NetworkX's spring layout instead.

### If you still want it:

#### Option 1: Install Graphviz Binary
1. Download Graphviz: https://graphviz.org/download/
2. Install and add to PATH
3. Then try: `pip install pygraphviz`

#### Option 2: Install Visual Studio Build Tools
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Then try: `pip install pygraphviz`

#### Option 3: Use Without It
Just skip it! The app will automatically use an alternative layout algorithm.

---

## 🐛 Common Issues

### "pip: command not found"
```bash
# Use python -m pip instead
python -m pip install -r backend/requirements.txt
```

### "npm: command not found"
Install Node.js from: https://nodejs.org/

### Port already in use
Kill the process or use different ports:
```bash
# Backend
uvicorn main:app --reload --port 8001

# Frontend auto-detects next available port
```

---

## ✅ Verify Installation

Run this to check everything:
```bash
verify_setup.bat
```

---

## 🎉 You're Ready!

Once installed, just run:
```bash
start_all.bat
```

And enjoy your beautiful DAG optimizer at **http://localhost:5173**! 🚀


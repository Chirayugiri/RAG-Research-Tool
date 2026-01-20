# Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Make sure your `.env` file in the root directory has:
```env
PINECONE_API_KEY=your_key_here
PINECONE_INDEX_NAME=news-index
EDENAI_API_KEY=your_key_here
CHAT_GROQ_API_KEY=your_key_here
```

### 3. Start the Application

**Option A: Using start scripts (recommended)**

Terminal 1 (Backend):
```bash
cd backend
./start.sh
```

Terminal 2 (Frontend):
```bash
cd frontend
./start.sh
```

**Option B: Manual start**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### 4. Open the Application

Visit **http://localhost:5173** in your browser

---

## 📝 Usage

1. **Add URLs**: In the sidebar, enter 1-10 news article URLs
2. **Process**: Click "🚀 Process URLs" and wait ~10-30 seconds
3. **Ask Questions**: Type questions in the input box at the bottom
4. **View Answers**: See AI-generated responses with source citations
5. **Expand Sources**: Click source cards to see article excerpts

---

## 🎨 UI Features

- **Dark Mode**: Click moon/sun icon in header
- **Clear Index**: Click trash icon to delete all documents
- **Collapse Sidebar**: Click arrow to hide/show URL panel
- **Auto-scroll**: Chat automatically scrolls to new messages
- **Keyboard Shortcuts**:
  - Enter: Send message
  - Shift+Enter: New line in message

---

## 🔧 Troubleshooting

### Backend won't start
- Check `.env` file exists with all API keys
- Verify virtual environment is activated
- Run `pip install -r requirements.txt` again

### Frontend won't start
- Check `frontend/.env` exists (should have `VITE_API_URL=http://localhost:8000`)
- Run `npm install` again
- Clear node_modules: `rm -rf node_modules && npm install`

### CORS errors
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `frontend/.env`
- Restart both servers

### "No documents processed" error
- Make sure you clicked "Process URLs" and waited for completion
- Check backend terminal for errors
- Verify API keys are valid

---

## 📚 More Information

See [README.md](file:///home/chirayu/All%20Files/Projects/Python%20Projects/RAG-News-Tool/README.md) for complete documentation.

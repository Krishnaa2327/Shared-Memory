# 🧠 Universal AI Memory System

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)
![Node](https://img.shields.io/badge/node-18+-brightgreen.svg)

**Share context seamlessly across Claude, ChatGPT, and Gemini**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## 🎯 Problem Statement

Ever wished your AI assistants could remember conversations across platforms? Tired of repeating context when switching between Claude, ChatGPT, and Gemini?

**Universal AI Memory System** solves this by creating a shared memory layer that allows multiple AI assistants to access the same contextual information, eliminating repetitive explanations and enabling true multi-AI workflows.

---

## ✨ Features

### 🔄 **Cross-Platform Integration**
- **Claude Desktop**: Native MCP (Model Context Protocol) integration
- **ChatGPT**: Custom GPT with Actions API
- **Gemini**: Native MCP support via Google GenAI SDK
- **VS Code/Cursor**: Direct IDE integration for development workflows

### 💾 **Persistent Storage**
- SQLite database with Render persistent disk storage
- Survives server restarts and redeployments
- Full CRUD operations (Create, Read, Update, Delete)
- Export/Import functionality for backups

### 🚀 **Production Ready**
- RESTful API built with FastAPI
- Deployed on Render with automatic scaling
- CORS enabled for web clients
- API key authentication support

### 🎨 **Developer Friendly**
- Comprehensive OpenAPI documentation
- TypeScript extensions for IDEs
- Python clients with function calling
- Node.js MCP server implementation

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     Client Layer                           │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   Claude     │   ChatGPT    │   Gemini     │   VS Code     │
│   Desktop    │  Custom GPT  │   API        │   Extension   │
│   (MCP)      │  (Actions)   │   (MCP)      │  (TypeScript) │
└──────┬───────┴──────┬───────┴──────┬───────┴───────┬───────┘
       │              │              │               │
       └──────────────┼──────────────┼───────────────┘
                      │              │
         ┌────────────▼──────────────▼────────────┐
         │      Render Cloud (Production)         │
         │  ┌──────────────────────────────────┐  │
         │  │   FastAPI Backend                │  │
         │  │   • RESTful API                  │  │
         │  │   • CRUD Operations              │  │
         │  │   • Authentication               │  │
         │  └────────────┬─────────────────────┘  │
         │               │                        │
         │  ┌────────────▼─────────────────────┐  │
         │  │   SQLite Database                │  │
         │  │   • Persistent Disk (1GB Free)   │  │
         │  │   • Indexed Queries              │  │
         │  │   • Backup/Export                │  │
         │  └──────────────────────────────────┘  │
         └────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** for backend
- **Node.js 18+** for MCP clients
- **API Keys**: 
  - [Gemini API Key](https://aistudio.google.com/app/apikey)
  - [ChatGPT Plus](https://chat.openai.com/gpts) (for Custom GPTs)
  - [Claude Desktop](https://claude.ai/download) (for MCP)

### Installation

```bash
# Clone the repository
git clone https://github.com/Krishnaa2327/Shared-Memory.git
cd Shared-Memory

# Install backend dependencies
pip install -r requirements.txt

# Install MCP client dependencies
npm install

# Set environment variables
export GEMINI_API_KEY="your-gemini-key"
export API_KEY="your-backend-api-key"  # Optional for security
```

### Run Locally

```bash
# Start the backend
python backend.py

# In another terminal, test the MCP server
node claude-client.js #test claude desktop using this command but setup claude config file first give below

# For Gemini integration
node gemini-chat.js
```

### Deploy to Render

1. Fork this repository
2. Create a new Web Service on [Render](https://render.com)
3. Connect your GitHub repository
4. Add persistent disk: `/data` (1GB free)
5. Set environment variable: `DATABASE_PATH=/data/memories.db`
6. Deploy! 🚀

---

## 📖 Usage

### Claude Desktop Integration

**1. Configure MCP Server**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sharedMemory": {
      "command": "node",
      "args": ["/absolute/path/to/claude-client.js"]
    }
  }
}
```

**2. Restart Claude Desktop**

**3. Test it:**
```
You: Remember that I prefer TypeScript for all projects
Claude: [Stores in memory automatically]

You: What do I prefer for projects?
Claude: You prefer TypeScript for all projects.
```

---

### ChatGPT Custom GPT Setup

**1. Create Custom GPT**
- Go to [ChatGPT GPTs Editor](https://chat.openai.com/gpts/editor)
- Click "Create a GPT"

**2. Add Actions**
- Copy the OpenAPI schema from `openapi.yaml`
- Replace `https://your-app.onrender.com` with your Render URL
- Paste into Actions configuration

**3. Test it:**
```
You: Remember: I love Python for AI projects
ChatGPT: [Calls API to store memory]

You: Search for programming preferences
ChatGPT: [Retrieves from shared memory]
```

---

### Gemini MCP Integration

**1. Set API Key**
```bash
export GEMINI_API_KEY="your-key-from-google-ai-studio"
```

**2. Run Gemini Client**
```bash
node gemini-chat.js
```

**3. Chat with Memory:**
```
You: Remember that I prefer dark mode
Gemini: [Stores via MCP automatically]

You: What's my UI preference?
Gemini: You prefer dark mode.
```

---

### API Endpoints

|     Endpoint          | Method |               Description                   |
|-----------------------|--------|---------------------------------------------|
| `/memory/add`         | POST   | Store a new memory                          |
| `/memory/search`      | GET    | Search memories by query                    |
| `/memory/list`        | GET    | List all memories (optional project filter) |
| `/memory/update/{id}` | PUT    | Update existing memory                      |
| `/memory/delete/{id}` | DELETE | Delete a memory                             |
| `/memory/stats`       | GET    | Get statistics and analytics                |
| `/memory/export`      | GET    | Export all memories as JSON                 |
| `/memory/import`      | POST   | Import memories from JSON                   |

**Example API Call:**
```bash
# Add a memory
curl -X POST https://your-app.onrender.com/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "project": "my-project",
    "content": "User prefers React over Vue",
    "tags": ["preferences", "frontend"]
  }'

# Search memories
curl "https://your-app.onrender.com/memory/search?query=React&limit=10"
```

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Lightweight, serverless database
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### MCP Integration
- **Node.js** - MCP server runtime
- **@modelcontextprotocol/sdk** - Official MCP SDK
- **@google/genai** - Google Gemini SDK with MCP support

### Frontend/Extensions
- **TypeScript** - VS Code/Cursor extensions
- **OpenAPI 3.1** - ChatGPT Actions schema
- **React** - Web dashboard (coming soon)

### Deployment
- **Render** - Cloud hosting with persistent storage
- **Docker** - Containerization (optional)
- **GitHub Actions** - CI/CD (optional)

---

## 📊 Project Structure

```
universal-ai-memory/
├── backend.py                 # FastAPI backend with SQLite
├── claude-client.js                  # MCP client for backend integration
├── gemini-chat.js            # Gemini MCP client
├── openapi.yaml              # OpenAPI schema for ChatGPT
├── requirements.txt          # Python dependencies
├── package.json              # Node.js dependencies
├── render.yaml               # Render deployment config
├── vscode-extension/         # VS Code extension source
│   ├── src/
│   │   └── extension.ts
│   └── package.json
├── docs/                     # Documentation
│   ├── CHATGPT_SETUP.md
│   ├── GEMINI_SETUP.md
│   └── CLAUDE_SETUP.md
└── README.md                 # This file
```

---

## 🎯 Use Cases

### 1. **Multi-AI Research Workflow**
```
Claude → Analyzes academic paper
ChatGPT → Remembers key findings
Gemini → Generates summary using shared context
```

### 2. **Development Assistant**
```
VS Code → Store coding preferences
Claude → Suggests code following your style
Cursor → Accesses same preferences
```

### 3. **Personal Knowledge Base**
```
Morning: Add tasks to memory via ChatGPT
Afternoon: Claude reminds you of priorities
Evening: Gemini helps review completed work
```

### 4. **Team Collaboration**
```
Team Member A → Adds project decisions
Team Member B → Retrieves context in Claude
Team Member C → References in ChatGPT
```

---

## 🔒 Security Best Practices

### API Key Authentication

**Backend (backend.py):**
```python
from fastapi import Header, HTTPException, Depends

API_KEY = os.getenv('API_KEY', 'your-secret-key')

async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.post("/memory/add", dependencies=[Depends(verify_api_key)])
async def add_memory(memory: Memory):
    # ... your code
```

**Client:**
```javascript
const response = await axios.post(url, data, {
    headers: { 'X-API-Key': process.env.API_KEY }
});
```

### Environment Variables

Never commit API keys! Use `.env` file:

```bash
# .env
GEMINI_API_KEY=your-gemini-key
API_KEY=your-backend-api-key
DATABASE_PATH=/data/memories.db
```

Add to `.gitignore`:
```
.env
*.db
node_modules/
__pycache__/
```

---

## 📈 Performance & Limits

### Free Tier Limits

|     Service      |     Free Tier      |               Limit                   |
|------------------|--------------------|---------------------------------------|
| **Render**       | 750 hours/month    | Service sleeps after 15min inactivity |
| **Render Disk**  | 1 GB               | Persistent storage                    |
| **Gemini API**   | 1,500 requests/day | 15 RPM                                |
| **ChatGPT Plus** | Unlimited          | Requires $20/month subscription       |

### Database Performance

- **SQLite handles**: ~100k memories efficiently
- **Query speed**: <50ms for indexed searches
- **Storage**: ~1KB per memory (1GB = ~1M memories)

### Scaling Options

When you outgrow free tier:

1. **Render Pro**: $7/month for PostgreSQL
2. **Supabase**: Free PostgreSQL with 500MB
3. **Railway**: $5 credit/month, pay-as-you-go

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 1. **Report Bugs**
Open an issue with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

### 2. **Suggest Features**
Open an issue with:
- Use case description
- Proposed solution
- Alternative approaches considered

### 3. **Submit Pull Requests**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/Krishnaa2327/Shared-Memory.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dev dependencies
pip install -r requirements-dev.txt
npm install --save-dev

# Run tests
pytest
npm test

# Format code
black .
prettier --write "**/*.js"
```

---

## 📝 Roadmap

### ✅ Completed
- [x] FastAPI backend with SQLite
- [x] MCP server for Claude Desktop
- [x] ChatGPT Custom GPT integration
- [x] Gemini MCP native support
- [x] Render deployment with persistent storage
- [x] VS Code/Cursor extensions

### 🚧 In Progress
- [ ] Web dashboard UI
- [ ] PostgreSQL migration guide
- [ ] Docker containerization
- [ ] Comprehensive test suite

### 🔮 Future Plans
- [ ] Mobile app (iOS/Android)
- [ ] Chrome extension
- [ ] Slack/Discord bots
- [ ] Vector embeddings for semantic search
- [ ] Multi-user support with permissions
- [ ] Analytics dashboard
- [ ] Notion/Obsidian integration

---

## 🐛 Troubleshooting

### Issue: "Connection refused"
**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/

# Check Render deployment
curl https://your-app.onrender.com/
```

### Issue: "Database is locked"
**Solution:** SQLite doesn't handle many concurrent writes well.
```python
# Increase timeout
conn = sqlite3.connect(DB_PATH, timeout=30.0)

# Or migrate to PostgreSQL for production
```

### Issue: Claude doesn't see MCP tools
**Solution:**
1. Verify config file location: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Use absolute path to MCP server
3. Restart Claude Desktop completely
4. Check logs: Help → Show Logs

### Issue: ChatGPT "Failed to load action"
**Solution:**
1. Verify server URL in OpenAPI schema
2. Test endpoint: `curl https://your-app.onrender.com/`
3. Check YAML syntax: https://www.yamllint.com/
4. Ensure API is public or add authentication

### Issue: Gemini "API key not valid"
**Solution:**
1. Get fresh key: https://aistudio.google.com/app/apikey
2. Check environment variable: `echo $GEMINI_API_KEY`
3. Verify no extra spaces in key

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for Claude and MCP protocol
- **OpenAI** for ChatGPT and Actions API
- **Google** for Gemini and MCP support in GenAI SDK
- **Render** for excellent cloud hosting
- **FastAPI** community for amazing documentation

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/universal-ai-memory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/universal-ai-memory/discussions)
- **Email**: krishnachaudhari0205@gmail.com

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Built with ❤️ for the AI community**

[⬆ Back to Top](#-universal-ai-memory-system)

</div>
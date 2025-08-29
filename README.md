# 🤖 LOCAL LLM Agent v2.0.0 – Sleek Web UI + Powerful CLI, right on your machine.

A production-ready AI assistant with tools, memory, and a stunning modern web interface that works LOCALLY on your device!

**Created by: [Syed Wamiq](https://github.com/syedwam7q)**

---

## ✨ Features

**AI-Agents, Right on Your Device** - Run and collaborate with intelligent agents locally, directly on your system:
- 🧠  **Multi-LLM Support** - OpenAI GPT models with extensible provider system
- 🛠️  **12 Built-in Tools** - Search, computation, file operations, data analysis, all local operations
- 💾  **Persistent Memory** - SQLite-based conversation storage
- 🌐  **Modern Web UI** - ChatGPT-inspired interface with real-time streaming
- 💻  **Beautiful CLI** - Rich formatting with interactive chat interface
- 🔧  **Extensible** - Easy to add new tools and capabilities
- ⚡  **Dual Interface** - Choose between modern web UI or efficient CLI

## 🚀 Quick Start

### 1. Clone & Setup
```bash
# Clone the repository
git clone https://github.com/syedwam7q/local-llm-agent-CLI-and-UI.git
cd local-llm-agent-CLI-and-UI

# Run the automated setup script
./setup.sh
```

**The setup script automatically:**
- ✅ Checks Python 3.8+ installation
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Creates necessary directories
- ✅ Sets up environment configuration
- ✅ Makes scripts executable
- ✅ Tests the installation

**Dependencies automatically installed:**
- Core: `openai`, `anthropic`
- CLI: `rich`, `typer`, `prompt-toolkit`
- Web: `fastapi`, `uvicorn`, `websockets`
- Tools: `requests`, `beautifulsoup4`, `tavily-python`
- Data: `pandas`, `numpy`, `matplotlib`, `sqlalchemy`
- Files: `PyPDF2`, `python-docx`, `openpyxl`

### 2. Configure API Keys
```bash
# Edit the .env file with your API keys
nano .env

# Required:
OPENAI_API_KEY=your_openai_key_here

# Optional (for web search):
TAVILY_API_KEY=your_tavily_key_here
```

### 3. Start the Application
```bash
# Modern Web Interface (Recommended)
./start_modern_ui.sh

# Traditional CLI
./run_chat.sh

# Or manually
source venv/bin/activate
python src/main.py chat --web-ui  # Modern web interface
python src/main.py chat           # CLI interface
```

### 4. Access the Modern Web Interface
Open your browser to: **http://localhost:8000**

## 🎨 Modern Web Interface Features

### ChatGPT/Gemini-Inspired Design
- **🌟 Glassmorphism UI** - Modern glass-like effects with blur and transparency
- **🎭 Smooth Animations** - Polished transitions and micro-interactions
- **🌙 Dark Theme** - Professional dark design optimized for extended use
- **📱 Fully Responsive** - Perfect experience on desktop, tablet, and mobile

### Real-Time Communication
- **⚡ WebSocket Streaming** - See AI responses as they're generated in real-time
- **🔄 Live Connection Status** - Always know your connection state
- **💬 Typing Indicators** - Visual feedback when AI is thinking

### File Management
- **📎 Drag & Drop Upload** - Simply drag files into the interface
- **📄 Multi-Format Support** - TXT, JSON, CSV, PDF, DOCX, XLSX files
- **🔍 Content Preview** - See file contents before processing
- **📊 Smart Processing** - Automatic content extraction and analysis

### Session Management
- **💾 Persistent Sessions** - All conversations saved automatically
- **🔄 Session Switching** - Seamlessly switch between multiple chats
- **✏️ Editable Titles** - Rename conversations for better organization
- **🗑️ Session Cleanup** - Delete unwanted conversations

### Advanced Features
- **📝 Markdown Rendering** - Rich text formatting with syntax highlighting
- **🛠️ Tool Integration** - Visual feedback when AI uses tools
- **❌ Error Handling** - User-friendly error messages and recovery
- **⚡ Performance Optimized** - Smooth interactions even with long conversations

## 🛠️ Available Tools

### Search & Web
- **websearch** - Real-time web search with Tavily API
- **webscrape** - Extract content from web pages
- **mocksearch** - Fallback search for testing

### Computation
- **calculator** - Mathematical expressions and calculations
- **codeexecutor** - Safe Python code execution
- **unitconverter** - Convert between units of measurement

### File Operations
- **filereader** - Read TXT, JSON, CSV, PDF, DOCX files
- **filewriter** - Write content to various file formats
- **directorylist** - Navigate and list file systems

### Data Analysis
- **dataanalysis** - Pandas-powered data analysis
- **datavisualization** - Create charts and graphs
- **jsonprocessor** - JSON data manipulation

## 📋 Commands

```bash
# Start modern web interface (Recommended)
python src/main.py chat --web-ui

# Start CLI interface
python src/main.py chat

# List all available tools
python src/main.py tools

# Show current configuration
python src/main.py settings-cmd

# Run tests
python src/main.py test

# Custom port for web UI
python src/main.py chat --web-ui --port 8001
```

## 🎯 Usage Examples

### Basic Conversation
```
💬 You: Hello! What is 25 * 17?
🤖 Assistant: Hello! 25 * 17 equals 425.

💬 You: Search for the latest AI news
🤖 Assistant: [Uses web search tool to find current AI news]

💬 You: Change the 'Author Name' to 'Syed Wamiq' in "xxx/xx/x.file" and change its file type to .docx
🤖 Assistant: [Edits the file for you and also changes its file type]

💬 You: Summarize the file "xxx/xx/x/file" and provide any key links mentioned
🤖 Assistant: [Uses file reader tool and provides comprehensive summary whilst mentioning useful links]
```

### Available Commands in Chat
- `/help` - Show available commands
- `/tools` - List all tools
- `/history` - Show conversation history
- `/clear` - Clear the screen
- `/exit` - Exit the chat

## 🏗️ Project Structure

```
llm-agent/
├── src/                    # Source code
│   ├── main.py            # CLI entry point
│   ├── config/            # Configuration management
│   │   └── settings.py    # Application settings
│   ├── core/              # Core agent logic
│   │   ├── agent.py       # Main agent implementation
│   │   ├── llm.py         # LLM provider integrations
│   │   └── memory.py      # Conversation memory
│   ├── tools/             # Tool implementations
│   │   ├── base.py        # Base tool classes
│   │   ├── computation_tools.py # Math & code execution
│   │   ├── data_tools.py  # Data analysis tools
│   │   ├── file_tools.py  # File operations
│   │   └── search_tools.py # Web search tools
│   ├── ui/                # User interfaces
│   │   ├── cli.py         # Command-line interface
│   │   ├── modern_web.py  # Modern web UI
│   │   ├── static/        # Web UI assets
│   │   └── templates/     # Web UI templates
│   └── utils/             # Utility functions
│       └── file_utils.py  # File handling utilities
├── data/                  # Data storage
│   ├── uploads/           # File upload directory
│   └── .gitkeep           # Placeholder for Git
├── logs/                  # Application logs
│   └── .gitkeep           # Placeholder for Git
├── tests/                 # Test files
│   └── test_ui.py         # UI tests
├── .github/               # GitHub templates & workflows
│   ├── ISSUE_TEMPLATE/    # Issue templates
│   ├── workflows/         # GitHub Actions
│   └── pull_request_template.md # PR template
├── requirements.txt       # Python dependencies
├── setup.sh               # One-time setup script
├── run_chat.sh            # CLI quick start script
├── start_modern_ui.sh     # Modern UI startup script
├── git-safety-check.sh    # Git safety verification
├── prepare-for-git.sh     # Git preparation script
├── LICENSE                # MIT License
├── CONTRIBUTING.md        # Contribution guidelines
├── CHANGELOG.md           # Version history
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore rules
├── .gitattributes         # Git attributes
├── .editorconfig          # Editor configuration
├── .dockerignore          # Docker ignore rules
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker configuration
└── README.md              # This file
```

## 🧪 Testing

```bash
# Run basic functionality tests
python src/main.py test

# Test individual components
python src/main.py tools    # List and verify tools
python src/main.py settings-cmd  # Check configuration

# Test web UI (start and access in browser)
python src/main.py chat --web-ui --port 8001
```

## 🐳 Docker Support

```bash
# Build image
docker build -t llm-agent .

# Run container
docker run -it --env-file .env llm-agent
```

## ⚙️ Configuration

Key settings in `.env`:

```bash
# LLM Configuration
AGENT_MODEL=gpt-4o-mini
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=4000

# API Keys
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here

# Features
ENABLE_WEB_SEARCH=true
ENABLE_CODE_EXECUTION=true
ENABLE_FILE_OPERATIONS=true

# Web UI
WEB_UI_ENABLED=true
WEB_UI_PORT=8000
```

## 🔧 Development

### Adding New Tools
1. Create tool class in `src/tools/`
2. Inherit from `BaseTool`
3. Use `@register_tool` decorator
4. Implement `execute()` method

### Adding New LLM Providers
1. Create provider class in `src/core/llm.py`
2. Inherit from `LLMProvider`
3. Implement required methods
4. Register in `LLMManager`

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🆘 Support & Troubleshooting

### Common Issues

**1. Setup Issues:**
```bash
# If setup.sh fails, try manual setup:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**2. Permission Issues (macOS/Linux):**
```bash
# Make scripts executable
chmod +x setup.sh
chmod +x start_modern_ui.sh
chmod +x run_chat.sh
```

**3. Python Version Issues:**
```bash
# Check Python version (requires 3.8+)
python3 --version

# If using older Python, install Python 3.8+
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
```

**4. API Key Issues:**
```bash
# Check your .env file has the required keys
cat .env

# Required:
OPENAI_API_KEY=your_openai_key_here

# Optional:
TAVILY_API_KEY=your_tavily_key_here
```

**5. Port Already in Use:**
```bash
# Use a different port
python src/main.py chat --web-ui --port 8001
```

**6. Dependencies Issues:**
```bash
# Reinstall all dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Getting Help

- Run `./setup.sh` for automated setup
- Run `python src/main.py --help` for CLI help
- Use `/help` command in chat interface
- Check `logs/` directory for error logs
- Review GitHub issues for common problems

---

## 🏆 **Credits**

**Created by: [Syed Wamiq](https://github.com/syedwam7q)**

This project represents a modern, production-ready AI assistant with:
- Professional CLI+UI interface
- Advanced tool integration
- Real-time streaming capabilities
- Mobile-responsive design
- Enterprise-grade architecture

**Built with ❤️ using Python, FastAPI, OpenAI, and modern web technologies.**

## 🌟 **Showcase**

The Local LLM Agent [LLA] features a completely redesigned modern interface that rivals commercial AI assistants:

- **Modern Design**: Glassmorphism effects, smooth animations, professional typography
- **Advanced Features**: File uploads, real-time streaming, markdown rendering
- **Developer Experience**: Clean code, comprehensive documentation, easy deployment
- **User Experience**: Intuitive interface, responsive design, accessibility features

**Start the enhanced UI:** `./start_modern_ui.sh` or `./run_chat.sh`

# 📰 Research Paper Blog Post Generator

A powerful AI-driven application that transforms academic research papers into engaging blog posts using LangGraph, LangChain, and Groq's language models.

## 🎯 Features

✨ **AI-Powered Generation**
- Automatic extraction and summarization of research papers
- Intelligent storytelling transformation of methodologies
- Contextual humor enhancement for readability
- Domain expert validation and structuring

🔄 **Iterative Improvement Loop**
- Feedback-based refinement process
- Tool-based node selection for targeted improvements
- Quality rating system (1-10 scale)
- Automatic workflow routing based on feedback

📊 **Comprehensive Dashboard**
- Real-time progress tracking
- Execution time monitoring
- Detailed analytics and metrics
- Multiple view tabs for different content sections

💾 **Export Options**
- Download reports as Markdown
- Export workflow state as JSON
- View detailed metadata and summaries

## 🚀 Quick Start

### Prerequisites
```bash
python >= 3.10
pip install -r requirements.txt
```

### Installation
```bash
# Navigate to the project directory
cd Blog_Post_Project

# Install required packages (if not already done)
pip install streamlit
```

### Run the Application

#### Option 1: Using Streamlit (Recommended - Web UI)
```bash
streamlit run BlogStreamApp.py
```
This will:
- Open the Streamlit application in your default browser (usually http://localhost:8501)
- Display an interactive web interface
- Provide real-time progress updates
- Allow easy download of results

#### Option 2: Terminal/Command Line
```bash
cd Blog_Post_Project
python BlogStreamApp_cli.py  # (if you want CLI version)
```

## 📋 How to Use

### Web Interface (Streamlit)

1. **Enter Research Paper**
   - Choose "ArXiv ID" (e.g., 2005.11401) or "Research Topic"
   - Provide either an ArXiv paper ID or a research topic

2. **Configure Settings** (Optional)
   - Adjust max iterations (5-20) in the sidebar
   - Default: 15 iterations for optimal balance

3. **Generate Blog Post**
   - Click "🚀 Generate Blog Post" button
   - Monitor progress with real-time status updates
   - View execution time, ratings, and iterations

4. **View & Download Results**
   - **Blog Post Tab**: Read the generated blog content
   - **Feedback Tab**: Review workflow feedback and improvement suggestions
   - **Metadata Tab**: Examine extracted information (domain, title, methodology)
   - **State Tab**: View complete workflow state as JSON
   - **Download Tab**: Export reports and states in various formats

## 🏗️ Project Architecture

```
Blog_Post_Project/
├── BlogStreamApp.py              # Main Streamlit web application
├── Agent_workflow.py             # LangGraph workflow orchestration
├── models.py                     # PaperState data model
├── Agents/                       # Individual agent nodes
│   ├── Summarization_agent.py
│   ├── Storytelling_agent.py
│   ├── Humor_agent.py
│   ├── domain_expert_structuring_node.py
│   └── Visual_Illustration_agent.py
├── ToolAgents/                   # Tool definitions
│   └── select_node_tool.py       # Node selection tool for routing
├── Helpersfunctions/             # Utility functions
│   ├── Download_ResearchPaper.py
│   ├── Extract_pdf.py
│   └── Generate_report.py
└── Generated_Reports/            # Output directory for blog posts
```

## 🔄 Workflow Pipeline

```
Input (ArXiv ID or Topic)
    ↓
Download Research Paper
    ↓
Extract PDF Content
    ↓
Summarize Text
    ↓
Domain Expert Structuring
    ↓
Storytelling Enhancement
    ↓
Humor Integration
    ↓
Report Generation
    ↓
Tool-Based Evaluation & Feedback Loop
    ├→ If Rating < 9: Revisit selected node
    └→ If Rating >= 9: End workflow
```

## 🛠️ Configuration

### Streamlit Config (`.streamlit/config.toml`)
Located in `.streamlit/config.toml`, contains:
- Color scheme customization
- Server settings
- Logger configuration

### Workflow Settings
In the **Sidebar**:
- **Max Iterations**: Control maximum refinement loops (5-20)
- Default: 15 iterations

## 📊 Output Files

Generated files are automatically saved:

```
Generated_Reports/
├── AI_Paper_Report_YYYYMMDD_HHMM.md    # Blog post markdown
└── final_state.json                     # Complete workflow state
```

## 🔧 Environment Variables

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
OPENAI_API_KEY=your_openai_api_key_here (if needed)
```

## 📈 Performance Tips

1. **Start with smaller iteration counts** (5-10) for testing
2. **ArXiv IDs are faster** than searching by topic
3. **Monitor rate limits** - Groq API has usage limits
4. **Check sidebar** for report history and statistics

## 🚨 Troubleshooting

### Port Already in Use
```bash
streamlit run BlogStreamApp.py --server.port 8502
```

### Groq API Errors
- Verify `GROQ_API_KEY` in `.env`
- Check API rate limits
- Ensure proper internet connection

### Memory Issues
- Reduce `max_iterations` in sidebar
- Close other applications
- Use smaller papers initially

## 📝 Example Usage

### Example 1: ArXiv Paper
1. Input: `2005.11401` (Vision Transformer paper)
2. Settings: Keep default 15 iterations
3. Click Generate
4. Results in ~2-5 minutes (depending on paper length)

### Example 2: Research Topic
1. Input: `Attention Mechanisms in Deep Learning`
2. System will search and download relevant paper
3. Generate blog post
4. Download as Markdown

## 🤝 Contributing

To add new features:
1. Create new agents in `Agents/`
2. Update workflow in `Agent_workflow.py`
3. Add UI components in `BlogStreamApp.py`

## 📄 License

MIT License - See LICENSE file for details

## 🙋 Support

For issues or questions:
1. Check the sidebar "Project Info" section
2. Review error messages in the warning boxes
3. Check `.env` file configuration
4. Verify API keys and rate limits

---

**Built with ❤️ using Streamlit, LangGraph & LangChain**


# ⚡ Quick Reference Card

## 🚀 Start in 30 Seconds

```powershell
cd "Blog_Post_Project"
.\run_streamlit.ps1
```

The app opens at: **http://localhost:8501**

---

## 📋 Quick Usage

| Step | Action |
|------|--------|
| 1️⃣ | Choose **ArXiv ID** or **Research Topic** |
| 2️⃣ | Enter paper ID (e.g., `2005.11401`) or topic |
| 3️⃣ | Optional: Adjust **Iterations** in sidebar (5-20) |
| 4️⃣ | Click **🚀 Generate Blog Post** |
| 5️⃣ | View results in tabs (2-10 minutes) |
| 6️⃣ | Download markdown or JSON |

---

## 🎯 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Run workflow |
| `Ctrl+C` | Stop server (terminal) |
| `Ctrl+L` | Clear console |

---

## 📊 Tab Guide

| Tab | Purpose |
|-----|---------|
| **📄 Blog Post** | Read the generated content |
| **📝 Feedback** | Check ratings & improvement notes |
| **🔍 Metadata** | View extracted paper info |
| **💾 State** | Debug workflow state (JSON) |
| **📥 Download** | Export results |

---

## ⚙️ Configuration

### Sidebar Options
- **Iterations**: 5-20 (default: 15)
- **View Reports**: See past generated reports
- **Project Info**: Framework details

### Environment (.env)
```
GROQ_API_KEY=your_key_here
HF_TOKEN=your_token_here
```

---

## 🔴 Troubleshooting

### Port in Use
```powershell
streamlit run BlogStreamApp.py --server.port 8502
```

### API Key Error
- Check `.env` file exists
- Verify `GROQ_API_KEY` is set

### Module Not Found
```powershell
pip install -r requirements.txt
```

### Slow Processing
- Use ArXiv ID (faster than topic search)
- Reduce iterations to 5-10
- Try smaller papers first

---

## 📈 Performance Typical Times

| Paper Size | Time |
|-----------|------|
| 5-10 pages | 2-3 min |
| 10-20 pages | 3-5 min |
| 20+ pages | 5-10+ min |
| Per iteration | 30-60 sec |

---

## 💾 Output Files

```
Generated_Reports/
├── AI_Paper_Report_20251112_1430.md
├── AI_Paper_Report_20251112_1445.md
└── ... (timestamped reports)

final_state.json                (latest run state)
workflow_graph.png              (workflow diagram)
```

---

## 🎨 Customization

### Change Theme Color
Edit `.streamlit/config.toml`:
```toml
primaryColor = "#FF5733"
```

### Change App Title
Edit line 3 in `BlogStreamApp.py`:
```python
page_title="Your Custom Title"
```

---

## 📚 Example ArXiv IDs

| Topic | ID |
|-------|-----|
| Vision Transformer | `2005.11401` |
| BERT | `1810.04805` |
| GPT-3 | `2005.14165` |
| Transformers | `1706.03762` |

---

## 🔗 Useful Links

- **Streamlit Docs**: https://docs.streamlit.io
- **ArXiv Papers**: https://arxiv.org
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Groq API**: https://console.groq.com

---

## ✅ Pre-Startup Checklist

- [ ] `.env` file exists with API keys
- [ ] Python 3.10+ installed
- [ ] Streamlit installed (`pip install streamlit`)
- [ ] Internet connection active
- [ ] Port 8501 not in use
- [ ] No other app instances running

---

## 💡 Pro Tips

1. **Start Small** - Use 5-10 iterations for testing
2. **Use ArXiv IDs** - Much faster than topic search
3. **Check Sidebar** - View generated reports history
4. **Export Results** - Download markdown for sharing
5. **Monitor Feedback** - Understand what LLM suggests improving

---

## 🎯 Common Tasks

### View Generated Blog Post
```
1. Wait for completion (2-10 min)
2. Click "📄 Blog Post" tab
3. Read generated markdown
4. Click "📥 Download Tab" → Download Report
```

### Check What Needs Improvement
```
1. After generation, click "📝 Feedback" tab
2. Read "Latest Feedback" section
3. Check "Next Suggested Node"
4. Review improvement suggestions
```

### Export Results
```
1. Click "📥 Download" tab
2. Click "📄 Download Report (MD)" for blog post
3. Click "📊 Download State (JSON)" for debugging
4. Files ready to share or archive
```

### Debug Workflow
```
1. Click "💾 State" tab
2. View complete JSON state
3. Check field values for debugging
4. Copy JSON to JSON debugger if needed
```

---

## 🔐 Security Notes

✅ **Safe**
- Data processed locally
- No cloud storage (except Groq API call)
- API keys stay in `.env` file

❌ **Avoid**
- Sharing `.env` file
- Committing API keys to Git
- Running untrusted scripts

---

## 📞 Quick Help

**App won't start?**
→ Check `.env` file and API keys

**Port already in use?**
→ Use `--server.port 8502`

**Report not generating?**
→ Try different paper or reduce iterations

**Need API key?**
→ https://console.groq.com

---

**🎉 Ready to generate blog posts!**

For full docs, see: `STREAMLIT_README.md` and `STREAMLIT_SETUP_GUIDE.md`

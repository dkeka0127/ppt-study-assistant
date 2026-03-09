# RAG Pipeline Integration Guide

## 🚀 RAG (Retrieval Augmented Generation) Features

Your PPT Study Assistant now includes an advanced RAG pipeline that significantly improves the accuracy and relevance of AI responses.

## ✨ New Features

### 1. **Semantic Search**
- Finds the most relevant content from your PPT based on meaning, not just keywords
- Uses sentence-transformers for high-quality text embeddings

### 2. **Intelligent Re-ranking**
- Re-ranks search results using cross-encoder models
- Ensures the most relevant information is prioritized

### 3. **Source Attribution**
- Shows which slides contributed to each answer
- Helps users verify information and study specific sections

### 4. **Dynamic Question Suggestions**
- Generates context-aware suggested questions
- Adapts based on PPT content and conversation history

### 5. **Performance Optimization**
- Embedding cache for faster repeated queries
- Efficient vector storage with ChromaDB

## 📊 How It Works

1. **Upload PPT** → Content is processed and chunked
2. **Vector Storage** → Chunks are converted to embeddings and stored in ChromaDB
3. **User Query** → Question is converted to embedding
4. **Semantic Search** → Find similar content in vector database
5. **Re-ranking** → Improve relevance with cross-encoder
6. **Context Generation** → Optimize context for LLM
7. **Response** → Generate answer with source attribution

## 🎯 Benefits

- **More Accurate Answers**: Responses based on actual PPT content
- **Better Context**: Smart selection of relevant information
- **Transparency**: See which slides provide the information
- **Scalability**: Handles large PPT files efficiently
- **Fallback Support**: Works even if RAG fails (uses traditional context)

## 📈 Status Indicators

The app shows RAG status in multiple places:

1. **Top Stats Bar**: Shows "🚀 RAG" when active, "📝 기본" in basic mode
2. **AI Tutor Tab**: Green success message when RAG is active
3. **Processing Screen**: Shows RAG initialization progress

## 🔧 Technical Details

### Components
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Re-ranking Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Vector Database**: ChromaDB (local, persistent)
- **Chunk Size**: 500 characters with 100 character overlap

### Performance
- Embedding dimension: 384
- Cache size: 1000 embeddings
- Re-ranking: Top 5 from 10 candidates
- Context limit: 4000 tokens

## 💡 Usage Tips

1. **Large PPTs**: RAG handles large files better than the basic mode
2. **Specific Questions**: Ask detailed questions for best results
3. **Source Check**: Click "📚 참고 자료" to see which slides were used
4. **Suggested Questions**: Use dynamic suggestions for better learning

## 🔍 Troubleshooting

### RAG Not Activating?
- Check console for initialization errors
- Ensure all dependencies are installed
- Verify disk space for ChromaDB storage

### Slow Performance?
- First query is slower (model loading)
- Subsequent queries use cache
- Consider reducing chunk size for very large PPTs

### API Errors?
- RAG works independently of Bedrock API
- Fallback to basic mode if API fails
- Check AWS credentials for full functionality

## 📝 Fallback Behavior

If RAG initialization fails, the app automatically falls back to:
- Traditional context-based responses
- Static suggested questions
- Original chatbot functionality

This ensures the app always works, even if advanced features are unavailable.

## 🚦 Quick Status Check

Run this to verify RAG is working:
```bash
python test_app_integration.py
```

Expected output:
- ✅ RAG initialization successful
- ✅ Documents processed: X
- ✅ Vector DB count: X
- ✅ Response generation working

## 📚 Further Development

Potential improvements:
- Multi-language support
- PDF support alongside PPT
- Conversation memory across sessions
- Advanced filtering options
- Custom embedding models
- Cloud vector database integration
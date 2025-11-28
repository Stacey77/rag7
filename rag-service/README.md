# Ragamuffin RAG Service

Multimodal Retrieval-Augmented Generation (RAG) service with Milvus vector database integration.

## Features

- **Text Embedding**: Generate and store text embeddings using sentence transformers
- **Image Embedding**: Process and embed images for multimodal search
- **Document Processing**: Support for PDFs and various document formats
- **Vector Search**: Fast similarity search using Milvus
- **Multimodal RAG**: Query across text, images, and documents

## Architecture

```
RAG Service (Port 8001)
├── Text Processing
│   ├── Embedding generation (sentence-transformers)
│   └── Text storage in Milvus
├── Image Processing
│   ├── Image encoding
│   └── Visual embedding generation
├── Document Processing
│   ├── PDF parsing
│   └── Document chunking
└── RAG Query Engine
    ├── Context retrieval
    └── Response generation
```

## API Endpoints

### Health & Info
- `GET /` - Service information
- `GET /health` - Health check

### Text Operations
- `POST /embed/text` - Embed and store text
- `POST /search/text` - Search for similar text

### Image Operations
- `POST /embed/image` - Embed and store images

### RAG Operations
- `POST /rag/query` - Multimodal RAG query

### Collection Management
- `GET /collections` - List all collections

## Usage Examples

### Embed Text
```bash
curl -X POST "http://localhost:8001/embed/text" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["This is a sample document", "Another document"],
    "collection_name": "text_embeddings"
  }'
```

### Search Text
```bash
curl -X POST "http://localhost:8001/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "sample query",
    "top_k": 5,
    "collection_name": "text_embeddings"
  }'
```

### Embed Image
```bash
curl -X POST "http://localhost:8001/embed/image" \
  -F "file=@image.jpg" \
  -F "collection_name=image_embeddings"
```

### RAG Query
```bash
curl -X POST "http://localhost:8001/rag/query" \
  -F "query=What is machine learning?" \
  -F "top_k=5"
```

## Environment Variables

- `MILVUS_HOST`: Milvus server host (default: localhost)
- `MILVUS_PORT`: Milvus server port (default: 19530)
- `EMBEDDING_MODEL`: Model for embeddings (default: sentence-transformers/all-MiniLM-L6-v2)
- `OPENAI_API_KEY`: OpenAI API key for advanced features (optional)

## Integration with Ragamuffin

The RAG service integrates with:

1. **Backend**: RAG endpoints accessible via `RAG_SERVICE_URL` environment variable
2. **Milvus**: Vector storage for embeddings
3. **n8n**: Workflow automation for RAG pipelines
4. **LangFlow**: Flow-based RAG workflows

## Multimodal Capabilities

### Text
- Document embedding and retrieval
- Semantic search
- Context extraction

### Images
- Visual embedding generation
- Image similarity search
- Cross-modal retrieval (text→image, image→text)

### Documents
- PDF processing
- Document chunking
- Metadata extraction

## Development

### Local Development
```bash
cd rag-service
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### With Docker
```bash
docker build -t ragamuffin-rag .
docker run -p 8001:8001 \
  -e MILVUS_HOST=milvus \
  -e MILVUS_PORT=19530 \
  ragamuffin-rag
```

## Security Considerations

⚠️ **Development Configuration** - For production:

1. **Authentication**: Add API key authentication
2. **Input Validation**: Validate all uploaded files
3. **Rate Limiting**: Implement request rate limiting
4. **Resource Limits**: Set embedding batch size limits
5. **Access Control**: Restrict collection access
6. **Encryption**: Use TLS for data in transit

## Performance

- **Embedding Model**: Lightweight sentence-transformers (384 dimensions)
- **Batch Processing**: Support for batch embedding generation
- **Indexing**: IVF_FLAT index for fast similarity search
- **Caching**: Model caching for improved performance

## Troubleshooting

### Milvus Connection Issues
```bash
# Check Milvus is running
curl http://localhost:9091/healthz

# Verify connection from RAG service
docker exec -it ragamuffin-rag curl http://milvus:19530
```

### Embedding Model Issues
```bash
# Check model download
docker logs ragamuffin-rag | grep "Loaded embedding model"

# Verify model directory
docker exec -it ragamuffin-rag ls -la /root/.cache/torch/sentence_transformers/
```

### Memory Issues
If embedding generation is slow or failing:
- Reduce batch size
- Use a smaller model
- Increase Docker memory limits

## Advanced Features

### Custom Embedding Models
Set `EMBEDDING_MODEL` to any sentence-transformers model:
```bash
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
```

### OpenAI Integration
For enhanced embeddings with OpenAI:
```bash
OPENAI_API_KEY=your-api-key
```

## Roadmap

- [ ] CLIP integration for true multimodal embeddings
- [ ] Document format support (DOCX, Excel, etc.)
- [ ] Hybrid search (dense + sparse)
- [ ] Query rewriting
- [ ] Result re-ranking
- [ ] Streaming responses
- [ ] Multi-tenant collections

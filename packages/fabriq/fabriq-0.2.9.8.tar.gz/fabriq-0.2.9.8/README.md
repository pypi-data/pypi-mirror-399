# Fabriq

**Fabriq** is a powerful, modular framework for building quick and low code AI solutions.
It provides a modular framework for building and deploying conversational AI Agents with minimal effort.

`NOTICE:` This package is currently under active development. The API and functionality are subject to significant changes.

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Installation Steps](#installation-steps)
   - [Configuration](#configuration)
3. [Core Components](#core-components)
   - [ConfigParser](#configparser)
   - [LLM](#llm)
   - [EmbeddingModel](#embeddingmodel)
   - [VectorStore](#vectorstore)
   - [DocumentLoader](#documentloader)
   - [TextSplitter](#textsplitter)
   - [DocumentIndexer](#documentindexer)
   - [RAGPipeline](#ragpipeline)
   - [Evaluation](#evaluation)
   - [AgentBuilder](#agentbuilder)
4. [Quick Start](#quick-start)
   - [Basic RAG Pipeline](#basic-rag-pipeline)
   - [Chat Interface](#chat-interface)
5. [Configuration Guide](#configuration-guide)
6. [Advanced Features](#advanced-features)
   - [Multimodal Processing](#multimodal-processing)
   - [Custom Tools](#custom-tools)
7. [Examples](#examples)
   - [Building a Research Assistant](#building-a-research-assistant)
   - [Creating a Multi-Agent System](#creating-a-multi-agent-system)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)
10. [License](#license)
11. [Support](#support)
12. [Author](#author)

---

## Features

✅ **Multi-provider LLM Support**: OpenAI, Azure OpenAI, HuggingFace, Gemini, Bedrock, Ollama, Groq, Mistral, and more

✅ **Comprehensive Document Processing**: PDF, Word, Excel, images, audio, and video with OCR support

✅ **Advanced RAG Pipeline**: Query rewriting, small talk detection, relevance checking, and optional reranking

✅ **Multiple Vector Stores**: ChromaDB, FAISS, and PGVector support

✅ **Agent Framework**: Build complex agent workflows with sequential or hierarchical processing

✅ **Evaluation Suite**: Metrics for answer relevancy, contextual precision, recall, faithfulness, and hallucination

✅ **Modular Design**: Easy to customize and extend components

✅ **Tracing Support**: MLflow integration for monitoring and debugging

✅ **Low-Code Solutions**: Quick deployment with CLI and UI interfaces

---

## Installation

### Prerequisites

- Python 3.10, 3.11, or 3.12
- pip
- (Optional) CUDA for GPU acceleration

### Installation Steps

Install the package with desired features:
```bash
# For all features
pip install fabriq[all]

# For chatbot only
pip install fabriq[chat]

# For agents only
pip install fabriq[agents]

# For document loader only
pip install fabriq[doc-loader]

# For indexing only
pip install fabriq[index]

# For rag pipeline only
pip install fabriq[rag]

# For tools only
pip install fabriq[tools]

# For evaluations only
pip install fabriq[evals]

# For tracing only
pip install fabriq[trace]
```

### Configuration

1. Create a `.env` file in the project root.

2. Edit the `.env` file with your desired API keys:
```ini
OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_KEY=your-azure-key
MISTRAL_API_KEY=your-mistral-api-key
...
```

3. Configure the `config.yaml` file (see [Configuration Guide](#configuration-guide) for details)

---


## Quick Start

### Basic RAG Pipeline

```python
from fabriq.config import ConfigParser
from fabriq.pipelines import RAGPipeline

# Initialize config and RAG pipeline
config = ConfigParser("config.yaml")
rag = RAGPipeline(config)

# Get response
response = rag.get_response("What are the main components of Fabriq?")
print(response["text"])

# Get sources
for chunk in response["chunks"]:
    print(f"Source: {chunk.metadata['source']}")
```

### Chat Interface

Fabriq provides two chat interfaces:

**Terminal-based CLI**:
```bash
fabriq-chat-cli
```
- Chat Commands:
  - `/help`: Show help
  - `/clear`: Clear conversation history
  - `/history`: Show conversation history
  - `/upload <directory>`: Upload documents from a directory
  - `/exit` or `/quit`: Exit chatbot


**Web-based UI** (requires Streamlit):
```bash
fabriq-chat-ui
```

---


## Advanced Features

### Multimodal Processing

The document loader can process images, tables, audio etc. within documents:
```yaml
# Enable in config.yaml
document_loader:
  params:
    multimodal: true
```

### Custom Tools

Create custom tools for agents:
```python
class CustomTool:
    def __init__(self, api_key):
        self.api_key = api_key
        self.description = "Detailed Tool Description"

    def run(self, query):
        # Implement tool logic
        return "Tool result"
```

---

## Examples

### Building a Research Assistant

```python
from fabriq.config import ConfigParser
from fabriq.pipelines import RAGPipeline
from fabriq.indexers import DocumentIndexer

# Initialize components
config = ConfigParser("config.yaml")
indexer = DocumentIndexer(config)
rag = RAGPipeline(config)

# Index research papers
indexer.index_documents([
    "paper1.pdf",
    "paper2.pdf",
    "report.docx"
])

# Ask questions
response = rag.get_response("What are the latest advancements in NLP?")
print(response["text"])

# Get sources
for chunk in response["chunks"]:
    print(f"Source: {chunk.metadata['source']}")
```

### Creating a Multi-Agent System

```yaml
# config.yaml
agent_builder:
  process: hierarchical
  params:
    agents:
      - name: researcher
        role: Research Analyst
        goal: Find relevant information
        backstory: Expert in information retrieval
        tools: [WebSearchTool]
      - name: analyst
        role: Data Analyst
        goal: Analyze information
        backstory: Skilled in data interpretation
      - name: writer
        role: Technical Writer
        goal: Create comprehensive reports
        backstory: Experienced technical communicator
    tasks:
      - name: research
        description: >
          Research the topic: {topic_name}
        expected_output: Research notes
        agent: researcher
      - name: analyze
        description: Analyze research findings
        expected_output: Analysis report
        agent: analyst
        context: [research]
      - name: write
        description: Write final report
        expected_output: Complete report
        agent: writer
        context: [analyze]
```

```python
from fabriq.config import ConfigParser
from fabriq.agents import AgentBuilder

config = ConfigParser("config.yaml")
agent_builder = AgentBuilder(config)

# Execute the workflow
result = agent_builder.run(inputs={"topic_name":"Artificial Intelligence"})
print(result)
```

_For more details, see the wardrobe directory and example notebooks in the config folder._

---

## Troubleshooting

### Common Issues and Solutions

**1. Configuration Errors**
- *Symptom*: `ValueError: Unsupported LLM model type`
- *Solution*: Verify `config.yaml` contains valid model types and all required parameters.

**2. Document Loading Failures**
- *Symptom*: OCR errors when loading documents
- *Solution*:
  - Ensure Tesseract OCR is installed
  - Check file permissions
  - Verify document integrity

**3. Vector Store Connection Issues**
- *Symptom*: Connection errors with PGVector
- *Solution*:
  - Verify PostgreSQL is running
  - Check connection string in config
  - Ensure pgvector extension is installed

**4. LLM API Errors**
- *Symptom*: Rate limit exceeded errors
- *Solution*:
  - Add retry logic in `model_kwargs`
  - Reduce batch size
  - Verify API key validity

**5. Memory Issues**
- *Symptom*: Out of memory errors with large documents
- *Solution*:
  - Reduce `chunk_size` in text splitter
  - Process documents in smaller batches
  - Use smaller embedding models

### Debugging Tips

1. Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Test components individually:
```python
# Test LLM
llm = LLM(config)
print(llm.generate("Test prompt"))

# Test embeddings
embeddings = EmbeddingModel(config)
print(embeddings.embed_query("Test query"))
```

3. Use MLflow tracing:
```yaml
# config.yaml
llm:
  params:
    tracing_enabled: true
    tracing_uri: "http://localhost:5000"
```

---

## License

Fabriq is released under the [MIT License](LICENSE).

---

## Support

For questions and support:
- Open an issue on GitHub
---

## Author

[Aaryan Verma](https://linkedin.com/in/aaryanverma)
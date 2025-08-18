# Text Chunking Separators Reference Guide

A comprehensive reference for text chunking strategies and separator options for RAG systems.

## Table of Contents

- [Overview](#overview)
- [Default General-Purpose Separators](#default-general-purpose-separators)
- [Custom Separators by Document Type](#custom-separators-by-document-type)
- [LangChain Text Splitter Types](#langchain-text-splitter-types)
- [Advanced Semantic Approaches](#advanced-semantic-approaches)
- [Domain-Specific Examples](#domain-specific-examples)
- [Language-Specific Considerations](#language-specific-considerations)
- [Implementation Examples](#implementation-examples)
- [Decision Matrix](#decision-matrix)

## Overview

Text chunking is crucial for RAG systems to break documents into meaningful, searchable pieces. The choice of separators and chunking strategy dramatically affects search quality and semantic preservation.

**Key Principle**: Use the most natural document boundaries first, then fall back to less natural boundaries when necessary.

## Default General-Purpose Separators

The standard RecursiveCharacterTextSplitter uses this hierarchy:

```python
separators = ["\n\n", "\n", " ", ""]
```

**Priority Order:**
1. `"\n\n"` - Paragraph breaks (highest semantic value)
2. `"\n"` - Line breaks (moderate semantic value)  
3. `" "` - Word boundaries (preserves word integrity)
4. `""` - Character level (last resort)

**Use Case**: General text documents, articles, books, basic PDFs

## Custom Separators by Document Type

### Programming Code

**Best for**: Source code files, technical documentation with code blocks

```python
code_separators = [
    "\n\nclass ",      # Class definitions
    "\n\ndef ",        # Function definitions  
    "\n\nif __name__", # Main blocks
    "\n\nasync def ",  # Async functions
    "\n\ntry:",        # Error handling blocks
    "\n\n",            # Double newline
    "\n",              # Single newline
    " ",               # Space
    ""                 # Character level
]
```

### HTML/Web Content

**Best for**: Web pages, HTML documentation, web scraping content

```python
html_separators = [
    "</article>",      # Article boundaries
    "</section>",      # Section boundaries
    "</div>",          # Div boundaries
    "</p>",            # Paragraph boundaries
    "</h1>", "</h2>", "</h3>",  # Header boundaries
    "<br>", "<br/>",   # Line breaks
    "\n\n", "\n", " ", ""
]
```

### Academic Papers

**Best for**: Research papers, scientific documents, structured academic content

```python
academic_separators = [
    "\n\nAbstract",
    "\n\nIntroduction", 
    "\n\nRelated Work",
    "\n\nMethodology",
    "\n\nExperiments",
    "\n\nResults",
    "\n\nDiscussion",
    "\n\nConclusion",
    "\n\nReferences",
    "\n\nFigure ",     # Figure captions
    "\n\nTable ",      # Table captions
    "\n\n", "\n", " ", ""
]
```

### Legal Documents

**Best for**: Contracts, legal briefs, legislation, regulatory documents

```python
legal_separators = [
    "\n\nArticle ",     # Article boundaries
    "\n\nSection ",     # Section boundaries
    "\n\nSubsection ",  # Subsection boundaries
    "\n\nClause ",      # Clause boundaries
    "\n\nWHEREAS",      # Contract clauses
    "\n\nNOW THEREFORE", # Contract transitions
    "\n\n", "\n", " ", ""
]
```

### Markdown Documents

**Best for**: Documentation, README files, wiki content, technical writing

```python
markdown_separators = [
    "\n\n# ",          # H1 headers
    "\n\n## ",         # H2 headers
    "\n\n### ",        # H3 headers
    "\n\n#### ",       # H4 headers
    "\n\n```",         # Code blocks
    "\n\n---",         # Horizontal rules
    "\n\n",            # Paragraphs
    "\n", " ", ""
]
```

### News Articles

**Best for**: Journalism, press releases, news content

```python
news_separators = [
    "\n\nHeadline:",
    "\n\nByline:",
    "\n\nLead:",
    "\n\nBody:",
    "\n\nQuote:",
    "\n\n", "\n", " ", ""
]
```

### Chat/Conversation Logs

**Best for**: Customer service logs, chat transcripts, dialogue systems

```python
chat_separators = [
    "\n\n[User]:",
    "\n\n[Assistant]:",
    "\n\n[Agent]:",
    "\n\n[System]:",
    "\n\nTimestamp:",
    "\n", " ", ""
]
```

### Technical Manuals

**Best for**: User manuals, API documentation, technical specifications

```python
manual_separators = [
    "\n\nChapter ",
    "\n\nSection ",
    "\n\nStep ",
    "\n\nNote:",
    "\n\nWarning:",
    "\n\nExample:",
    "\n\n", "\n", " ", ""
]
```

## LangChain Text Splitter Types

### CharacterTextSplitter
**Simple character-based splitting with single separator**

```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
```

**Use Case**: Simple documents with consistent structure

### RecursiveCharacterTextSplitter  
**Hierarchical separator-based splitting (our current choice)**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1800,
    chunk_overlap=270,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)
```

**Use Case**: General-purpose text with varied structure

### TokenTextSplitter
**Token-based splitting for LLM context management**

```python
from langchain.text_splitter import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=500,    # 500 tokens, not characters
    chunk_overlap=50,
    model_name="gpt-3.5-turbo"
)
```

**Use Case**: When you need precise token control for LLM processing

### MarkdownHeaderTextSplitter
**Structure-aware Markdown splitting**

```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"), 
    ("###", "Header 3"),
    ("####", "Header 4")
]

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False
)
```

**Use Case**: Technical documentation, wikis, structured Markdown content

### HTMLHeaderTextSplitter
**HTML structure-aware splitting**

```python
from langchain.text_splitter import HTMLHeaderTextSplitter

headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
    ("h4", "Header 4")
]

splitter = HTMLHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)
```

**Use Case**: Web content, HTML documentation, scraped web pages

### Language-Specific Code Splitters

**PythonCodeTextSplitter**
```python
from langchain.text_splitter import PythonCodeTextSplitter

splitter = PythonCodeTextSplitter(
    chunk_size=2000,
    chunk_overlap=200
)
```

**JavaScriptCodeTextSplitter**
```python
from langchain.text_splitter import JavaScriptCodeTextSplitter

splitter = JavaScriptCodeTextSplitter(
    chunk_size=2000,
    chunk_overlap=200
)
```

**LatexTextSplitter**
```python
from langchain.text_splitter import LatexTextSplitter

splitter = LatexTextSplitter(
    chunk_size=2000,
    chunk_overlap=200
)
```

**Use Case**: Programming documentation, code analysis, technical tutorials

## Advanced Semantic Approaches

### Semantic Chunking (Embedding-Based)

**Concept**: Split based on semantic similarity rather than structural boundaries

```python
def semantic_chunk(text, similarity_threshold=0.8, max_chunk_size=2000):
    """
    Split text based on semantic similarity between sentences.
    """
    sentences = split_into_sentences(text)
    embeddings = embed_sentences(sentences)
    
    chunks = []
    current_chunk = [sentences[0]]
    current_size = len(sentences[0])
    
    for i in range(1, len(sentences)):
        similarity = cosine_similarity(
            embeddings[i-1], 
            embeddings[i]
        )
        
        sentence_len = len(sentences[i])
        
        # Split if similarity drops OR chunk gets too large
        if (similarity < similarity_threshold or 
            current_size + sentence_len > max_chunk_size):
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]
            current_size = sentence_len
        else:
            current_chunk.append(sentences[i])
            current_size += sentence_len
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks
```

**Advantages**: Preserves semantic coherence
**Disadvantages**: Computationally expensive, requires embeddings model

### Topic-Based Chunking

**Concept**: Group content by topics using topic modeling

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def topic_based_chunk(text, n_topics=5):
    """
    Group paragraphs by topic similarity.
    """
    paragraphs = text.split('\n\n')
    
    # Vectorize paragraphs
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(paragraphs)
    
    # Cluster by topic
    kmeans = KMeans(n_clusters=n_topics, random_state=42)
    topics = kmeans.fit_predict(vectors)
    
    # Group paragraphs by topic
    chunks = []
    for topic_id in range(n_topics):
        topic_paragraphs = [
            p for i, p in enumerate(paragraphs) 
            if topics[i] == topic_id
        ]
        if topic_paragraphs:
            chunks.append('\n\n'.join(topic_paragraphs))
    
    return chunks
```

**Use Case**: Long documents with mixed topics, research papers

### Named Entity Recognition (NER) Boundaries

**Concept**: Split at natural entity boundaries to preserve entity context

```python
import spacy

def ner_aware_chunk(text, chunk_size=1500):
    """
    Split text while preserving named entity contexts.
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    chunks = []
    current_chunk = ""
    
    for sent in doc.sents:
        if len(current_chunk) + len(sent.text) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
        current_chunk += sent.text + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
```

**Use Case**: Documents with many named entities, news articles

## Language-Specific Considerations

### Chinese Text

**Challenges**: No spaces between words, different punctuation patterns

```python
chinese_separators = [
    "。\n\n",    # Period + double newline
    "！\n\n",    # Exclamation + double newline
    "？\n\n",    # Question + double newline
    "。\n",      # Period + newline
    "！\n",      # Exclamation + newline
    "？\n",      # Question + newline
    "。",        # Period only
    "！",        # Exclamation only
    "？",        # Question only
    "\n\n", "\n", ""  # No space separator
]
```

### Arabic Text

**Challenges**: Right-to-left text, different punctuation

```python
arabic_separators = [
    ".\n\n",     # Period + double newline
    "!\n\n",     # Exclamation + double newline  
    "?\n\n",     # Question + double newline
    ".\n",       # Period + newline
    "!\n",       # Exclamation + newline
    "?\n",       # Question + newline
    ".",         # Period only
    "!",         # Exclamation only
    "?",         # Question only
    "\n\n", "\n", " ", ""
]
```

### Japanese Text

**Challenges**: Multiple writing systems (hiragana, katakana, kanji)

```python
japanese_separators = [
    "。\n\n",    # Japanese period + double newline
    "！\n\n",    # Japanese exclamation + double newline
    "？\n\n",    # Japanese question + double newline
    "。\n",      # Japanese period + newline
    "。",        # Japanese period only
    "\n\n", "\n", ""
]
```

## Implementation Examples

### Customizing Our Current PDF Processor

**Option 1: Modify pdf_processor.py directly**

```python
# In pdf_processor.py, update the RecursiveCharacterTextSplitter call:

def pdf_to_documents_recursive(self, pdf_path: Path, document_type="general", chunk_size: int = None, chunk_overlap: int = None):
    """
    Convert PDF with document-type-aware separators.
    """
    # Define separator sets
    separator_sets = {
        "general": ["\n\n", "\n", " ", ""],
        "academic": ["\n\nAbstract", "\n\nIntroduction", "\n\nMethodology", 
                    "\n\nResults", "\n\nConclusion", "\n\n", "\n", " ", ""],
        "legal": ["\n\nArticle ", "\n\nSection ", "\n\nClause ", 
                 "\n\n", "\n", " ", ""],
        "code": ["\n\nclass ", "\n\ndef ", "\n\n", "\n", " ", ""],
        "manual": ["\n\nChapter ", "\n\nSection ", "\n\nStep ", 
                  "\n\n", "\n", " ", ""]
    }
    
    separators = separator_sets.get(document_type, separator_sets["general"])
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or self.default_pdf_chunk_size,
        chunk_overlap=chunk_overlap or self.default_pdf_overlap,
        length_function=len,
        separators=separators
    )
    
    # Rest of the implementation...
```

**Option 2: Create specialized processors**

```python
# Create separate processor classes for different document types

class AcademicPDFProcessor(PDFProcessor):
    def __init__(self):
        super().__init__()
        self.separators = [
            "\n\nAbstract", "\n\nIntroduction", "\n\nMethodology",
            "\n\nResults", "\n\nConclusion", "\n\nReferences",
            "\n\n", "\n", " ", ""
        ]

class LegalPDFProcessor(PDFProcessor):
    def __init__(self):
        super().__init__()
        self.separators = [
            "\n\nArticle ", "\n\nSection ", "\n\nClause ",
            "\n\nWHEREAS", "\n\nNOW THEREFORE",
            "\n\n", "\n", " ", ""
        ]

class CodeDocumentProcessor(PDFProcessor):
    def __init__(self):
        super().__init__()
        self.separators = [
            "\n\nclass ", "\n\ndef ", "\n\nasync def ",
            "\n\n", "\n", " ", ""
        ]
```

### Using Different LangChain Splitters

**Example: HTML Documentation**

```python
from langchain.text_splitter import HTMLHeaderTextSplitter
from langchain_community.document_loaders import UnstructuredHTMLLoader

def process_html_docs(html_path: Path):
    # Load HTML
    loader = UnstructuredHTMLLoader(str(html_path))
    data = loader.load()
    
    # Split by HTML structure
    headers_to_split_on = [
        ("h1", "Header 1"),
        ("h2", "Header 2"),
        ("h3", "Header 3")
    ]
    
    html_splitter = HTMLHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    
    html_docs = html_splitter.split_documents(data)
    
    # Further split large sections if needed
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1800,
        chunk_overlap=270
    )
    
    final_docs = text_splitter.split_documents(html_docs)
    return final_docs
```

**Example: Markdown Documentation**

```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

def process_markdown_docs(md_path: Path):
    with open(md_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    
    # Split by Markdown headers
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3")
    ]
    
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )
    
    md_docs = md_splitter.split_text(markdown_text)
    
    # Convert to Documents with metadata
    documents = []
    for i, chunk in enumerate(md_docs):
        doc = Document(
            page_content=chunk.page_content,
            metadata={
                "source": str(md_path),
                "chunk_id": i,
                "headers": chunk.metadata
            }
        )
        documents.append(doc)
    
    return documents
```

## Decision Matrix

| Document Type | Recommended Approach | Separators | Chunk Size | Overlap |
|---------------|---------------------|------------|------------|---------|
| **General Text/PDFs** | RecursiveCharacterTextSplitter | `["\n\n", "\n", " ", ""]` | 1500-2000 | 15-20% |
| **Academic Papers** | Custom separators | Academic sections | 2000-2500 | 20% |
| **Programming Code** | PythonCodeTextSplitter | Language-aware | 1500-2000 | 15% |
| **HTML Documentation** | HTMLHeaderTextSplitter | HTML headers | 1500-2000 | 15% |
| **Markdown Docs** | MarkdownHeaderTextSplitter | MD headers | 1500-2000 | 15% |
| **Legal Documents** | Custom separators | Legal sections | 2000-3000 | 20-25% |
| **News Articles** | Custom separators | Article structure | 1000-1500 | 15% |
| **Chat Logs** | Custom separators | Speaker turns | 800-1200 | 10% |
| **Technical Manuals** | Custom separators | Manual sections | 1500-2000 | 20% |
| **Multilingual** | Language-specific | Language punctuation | Varies | 15-20% |

## Best Practices

### 1. Document Analysis First
- Examine document structure before choosing separators
- Identify natural boundaries (headers, sections, paragraphs)
- Consider domain-specific conventions

### 2. Test and Validate
- Use search quality metrics to validate separator choices
- A/B test different approaches with representative queries
- Monitor chunk coherence and boundary quality

### 3. Iterative Refinement
- Start with general separators
- Gradually customize based on performance
- Document what works for different document types

### 4. Consider Performance Trade-offs
- Semantic approaches: Better quality, higher computational cost
- Structure-aware: Good balance of quality and performance  
- Simple character-based: Fast but potentially lower quality

### 5. Overlap Optimization
- 15-20% overlap for most document types
- Higher overlap (20-25%) for complex or technical content
- Lower overlap (10-15%) for simple or repetitive content

## Future Enhancements

### Advanced Techniques to Consider
1. **Hybrid Approaches**: Combine structural and semantic chunking
2. **Dynamic Chunk Sizing**: Adjust chunk size based on content complexity
3. **Multi-Level Chunking**: Create hierarchical chunk structures
4. **Context-Aware Overlaps**: Variable overlap based on content importance
5. **Learning-Based Optimization**: ML models to optimize chunking for specific domains

### Framework Extensions
1. **Custom Splitter Classes**: Domain-specific splitter implementations
2. **Preprocessing Pipelines**: Clean and normalize text before chunking
3. **Quality Metrics**: Automated evaluation of chunk quality
4. **A/B Testing Framework**: Systematic testing of chunking strategies

---

*This document serves as a comprehensive reference for text chunking strategies in RAG systems. Update as new techniques and requirements emerge.*
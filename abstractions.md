# Task: Refactor the Embedding & Vector Store Architecture to Use Provider Abstractions

## Background

We're building Zam AI, a production-grade medical RAG platform. The current implementation is tightly coupled to a single embedding provider. Before we proceed further, I want to refactor the architecture so that both the embedding model and vector database are completely swappable.

The goal is to follow good software engineering principles (Dependency Inversion, Strategy Pattern, Clean Architecture) so that changing providers in the future only requires changing configuration, not modifying business logic.

This refactor should not change the external behavior of the application.

---

# Objectives

## 1. Create an Embedding Abstraction

Create a common interface (or abstract base class) for embedding providers.

Example:

```python
class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        ...
```

Implement the following providers:

- JinaEmbeddingProvider
- GeminiEmbeddingProvider
- VoyageEmbeddingProvider

Each provider should:

- Handle authentication internally
- Validate configuration
- Return embeddings in a consistent format
- Raise meaningful exceptions
- Hide provider-specific implementation details

No other part of the application should know which provider is being used.

---

## 2. Provider Factory

Implement a factory that instantiates the correct provider based on configuration.

Example:

```env
EMBEDDING_PROVIDER=jina
```

Supported values:

- jina
- gemini
- voyage

Usage should look like:

```python
embedding_provider = get_embedding_provider(settings)
vectors = await embedding_provider.embed(texts)
```

---

## 3. Refactor Existing Code

Search the project for any direct calls to:

- Jina
- Gemini embedding API
- Voyage embedding API

Replace all of them so that they go through the abstraction layer.

There should be **zero provider-specific code** outside the provider implementations.

---

# Vector Store Abstraction

Create a similar abstraction for vector databases.

Example:

```python
class VectorStore(ABC):
    @abstractmethod
    async def upsert(...):
        ...

    @abstractmethod
    async def query(...):
        ...

    @abstractmethod
    async def delete(...):
        ...
```

Implement:

- PineconeVectorStore
- QdrantVectorStore

---

## Factory

Support:

```env
VECTOR_STORE=pinecone
```

or

```env
VECTOR_STORE=qdrant
```

The rest of the codebase should never know which vector database is being used.

---

# Dependency Injection

The RAG pipeline should receive the abstractions.

Example:

```python
class RAGPipeline:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ):
        ...
```

Avoid global imports or hardcoded providers.

---

# Configuration

Move all provider-specific settings into configuration.

Examples:

```env
EMBEDDING_PROVIDER=jina

JINA_API_KEY=...

VOYAGE_API_KEY=...

GEMINI_API_KEY=...

VECTOR_STORE=pinecone

PINECONE_API_KEY=...

QDRANT_URL=...
```

The application should fail fast with clear errors if required configuration is missing.

---

# Folder Structure

Refactor into something similar to:

```
src/
    embeddings/
        base.py
        factory.py
        providers/
            jina.py
            gemini.py
            voyage.py

    vectorstores/
        base.py
        factory.py
        providers/
            pinecone.py
            qdrant.py
```

Use whatever naming best fits the existing project conventions.

---

# Error Handling

Each provider should:

- Wrap third-party exceptions
- Return consistent internal exceptions
- Log useful debugging information
- Never leak provider-specific implementation into higher layers

---

# Documentation

Document:

- How to add a new embedding provider
- How to add a new vector database
- How factories work
- How dependency injection is used
- Required environment variables

---

# Acceptance Criteria

The refactor is complete when:

- There are no direct embedding API calls outside provider implementations.
- There are no direct Pinecone/Qdrant calls outside vector store implementations.
- Switching providers only requires changing environment variables.
- Existing functionality continues to work.
- Code follows SOLID principles.
- The architecture is easy to extend with future providers.

---

# Important

Do **not** over-engineer the solution.

The abstractions should remain lightweight and focused.

The implementation should prioritize:

- readability
- maintainability
- extensibility
- testability

over unnecessary complexity.

If you identify opportunities to simplify or improve the architecture while preserving these goals, feel free to do so and explain your reasoning.
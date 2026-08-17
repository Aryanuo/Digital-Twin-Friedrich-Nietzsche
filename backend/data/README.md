# Nietzsche Digital Twin Data

This directory contains the local data-processing pipeline used to prepare
Nietzsche-related source material for the RAG system.


The processed data is intentionally excluded from Git because the source
corpus and generated embeddings are large and are not required by the
runtime application.

## Data Pipeline

The data preparation pipeline follows this sequence:

```text
Raw Source Material
        ↓
preprocess.py
        ↓
Processed Data
        ↓
chunker.py
        ↓
Text Chunks
        ↓
embed.py
        ↓
768-dimensional Embeddings
        ↓
Qdrant Cloud
```

## raw/

Contains the original source material used to build the Nietzsche corpus.

The corpus contain:

Books
Essays
Lectures
Letters
Notebooks
Other relevant philosophical material

The source material was collected primarily from Project Gutenberg and
other online sources.

## processed/

Contains text after preprocessing and cleaning.

preprocess.py converts the raw source material into a cleaner format
suitable for chunking and embedding.

## chunks/

Contains the processed text divided into smaller chunks.

chunker.py creates these chunks so that individual sections of text can
be embedded and retrieved efficiently.

## embeddings/

Contains the vector representations generated from the text chunks.

embed.py uses:

BAAI/bge-base-en-v1.5

to convert each text chunk into a 768-dimensional embedding vector.

These embeddings were uploaded to the nietzsche collection in Qdrant Cloud.



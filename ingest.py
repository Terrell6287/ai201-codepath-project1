# ingest.py
# M3: Document Ingestion and Chunking Pipeline
# Sources: Yugipedia (wiki), YGOPRODeck, MasterDuelMeta, Reddit threads

import os
import re
import random

# ── CONFIGURATION (matches planning.md spec) ────────────────────
CHUNK_SIZE_TOKENS = 400
OVERLAP_TOKENS = 50
CHARS_PER_TOKEN = 4  # approximation: 1 token ≈ 4 characters

CHUNK_SIZE_CHARS = CHUNK_SIZE_TOKENS * CHARS_PER_TOKEN   # 1600 chars
OVERLAP_CHARS = OVERLAP_TOKENS * CHARS_PER_TOKEN          # 200 chars

DOCUMENTS_FOLDER = "documents"

# Maps each filename to its source type for targeted cleaning
SOURCE_TYPE_MAP = {
    "yugipedia_archetypes.txt":          "wiki",
    "yugipedia_hand_traps.txt":          "wiki",
    "game8_beginner_guide.txt":          "guide",  
    "ygoprodeck_banlist_article.txt":    "guide",
    "masterduelmeta_reintro_guide.txt":  "guide",
    "masterduelmeta_combos.txt":         "guide",
    "masterduelmeta_guides.txt":         "guide",
    "reddit_yugioh_rulings.txt":         "reddit",
    "reddit_masterduel_megathread.txt":  "reddit",
    "rulebook.txt":                      "pdf",
}

# These sources use comment-level chunking instead of paragraph chunking
REDDIT_SOURCES = {
    "reddit_yugioh_rulings.txt",
    "reddit_masterduel_megathread.txt",
}

# ── STAGE 1: LOAD ───────────────────────────────────────────────
def load_documents(folder=DOCUMENTS_FOLDER):
    """Load all .txt files from the documents folder."""
    docs = []
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                docs.append({"filename": filename, "text": f.read()})
    print(f"[Load] {len(docs)} documents loaded.")
    return docs

# ── STAGE 2: CLEAN ──────────────────────────────────────────────
def clean_text(text, source_type="wiki"):
    """Remove boilerplate, HTML artifacts, and noise by source type."""

    # Universal fixes for all sources
    text = text.replace("&amp;", "&")
    text = text.replace("&nbsp;", " ")
    text = text.replace("&#39;", "'")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = re.sub(r'\n{3,}', '\n\n', text)   # collapse excess blank lines
    text = re.sub(r' {2,}', ' ', text)        # collapse excess spaces

    if source_type == "wiki":
        # Yugipedia: remove edit links, nav footers, category lines
        text = re.sub(r'\[edit\]', '', text)
        text = re.sub(r'Retrieved from.*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Navigation menu.*', '', text, flags=re.DOTALL)
        text = re.sub(r'Categories\s*:.*', '', text, flags=re.DOTALL)

    elif source_type == "reddit":
        # Reddit: remove vote counts, action links, usernames
        text = re.sub(r'\d+\s*points?', '', text)
        text = re.sub(r'\b(share|save|hide|report|reply|permalink|more)\b', '',
                      text, flags=re.IGNORECASE)
        text = re.sub(r'Posted by u/\S+', '', text)
        text = re.sub(r'u/\S+ · \d+[hd] ago', '', text)

    elif source_type == "guide":
        # MasterDuelMeta / YGOPRODeck: remove site chrome
        text = re.sub(r'\b(Advertisement|Subscribe|Sign [Uu]p|Log [Ii]n|Cookie)\b',
                      '', text, flags=re.IGNORECASE)
        text = re.sub(r'Read [Mm]ore.*', '', text)

    return text.strip()

# ── STAGE 3: CHUNK ──────────────────────────────────────────────
def chunk_by_paragraph(text, source):
    """
    For wiki pages and guides.
    Splits on paragraph boundaries, targeting CHUNK_SIZE_CHARS.
    Carries OVERLAP_CHARS from the end of one chunk into the start of the next
    so strategy explanations aren't cut cold at boundaries.
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 40]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) <= CHUNK_SIZE_CHARS:
            current += para + "\n\n"
        else:
            if current.strip():
                chunks.append({"text": current.strip(), "source": source})
            # Overlap: carry tail of previous chunk forward
            overlap_tail = current[-OVERLAP_CHARS:] if len(current) > OVERLAP_CHARS else current
            current = overlap_tail + para + "\n\n"

    if current.strip():
        chunks.append({"text": current.strip(), "source": source})

    return chunks

def chunk_by_comment(text, source, min_length=60):
    """
    For Reddit threads and combo megathreads.
    Each comment/entry is already a self-contained thought,
    so treat each paragraph-separated block as its own chunk.
    Filters out fragments shorter than min_length.
    """
    entries = [e.strip() for e in text.split('\n\n') if len(e.strip()) >= min_length]
    return [{"text": entry, "source": source} for entry in entries]

# ── FULL PIPELINE ───────────────────────────────────────────────
def build_pipeline(folder=DOCUMENTS_FOLDER):
    docs = load_documents(folder)
    all_chunks = []

    for doc in docs:
        fname = doc["filename"]
        source_type = SOURCE_TYPE_MAP.get(fname, "wiki")

        cleaned = clean_text(doc["text"], source_type=source_type)

        if fname in REDDIT_SOURCES:
            chunks = chunk_by_comment(cleaned, source=fname)
        else:
            chunks = chunk_by_paragraph(cleaned, source=fname)

        print(f"[Chunk] {fname}: {len(chunks)} chunks")
        all_chunks.extend(chunks)

    print(f"\n[Done] Total chunks: {len(all_chunks)}")
    return all_chunks

# ── CHECKPOINT: inspect 5 random chunks ────────────────────────
def inspect_chunks(chunks, n=5):
    print(f"\n{'='*60}")
    print(f"CHUNK INSPECTION — {n} random samples")
    print(f"{'='*60}")
    samples = random.sample(chunks, min(n, len(chunks)))
    for i, chunk in enumerate(samples):
        print(f"\nChunk {i+1} | Source: {chunk['source']}")
        print(f"Length : {len(chunk['text'])} chars (~{len(chunk['text'])//4} tokens)")
        print(f"{'-'*40}")
        print(chunk['text'])

# ── ENTRY POINT ─────────────────────────────────────────────────
if __name__ == "__main__":
    chunks = build_pipeline()
    inspect_chunks(chunks)
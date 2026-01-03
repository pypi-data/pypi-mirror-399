import os
import json
import shutil
import chromadb
from fastembed import TextEmbedding
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading


PREFERRED_MODELS = [
    "jinaai/jina-embeddings-v2-base-zh",              # 中英混合友好，~0.64GB
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",  # 多语 ~50 语种
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # 多语轻量版
    "intfloat/multilingual-e5-large",                 # 多语更强，体积约 2.2GB
]

# Final chosen model will be detected at runtime from supported list
MODEL_NAME = None
COLLECTION_NAME = "brain_kb_v5"

# Optional imports for different file types
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

class KnowledgeBase:
    def __init__(self, kb_path="knowledge", db_path="vector_db"):
        self.kb_path = os.path.abspath(kb_path)
        self.db_path = os.path.abspath(db_path)
        self._collection_reset_guard = False
        
        if not os.path.exists(self.kb_path):
            os.makedirs(self.kb_path)
        
        # Initialize Embedding Model (BAAI/bge-small-zh-v1.5 is ~100MB)
        # This will load from cache if already downloaded
        # Pick the first available model from the preferred list
        _supported_raw = TextEmbedding.list_supported_models()
        supported = set()
        for item in _supported_raw:
            if isinstance(item, dict) and "model" in item:
                supported.add(item["model"])
            elif isinstance(item, str):
                supported.add(item)
        chosen = None
        for name in PREFERRED_MODELS:
            if name in supported:
                chosen = name
                break
        if not chosen:
            raise RuntimeError(
                "No preferred embedding models are supported by fastembed. "
                "Please check available models via TextEmbedding.list_supported_models()."
            )

        print(f"Loading Knowledge Base Embedding Model: {chosen} (may take some time on first run)...")
        try:
            self.model = TextEmbedding(model_name=chosen)
            print("Embedding Model loaded successfully.")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            raise

        # Store chosen model name for reference
        global MODEL_NAME
        MODEL_NAME = chosen
        
        # Initialize Vector DB
        self._init_collection()
        
        # Initial sync
        self.sync_knowledge()
        
        # Start Watcher
        self.start_watcher()

    def _init_collection(self, recreate: bool = False):
        """(Re)initialize Chroma client/collection. If recreate=True, wipe on-disk index."""
        if recreate and os.path.exists(self.db_path):
            shutil.rmtree(self.db_path, ignore_errors=True)
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def sync_knowledge(self, allow_reset: bool = True):
        """Scans the knowledge folder and updates the vector database."""
        print("Syncing knowledge base...")
        supported_extensions = (".txt", ".md", ".pdf", ".docx", ".json")
        for filename in os.listdir(self.kb_path):
            file_path = os.path.join(self.kb_path, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(supported_extensions):
                try:
                    content = self._extract_text(file_path)
                    if content:
                        # Sliding window chunking on original text
                        chunk_size = 400
                        overlap = 80
                        original_chunks = []
                        for i in range(0, len(content), chunk_size - overlap):
                            chunk = content[i:i + chunk_size].strip()
                            if chunk:
                                original_chunks.append(chunk)
                        
                        if original_chunks:
                            # Normalize for embedding generation only (not for storage)
                            normalized_chunks = [c.lower().replace('_', ' ') for c in original_chunks]
                            
                            ids = [f"{filename}_{i}" for i in range(len(original_chunks))]
                            metadatas = [{"source": filename, "chunk": i} for i in range(len(original_chunks))]
                            
                            # Compute embeddings from normalized text
                            embeddings = []
                            for v in self.model.embed(normalized_chunks):
                                try:
                                    embeddings.append(v.tolist())
                                except Exception:
                                    embeddings.append(list(v))
                            
                            # Store ORIGINAL text (not normalized) so users see the real content
                            self.collection.upsert(
                                documents=original_chunks,
                                ids=ids,
                                metadatas=metadatas,
                                embeddings=embeddings
                            )
                            print(f"  ✓ Indexed {filename}: {len(original_chunks)} chunks")
                except Exception as e:
                    err_msg = str(e)
                    print(f"Error processing {filename}: {err_msg}")
                    # Auto-recover if HNSW/compaction/index errors occur
                    if allow_reset and any(x in err_msg.lower() for x in ["hnsw", "compaction", "segment reader"]):
                        if not self._collection_reset_guard:
                            print("Detected index corruption. Rebuilding vector_db and retrying sync once...")
                            self._collection_reset_guard = True
                            self._init_collection(recreate=True)
                            return self.sync_knowledge(allow_reset=False)
        print("Knowledge base sync complete.")

    def _extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == ".md":
            # Treat Markdown as plain text for retrieval
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif ext == ".pdf":
            if PdfReader:
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            else:
                print("pypdf not installed, skipping PDF.")
        elif ext == ".docx":
            if Document:
                doc = Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            else:
                print("python-docx not installed, skipping Word.")
        elif ext == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, ensure_ascii=False, indent=2)
        return None

    def query(self, text, top_k=5, distance_threshold=0.8):
        """Retrieves relevant snippets from the knowledge base.

        Uses cosine distance (lower is better). A result is treated as a hit only
        when best_distance <= distance_threshold.
        Returns:
            dict: {"hit": bool, "context": str, "hits": [{source, chunk, distance, text}, ...]}
        """
        try:
            # Normalize query same as indexed content
            normalized_text = text.lower().replace('_', ' ')
            
            q_vec = None
            for v in self.model.embed([normalized_text]):
                try:
                    q_vec = v.tolist()
                except Exception:
                    q_vec = list(v)
                break
            if q_vec is None:
                return {"hit": False, "context": "", "hits": []}

            results = self.collection.query(
                query_embeddings=[q_vec],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            docs = (results or {}).get("documents") or []
            metas = (results or {}).get("metadatas") or []
            dists = (results or {}).get("distances") or []

            if not docs or not docs[0]:
                print("[KB Query] No results returned from collection")
                return {"hit": False, "context": "", "hits": []}

            docs0 = docs[0]
            metas0 = metas[0] if metas and metas[0] else [{} for _ in docs0]
            dists0 = dists[0] if dists and dists[0] else [None for _ in docs0]

            hits = []
            for doc_text, meta, dist in zip(docs0, metas0, dists0):
                hits.append({
                    "source": (meta or {}).get("source", ""),
                    "chunk": (meta or {}).get("chunk", None),
                    "distance": dist,
                    "text": doc_text,
                })

            best = hits[0].get("distance")
            is_hit = (best is not None) and (best <= distance_threshold)
            
            # Debug log
            best_str = f"{best:.4f}" if best is not None else "N/A"
            print(f"[KB Query] '{text[:50]}...' -> best_dist={best_str}, threshold={distance_threshold}, hit={is_hit}")
            if hits:
                top3_dists = [f"{h['distance']:.4f}" if h['distance'] is not None else "N/A" for h in hits[:3]]
                print(f"[KB Query] Top 3 distances: {top3_dists}")
            
            context = "\n---\n".join([h["text"] for h in hits]) if is_hit else ""
            return {"hit": is_hit, "context": context, "hits": hits}
        except Exception as e:
            print(f"Query error: {e}")
            import traceback
            traceback.print_exc()
            return {"hit": False, "context": "", "hits": []}

    def start_watcher(self):
        event_handler = KBHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.kb_path, recursive=False)
        self.observer.start()

class KBHandler(FileSystemEventHandler):
    def __init__(self, kb_instance):
        self.kb = kb_instance
        self.supported_extensions = (".txt", ".md", ".pdf", ".docx", ".json")

    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith(self.supported_extensions):
            print(f"File modified: {event.src_path}. Re-syncing...")
            threading.Thread(target=self.kb.sync_knowledge).start()

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(self.supported_extensions):
            print(f"File created: {event.src_path}. Syncing...")
            threading.Thread(target=self.kb.sync_knowledge).start()


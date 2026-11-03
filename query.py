"""KodKalkan - bilgi tabaninda arama (RAG'in 'retrieval' adimi).

Kullanim:
    python query.py "kullanici girdisi os.system'e gidiyor"
"""
import sys

import chromadb
import ollama

from config import CHROMA_SETTINGS, COLLECTION, EMBED_MODEL

# bge-m3 sorgu tarafinda talimat oneki istemez; soru oldugu gibi vektorlenir.
_COL = None


def _collection(db: str):
    global _COL
    if _COL is None:
        col = chromadb.PersistentClient(path=db, settings=chromadb.Settings(**CHROMA_SETTINGS)).get_collection(COLLECTION)
        built_with = (col.metadata or {}).get("embed_model")
        if built_with != EMBED_MODEL:
            # bge-m3 ve qwen3-embedding ikisi de 1024 boyutlu: uyumsuzluk hata vermez,
            # sessizce anlamsiz sonuc dondurur. Bu yuzden acikca durduruyoruz.
            sys.exit(f"HATA: indeks '{built_with}' ile olusturulmus, sorgu modeli '{EMBED_MODEL}'. "
                     f"Once 'python ingest.py' calistirin.")
        _COL = col
    return _COL


def search(question: str, k: int = 3, db: str = "data/chroma"):
    col = _collection(db)
    q = ollama.embed(model=EMBED_MODEL, input=[question])["embeddings"]
    r = col.query(query_embeddings=q, n_results=k)
    return list(zip(r["metadatas"][0], r["documents"][0], r["distances"][0]))


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Kullanici girdisi SQL sorgusuna f-string ile ekleniyor"
    print(f"Soru: {question}\n")
    for i, (meta, doc, dist) in enumerate(search(question), 1):
        print(f"{i}. {meta['section']}  (benzerlik {1 - dist:.2f}, parca {meta['chunk']})")
        print("   " + doc[:220].replace("\n", " ") + "...\n")

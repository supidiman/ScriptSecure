"""KodKalkan - bilgi tabanini (PDF) parcalayip vektorler ve ChromaDB'ye yazar.

Kullanim:
    python ingest.py                 # kb/ altindaki tum PDF'ler
    python ingest.py --dry-run       # Ollama'ya baglanmadan sadece parcalari gosterir
"""
import argparse
import hashlib
import pathlib
import re
import time

from pypdf import PdfReader

from config import CHROMA_SETTINGS, COLLECTION, EMBED_MODEL

MAX_CHARS = 1800      # cok uzun bolumler bu boyutta alt parcalara bolunur
OVERLAP = 200

FOOTER = re.compile(r"^KodKalkan · RAG bilgi taban.*$|^\d{1,3}$")
HEADING = re.compile(r"^(CWE-\d+(?: / CWE-\d+)?): ", re.M)
SECTION = re.compile(r"^\d\. (Bu doküman|Ajanın analiz|Kaynaklar, hedefler|Zayıflık sınıfları|Zararlı Kod)", re.M)


def pdf_text(path: pathlib.Path) -> str:
    lines = []
    for page in PdfReader(path).pages[1:]:     # 1. sayfa kapak + icindekiler
        for line in (page.extract_text() or "").splitlines():
            if not FOOTER.match(line.strip()):
                lines.append(line)
    return "\n".join(lines)


def split_sections(text: str):
    """Her CWE basligi ve her ana bolum (1., 2., ...) ayri parca olur."""
    cuts = sorted({m.start() for m in HEADING.finditer(text)} | {m.start() for m in SECTION.finditer(text)} | {0})
    cuts.append(len(text))
    for a, b in zip(cuts, cuts[1:]):
        block = text[a:b].strip()
        if len(block) < 80:
            continue
        m = HEADING.match(block)
        label = m.group(1) if m else block.splitlines()[0][:60]
        if len(block) <= MAX_CHARS:
            yield label, block
        else:
            for i in range(0, len(block), MAX_CHARS - OVERLAP):
                part = block[i:i + MAX_CHARS]
                # alt parcalarin da hangi CWE'ye ait oldugu belli olsun
                yield label, part if i == 0 else f"[{label} devam]\n{part}"


def main():
    ap = argparse.ArgumentParser(description="Bilgi tabanini indeksler")
    ap.add_argument("--kb", default="kb", help="PDF klasoru")
    ap.add_argument("--db", default="data/chroma", help="ChromaDB klasoru")
    ap.add_argument("--dry-run", action="store_true", help="Sadece parcalari goster")
    args = ap.parse_args()

    pdfs = sorted(pathlib.Path(args.kb).glob("*.pdf"))
    chunks = []
    for pdf in pdfs:
        for n, (label, body) in enumerate(split_sections(pdf_text(pdf))):
            chunks.append({"id": hashlib.sha256(f"{pdf.name}:{n}".encode()).hexdigest()[:16],
                           "text": body, "meta": {"source": pdf.name, "section": label, "chunk": n}})

    print(f"{len(pdfs)} PDF, {len(chunks)} parca")
    if args.dry_run:
        for c in chunks:
            print(f"  [{c['meta']['chunk']:>2}] {c['meta']['section']:<28} {len(c['text']):>5} karakter")
        return

    import chromadb
    import ollama

    client = chromadb.PersistentClient(path=args.db, settings=chromadb.Settings(**CHROMA_SETTINGS))
    try:
        client.delete_collection(COLLECTION)       # her calistirmada temiz indeks
    except Exception:
        pass
    col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine", "embed_model": EMBED_MODEL})

    t0 = time.time()
    for i in range(0, len(chunks), 16):
        batch = chunks[i:i + 16]
        emb = ollama.embed(model=EMBED_MODEL, input=[c["text"] for c in batch])["embeddings"]
        col.add(ids=[c["id"] for c in batch], documents=[c["text"] for c in batch],
                embeddings=emb, metadatas=[c["meta"] for c in batch])
    print(f"{col.count()} parca '{COLLECTION}' koleksiyonuna yazildi "
          f"({EMBED_MODEL}, boyut {len(emb[0])}, {time.time() - t0:.1f} sn)")


if __name__ == "__main__":
    main()

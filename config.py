"""KodKalkan - ekip genelinde ORTAK model ayarlari.

Ortak karar:
  * Gomme (embedding) modeli herkeste ayni olmak ZORUNDA: bge-m3
    (Farkli gomme modeliyle olusturulan indeks, sorgu vektorleriyle uyusmaz.)
  * Ekip qwen3:4b ile gelistirir. Karsilastirmada qwen3:8b daha iyi cikti
    (7/8 vs 6/8 tespit, dosya basina ~25 sn vs ~50 sn), demo 8b ile yapilir.
    4b ile calistirmak icin:  python agent.py --model qwen3:4b
"""
EMBED_MODEL = "bge-m3"
LLM_MODEL = "qwen3:8b"
COLLECTION = "kodkalkan_kb"

# Internetsiz ortam: ChromaDB'nin telemetri (internete veri gonderme) denemesini kapat.
CHROMA_SETTINGS = {"anonymized_telemetry": False}

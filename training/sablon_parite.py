"""KALKAN · Adım 7 · şablon parite testi (eğitim ↔ çalışma anı)          v1 · 2026-11-21
🧪 .spike/venv-mlx/bin/python training/sablon_parite.py     (eğitimden ÖNCE çalıştır)

Soru: MLX'in sohbet veri setinin (ChatDataset) modele verdiği token dizisi, llama-server'ın çalışma anında
(enable_thinking=false) ürettiği istem + hedef ile AYNI mı? Ve kayıp maskesi (mask_prompt) tam olarak hedef JSON'un
başından mı başlıyor?
  A  eğitim metni    = apply_chat_template(messages)                                  (MLX ChatDataset)
  M  maske ofseti    = apply_chat_template(messages[:-1], add_generation_prompt=True)   (MLX mask_prompt)
  P  çalışma istemi  = apply_chat_template(messages[:-1], add_generation_prompt=True, enable_thinking=False)
İdeal: A == P + hedef + bitiş  ve  M == P  →  model tam olarak çalışma anında üreteceği şeyi öğrenir.
"""
import json
import sys
from pathlib import Path

from transformers import AutoTokenizer

KOK = Path(__file__).resolve().parents[1]
tok = AutoTokenizer.from_pretrained(str(KOK / ".spike/base"))
ornek = json.loads(open(KOK / "data/sft/train.jsonl", encoding="utf-8").readline())
msg, hedef = ornek["messages"], ornek["messages"][-1]["content"]

A = tok.apply_chat_template(msg, tokenize=False)
M = tok.apply_chat_template(msg[:-1], tokenize=False, add_generation_prompt=True)
P = tok.apply_chat_template(msg[:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False)

def goster(ad, s):
    print(f"\n── {ad} (son 160 karakter) ──\n{s[-160:]!r}")

goster("P çalışma istemi", P)
goster("M maske ofseti", M)
print(f"\n── A eğitim metni, P'den sonrası ──\n{A[len(P):]!r}" if A.startswith(P) else "\n── A, P ile BAŞLAMIYOR ──")

sorunlar = []
if not A.startswith(P):
    sorunlar.append("Eğitim metni çalışma istemiyle başlamıyor → model farklı bir ön ek görerek eğitilir.")
elif not A[len(P):].lstrip().startswith(hedef):
    sorunlar.append(f"P ile hedef arasında fazladan metin var: {A[len(P):A.find(hedef)]!r}")
if M != P:
    fark = M[len(P):] if M.startswith(P) else (P[len(M):] if P.startswith(M) else "(farklı)")
    sorunlar.append(f"Maske ofseti çalışma isteminden farklı (fark: {fark!r}). Kayıp bu kısmı da öğretir ya da atlar.")

print("\nKARAR:")
if not sorunlar:
    print("  ✅ PARİTE TAM: eğitim = çalışma anı. mlx_lm lora sohbet formatı + mask_prompt güvenle kullanılabilir.")
else:
    for s in sorunlar:
        print("  ❌", s)
    print("  → Bu çıktıyı Claude'a gönder; eğitimden önce veri biçimi buna göre düzeltilecek.")
    sys.exit(1)

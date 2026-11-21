"""KALKAN · Adım 7 · kayıp (loss) eğrisi                                 v1.1 · 2026-11-21
🧪 python training/loss_egrisi.py training/logs/ft-0.8b-v1.log   → aynı adla .csv + .png (docs/img/'ye de kopyalanır)

mlx-lm log satırları, iki biçim:
  eski: "Iter 10: Train loss 1.234, …"   "Iter 50: Val loss 0.987, …"
  yeni (0.32 tablo):  "    10    1.174 ▼  18  1.8k"   "   150    val 0.224    62.62s"
v1.1: yeni tablo biçimi + ANSI/\r (ilerleme çubuğu) temizliği.
Görsel: tek eksen, iki seri (eğitim = düz mavi, doğrulama = kesikli turuncu + işaretçi → renk tek başına taşımaz),
doğrudan etiket + gösterge, sönük ızgara. Palet: dataviz referans paleti slot 1–2 (doğrulayıcıdan geçti).
"""
import csv
import re
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

MAVI, TURUNCU = "#2a78d6", "#eb6834"
YUZEY, MUREKKEP, IKINCIL, SONUK, IZGARA, EKSEN = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"


ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
ESKI_EGT = re.compile(r"Iter (\d+): Train loss ([\d.]+)")
ESKI_DOG = re.compile(r"Iter (\d+): Val loss ([\d.]+)")
YENI_DOG = re.compile(r"^\s*(\d+)\s+val\s+([\d.]+)")
YENI_EGT = re.compile(r"^\s*(\d+)\s+([\d.]+)\s*[▲▼=]?\s+\d+\s+[\d.]+k?\s*$")


def oku(log: Path):
    egitim, dogrulama = {}, {}
    metin = ANSI.sub("", log.read_text(encoding="utf-8", errors="replace")).replace("\r", "\n")
    for satir in metin.splitlines():
        if m := ESKI_EGT.search(satir) or YENI_EGT.match(satir):
            egitim[int(m.group(1))] = float(m.group(2))
        elif m := ESKI_DOG.search(satir) or YENI_DOG.match(satir):
            dogrulama[int(m.group(1))] = float(m.group(2))
    return sorted(egitim.items()), sorted(dogrulama.items())


def main() -> None:
    log = Path(sys.argv[1] if len(sys.argv) > 1 else "training/logs/ft-0.8b-v1.log")
    egitim, dogrulama = oku(log)
    if not egitim:
        raise SystemExit(f"{log}: eğitim kaybı satırı bulunamadı (log biçimi değişmiş olabilir)")
    with open(log.with_suffix(".csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["iter", "seri", "loss"])
        w.writerows([(i, "egitim", v) for i, v in egitim] + [(i, "dogrulama", v) for i, v in dogrulama])

    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=160, facecolor=YUZEY)
    ax.set_facecolor(YUZEY)
    ax.plot(*zip(*egitim), color=MAVI, lw=2, label="eğitim")
    if dogrulama:
        ax.plot(*zip(*dogrulama), color=TURUNCU, lw=2, ls="--", marker="o", ms=5, label="doğrulama",
                markeredgecolor=YUZEY, markeredgewidth=1.5)
        en_iyi = min(dogrulama, key=lambda x: x[1])
        ax.annotate(f"en düşük doğrulama {en_iyi[1]:.3f} (iter {en_iyi[0]})", xy=en_iyi, xytext=(0, 18),
                    textcoords="offset points", ha="center", fontsize=9, color=IKINCIL,
                    arrowprops={"arrowstyle": "-", "color": SONUK, "lw": 1})
    ust = max(v for _, v in egitim + dogrulama)
    yakin = dogrulama and abs(dogrulama[-1][1] - egitim[-1][1]) < 0.06 * ust     # uç etiketler çakışmasın
    if dogrulama:
        ax.annotate("doğrulama", xy=dogrulama[-1], xytext=(6, 7 if yakin else 0), textcoords="offset points",
                    va="center", fontsize=9, color=IKINCIL)
    ax.annotate("eğitim", xy=egitim[-1], xytext=(6, -7 if yakin else 0), textcoords="offset points", va="center",
                fontsize=9, color=IKINCIL)
    ax.set_title(f"Kayıp eğrisi · {log.stem}", loc="left", fontsize=12, color=MUREKKEP)
    ax.set_xlabel("iterasyon", color=SONUK, fontsize=9)
    ax.set_ylabel("kayıp (yalnızca asistan cevabı)", color=SONUK, fontsize=9)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color=IZGARA, lw=0.8)
    ax.tick_params(colors=SONUK, labelsize=8, length=0)
    for k in ("top", "right", "left"):
        ax.spines[k].set_visible(False)
    ax.spines["bottom"].set_color(EKSEN)
    ax.legend(frameon=False, fontsize=9, labelcolor=IKINCIL, loc="upper right")
    fig.tight_layout()
    png = log.with_suffix(".png")
    fig.savefig(png, facecolor=YUZEY)
    hedef = Path("docs/img")
    hedef.mkdir(parents=True, exist_ok=True)
    shutil.copy(png, hedef / png.name)
    son_e, son_d = egitim[-1][1], (dogrulama[-1][1] if dogrulama else None)
    print(f"{png} · son eğitim {son_e:.3f} · son doğrulama {son_d} · en iyi doğrulama "
          f"{min(dogrulama, key=lambda x: x[1]) if dogrulama else '—'}")


if __name__ == "__main__":
    main()

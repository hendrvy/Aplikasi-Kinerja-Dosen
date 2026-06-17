import tkinter as tk
from tkinter import messagebox
import numpy as np

# ─── Fuzzy Engine ──────────────────────────────────────────────────────────────
class FuzzyLecturerEvaluation:
    def __init__(self):
        self.x_kinerja = np.arange(0, 101, 1)

    def _trimf(self, x, abc):
        a, b, c = abc
        return np.maximum(0, np.minimum(
            (x - a) / (b - a) if b > a else 1,
            (c - x) / (c - b) if c > b else 1,
        ))

    def _trapmf(self, x, abcd):
        a, b, c, d = abcd
        res = np.zeros_like(x, dtype=float)
        for i, val in enumerate(x):
            if val <= a or val >= d:   res[i] = 0
            elif b <= val <= c:        res[i] = 1
            elif a < val < b:          res[i] = (val - a) / (b - a)
            elif c < val < d:          res[i] = (d - val) / (d - c)
        return res

    def fuzzify_kehadiran(self, v):
        a = np.array([v])
        return {"Rendah": self._trapmf(a,[0,0,65,75])[0],
                "Tinggi": self._trapmf(a,[70,80,100,100])[0]}

    def fuzzify_evaluasi(self, v):
        a = np.array([v])
        return {"Rendah": self._trapmf(a,[0,0,50,65])[0],
                "Sedang": self._trimf(a,[55,70,85])[0],
                "Tinggi": self._trapmf(a,[75,85,100,100])[0]}

    def fuzzify_penelitian(self, v):
        a = np.array([v])
        return {"Rendah": self._trapmf(a,[0,0,2,4])[0],
                "Sedang": self._trimf(a,[3,5,7])[0],
                "Tinggi": self._trapmf(a,[6,8,10,10])[0]}

    def fuzzify_pengabdian(self, v):
        a = np.array([v])
        return {"Rendah": self._trapmf(a,[0,0,2,4])[0],
                "Tinggi": self._trapmf(a,[3,5,10,10])[0]}

    def evaluate(self, kehadiran, evaluasi, penelitian, pengabdian):
        fk = self.fuzzify_kehadiran(kehadiran)
        fe = self.fuzzify_evaluasi(evaluasi)
        fp = self.fuzzify_penelitian(penelitian)
        fa = self.fuzzify_pengabdian(pengabdian)

        mu_k  = self._trapmf(self.x_kinerja, [0,0,40,55])
        mu_b  = self._trimf(self.x_kinerja,  [45,65,85])
        mu_sb = self._trapmf(self.x_kinerja, [75,85,100,100])

        ak = np.zeros_like(self.x_kinerja)
        ab = np.zeros_like(self.x_kinerja)
        asb= np.zeros_like(self.x_kinerja)

        ak  = np.maximum(ak,  np.minimum(fk["Rendah"], mu_k))
        asb = np.maximum(asb, np.minimum(min(fe["Tinggi"], fp["Tinggi"]), mu_sb))
        ak  = np.maximum(ak,  np.minimum(fe["Rendah"], mu_k))
        ab  = np.maximum(ab,  np.minimum(min(fk["Tinggi"], fe["Sedang"], fp["Sedang"]), mu_b))
        asb = np.maximum(asb, np.minimum(min(fk["Tinggi"], fe["Tinggi"], fa["Tinggi"]), mu_sb))
        ak  = np.maximum(ak,  np.minimum(min(fk["Tinggi"], fe["Sedang"], fp["Rendah"]), mu_k))
        ab  = np.maximum(ab,  np.minimum(min(fk["Tinggi"], fe["Tinggi"], fp["Sedang"]), mu_b))
        ab  = np.maximum(ab,  np.minimum(min(fk["Tinggi"], fe["Sedang"], fa["Tinggi"]), mu_b))
        ak  = np.maximum(ak,  np.minimum(min(fk["Tinggi"], fe["Rendah"], fa["Rendah"]), mu_k))

        agg = np.maximum(ak, np.maximum(ab, asb))
        sw  = np.sum(agg)
        skor = 50.0 if sw == 0 else np.sum(self.x_kinerja * agg) / sw

        if skor <= 50:   kategori = "KURANG"
        elif skor <= 80: kategori = "BAIK"
        else:            kategori = "SANGAT BAIK"

        return skor, kategori


# ─── Warna ─────────────────────────────────────────────────────────────────────
BG        = "#0f172a"
CARD      = "#1e293b"
CARD_HDR  = "#162032"
ENTRY_BG  = "#0f172a"
BORDER    = "#334155"
ACCENT    = "#4ade80"
TEXT_MAIN = "#f1f5f9"
TEXT_SUB  = "#94a3b8"
BTN_BG    = "#1d4ed8"
BTN_HOV   = "#2563eb"
RED_C     = "#ef4444"
ORG_C     = "#f97316"
GRN_C     = "#4ade80"


# ─── Widget lingkaran skor ──────────────────────────────────────────────────────
class ScoreRing(tk.Canvas):
    SIZE = 130
    PAD  = 12
    W    = 11

    def __init__(self, master, **kw):
        super().__init__(master, width=self.SIZE, height=self.SIZE,
                         bg=CARD, highlightthickness=0, **kw)
        self._target  = 0
        self._current = 0
        self._color   = ACCENT
        self._after_id = None
        self._render(0)

    def _render(self, pct):
        self.delete("all")
        s, p, w = self.SIZE, self.PAD, self.W
        # track
        self.create_arc(p, p, s-p, s-p, start=0, extent=359.9,
                        outline="#1e3a5f", width=w, style="arc")
        # filled arc
        if pct > 0:
            self.create_arc(p, p, s-p, s-p, start=90,
                            extent=-(pct/100)*359.9,
                            outline=self._color, width=w, style="arc")
        # centre text
        label = f"{pct:.0f}" if pct > 0 else "–"
        self.create_text(s//2, s//2 - 8, text=label,
                         font=("Segoe UI", 22, "bold"), fill=TEXT_MAIN)
        self.create_text(s//2, s//2 + 14, text="Score",
                         font=("Segoe UI", 8), fill=TEXT_SUB)

    def _animate(self):
        if abs(self._current - self._target) < 0.5:
            self._current = self._target
            self._render(self._current)
            return
        self._current += (self._target - self._current) * 0.15
        self._render(self._current)
        self._after_id = self.after(16, self._animate)

    def set_score(self, score, color=ACCENT):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._target = score
        self._color  = color
        self._animate()


# ─── Entry dengan placeholder ───────────────────────────────────────────────────
class PHEntry(tk.Entry):
    def __init__(self, master, placeholder="", **kw):
        kw.setdefault("bg", ENTRY_BG)
        kw.setdefault("fg", TEXT_MAIN)
        kw.setdefault("insertbackground", TEXT_MAIN)
        kw.setdefault("relief", tk.FLAT)
        kw.setdefault("font", ("Segoe UI", 10))
        kw.setdefault("bd", 0)
        super().__init__(master, **kw)
        self._ph = placeholder
        self._active = False
        self._show()
        self.bind("<FocusIn>",  self._clear)
        self.bind("<FocusOut>", self._show)

    def _show(self, *_):
        if not self.get():
            self.insert(0, self._ph)
            self.config(fg=TEXT_SUB)
            self._active = True

    def _clear(self, *_):
        if self._active:
            self.delete(0, tk.END)
            self.config(fg=TEXT_MAIN)
            self._active = False

    def value(self):
        return "" if self._active else self.get()


# ─── Aplikasi utama ─────────────────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root  = root
        self.root.title("App Kinerja Dosen")
        self.root.geometry("420x680")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.fuzzy = FuzzyLecturerEvaluation()
        self._build()

    # ── Build UI ─────────────────────────────────────────────────────────────
    def _build(self):
        # ── Header ──
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 6))
        tk.Label(hdr, text="App Kinerja Dosen", font=("Segoe UI", 9),
                 fg=TEXT_SUB, bg=BG).pack(anchor="w")
        tk.Label(hdr, text="Evaluasi Kinerja Dosen",
                 font=("Segoe UI", 16, "bold"), fg=TEXT_MAIN, bg=BG).pack(anchor="w")

        # ── Card input ──
        cin = tk.Frame(self.root, bg=CARD,
                       highlightbackground=BORDER, highlightthickness=1)
        cin.pack(fill="x", padx=20, pady=(6, 6))

        tk.Label(cin, text="Parameter Evaluasi",
                 font=("Segoe UI", 11, "bold"), fg=TEXT_MAIN, bg=CARD)\
            .pack(anchor="w", padx=16, pady=(14, 6))

        self.entries = {}
        fields = [
            ("Kehadiran (0–100 %)",        "Masukkan nilai persentase",    "kehadiran"),
            ("Evaluasi Mahasiswa (0–100)",  "Masukkan skor evaluasi",       "evaluasi"),
            ("Penelitian (0–10 item)",      "Jumlah publikasi/penelitian",  "penelitian"),
            ("Pengabdian (0–10 item)",      "Jumlah kegiatan pengabdian",   "pengabdian"),
        ]
        for lbl, ph, key in fields:
            self._make_field(cin, lbl, ph, key)

        # tombol
        self.btn = tk.Button(
            cin, text="⊞  Hitung Kinerja",
            font=("Segoe UI", 11, "bold"), fg="white", bg=BTN_BG,
            activebackground=BTN_HOV, activeforeground="white",
            relief=tk.FLAT, bd=0, cursor="hand2",
            command=self._hitung
        )
        self.btn.pack(fill="x", padx=16, pady=(10, 16), ipady=8)
        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=BTN_HOV))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=BTN_BG))

        # ── Card hasil (awalnya tersembunyi) ──
        self.result_card = tk.Frame(self.root, bg=CARD,
                                    highlightbackground=BORDER, highlightthickness=1)

        # Header kartu hasil
        rh = tk.Frame(self.result_card, bg=CARD_HDR)
        rh.pack(fill="x")
        tk.Label(rh, text="⊡  Hasil Evaluasi",
                 font=("Segoe UI", 10, "bold"), fg=TEXT_MAIN, bg=CARD_HDR)\
            .pack(anchor="w", padx=16, pady=10)

        # Isi kartu hasil — layout horizontal: ring kiri, teks kanan
        body = tk.Frame(self.result_card, bg=CARD)
        body.pack(fill="x", padx=16, pady=12)

        # Ring
        left = tk.Frame(body, bg=CARD)
        left.pack(side="left", padx=(0, 14))
        self.ring = ScoreRing(left)
        self.ring.pack()

        # Teks kanan
        right = tk.Frame(body, bg=CARD)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Skor Akhir (Crisp)",
                 font=("Segoe UI", 8), fg=TEXT_SUB, bg=CARD).pack(anchor="w")
        self.lbl_skor = tk.Label(right, text="–",
                 font=("Segoe UI", 22, "bold"), fg=TEXT_MAIN, bg=CARD)
        self.lbl_skor.pack(anchor="w")

        tk.Label(right, text="Kategori Kinerja",
                 font=("Segoe UI", 8), fg=TEXT_SUB, bg=CARD).pack(anchor="w", pady=(8,2))
        self.badge = tk.Label(right, text="–",
                 font=("Segoe UI", 11, "bold"), fg=BG, bg=TEXT_SUB,
                 padx=14, pady=4)
        self.badge.pack(anchor="w")

        self.lbl_desc = tk.Label(self.result_card, text="",
                 font=("Segoe UI", 8), fg=TEXT_SUB, bg=CARD,
                 wraplength=360, justify="left")
        self.lbl_desc.pack(anchor="w", padx=16, pady=(0, 14))

    def _make_field(self, parent, label, ph, key):
        f = tk.Frame(parent, bg=CARD)
        f.pack(fill="x", padx=16, pady=4)
        tk.Label(f, text=label, font=("Segoe UI", 8, "bold"),
                 fg=TEXT_MAIN, bg=CARD).pack(anchor="w")
        wrap = tk.Frame(f, bg=BORDER)
        wrap.pack(fill="x", pady=(3,0))
        inner = tk.Frame(wrap, bg=ENTRY_BG)
        inner.pack(fill="x", padx=1, pady=1)
        e = PHEntry(inner, placeholder=ph)
        e.pack(fill="x", ipady=6, padx=8)
        self.entries[key] = e

    # ── Logika ───────────────────────────────────────────────────────────────
    def _hitung(self):
        try:
            keh = float(self.entries["kehadiran"].value())
            eva = float(self.entries["evaluasi"].value())
            pen = float(self.entries["penelitian"].value())
            pab = float(self.entries["pengabdian"].value())
        except ValueError:
            messagebox.showerror("Format Salah",
                "Harap isi semua kolom dengan angka yang valid!")
            return

        if not (0<=keh<=100 and 0<=eva<=100 and 0<=pen<=10 and 0<=pab<=10):
            messagebox.showerror("Error Input",
                "Nilai berada di luar range yang diizinkan!")
            return

        skor, kategori = self.fuzzy.evaluate(keh, eva, pen, pab)

        color_map = {"KURANG": RED_C, "BAIK": ORG_C, "SANGAT BAIK": GRN_C}
        desc_map  = {
            "KURANG":      "Kinerja dosen perlu ditingkatkan secara signifikan.",
            "BAIK":        "Kinerja dosen sudah baik dan perlu dipertahankan.",
            "SANGAT BAIK": "Berdasarkan inferensi Mamdani, kinerja dosen berada dalam kategori prima.",
        }
        col = color_map.get(kategori, TEXT_SUB)

        # Update ring dengan animasi
        self.ring.set_score(skor, color=col)

        # Update label
        self.lbl_skor.config(text=f"{skor:.2f}")
        self.badge.config(text=f"  {kategori}  ", bg=col,
                          fg="#0f172a" if kategori == "SANGAT BAIK" else "white")
        self.lbl_desc.config(text=desc_map.get(kategori, ""))

        # Tampilkan kartu hasil jika belum tampil
        if not self.result_card.winfo_ismapped():
            self.result_card.pack(fill="x", padx=20, pady=(0, 20))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()

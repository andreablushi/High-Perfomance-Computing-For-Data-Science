import pandas as pd
import matplotlib.pyplot as plt
import os
import subprocess
from io import StringIO

FILES = {
    "HTHISEND": "/home/blushi/HPC/High-Perfomance-Computing-For-Data-Science/homework/benchmarking/HTHISEND.csv",
    "ISEND":     "/home/blushi/HPC/High-Perfomance-Computing-For-Data-Science/homework/benchmarking/ISEND.csv",
    "SSEND":     "/home/blushi/HPC/High-Perfomance-Computing-For-Data-Science/homework/benchmarking/SSEND.csv",
}

def read_send_csv(path):
    # leggi e rimuovi righe di commento (es. "// ...", "# ...") e vuote
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    filtered = []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith('//') or s.startswith('#'):
            continue
        filtered.append(ln)
    if not filtered:
        raise RuntimeError(f"Nessuna riga valida trovata in {path}")
    text = ''.join(filtered)

    # prova prima con separatore tab (preserva header con spazi come "time (sec)")
    seps = [r'\t+', r'\t', r'\s+']
    df = None
    used_sep = None
    for sep in seps:
        try:
            df_try = pd.read_csv(StringIO(text), sep=sep, engine='python', header=0)
            cols = [c.strip() for c in df_try.columns.tolist()]
            # accettiamo se troviamo almeno una colonna "n" e una contenente "rate"
            if any(c.lower() == 'n' for c in cols) and any('rate' in c.lower() for c in cols):
                df = df_try
                used_sep = sep
                break
            # anche se non trova "rate", se le colonne sono esattamente 4 (Kind,n,time...,rate...) accettiamo
            if len(cols) == 4:
                df = df_try
                used_sep = sep
                break
        except Exception:
            continue

    # se nessuno ha funzionato, prova comunque l'ultima lettura per diagnostica
    if df is None:
        df = pd.read_csv(StringIO(text), sep=seps[-1], engine='python', header=0)
        used_sep = seps[-1]

    df.columns = [c.strip() for c in df.columns]

    print(f"\n==> {os.path.basename(path)}: righe_totali={len(lines)}, righe_utili={len(filtered)}, sep_used='{used_sep}'")
    print("Colonne raw:", df.columns.tolist())
    print("Prime righe:")
    print(df.head().to_string(index=False))

    # normalizza Kind
    if 'Kind' in df.columns:
        df['Kind'] = df['Kind'].astype(str).str.strip()

    # trova colonna Rate (es. "Rate", "Rate (MB/sec)", "(MB/sec)" ecc.)
    rate_col = None
    for c in df.columns:
        if 'rate' in c.lower():
            rate_col = c
            break
    # se non trovata, cerca token "(mb/sec)" e unisci con colonna precedente
    if rate_col is None:
        cols = list(df.columns)
        for i, c in enumerate(cols):
            if c.strip().startswith('(mb/sec)'.lower()) or c.strip().startswith('(mb/sec)'):
                if i > 0:
                    newname = cols[i-1] + ' ' + cols[i]
                    # rinomina le colonne coinvolte
                    df.rename(columns={cols[i-1]: newname, cols[i]: newname}, inplace=True)
        # rifai la ricerca
        for c in df.columns:
            if 'rate' in c.lower():
                rate_col = c
                break

    # fallback: se ci sono colonne duplicate o parti '(sec)' unirle nel nome
    if rate_col is None:
        # unisci parti di intestazione che iniziano per '(' con la precedente
        cols = list(df.columns)
        new_cols = []
        i = 0
        while i < len(cols):
            col = cols[i]
            if col.startswith('(') and new_cols:
                new_cols[-1] = new_cols[-1] + ' ' + col
            else:
                new_cols.append(col)
            i += 1
        # se il conteggio cambia, assegna i nuovi nomi
        if len(new_cols) == len(cols):
            df.columns = new_cols
        else:
            # tenta un'unione più aggressiva: combina coppie consecutive quando necessario
            merged = []
            i = 0
            while i < len(cols):
                if i+1 < len(cols) and cols[i+1].startswith('('):
                    merged.append(cols[i] + ' ' + cols[i+1])
                    i += 2
                else:
                    merged.append(cols[i])
                    i += 1
            # se la lunghezza risultante è plausibile (4 colonne), ricostruisci DataFrame scegliendo colonne appropriate
            if len(merged) <= len(cols):
                # ricostruisci df scegliendo la prima colonna di ogni coppia come valore (funziona per molti file tabulari)
                groups = []
                i = 0
                while i < len(cols):
                    if i+1 < len(cols) and cols[i+1].startswith('('):
                        groups.append([cols[i], cols[i+1]])
                        i += 2
                    else:
                        groups.append([cols[i]])
                        i += 1
                df2 = pd.DataFrame()
                for g in groups:
                    # preferisci la prima colonna del gruppo come valore
                    df2[' '.join(g)] = df[g[0]]
                df = df2
                df.columns = [c.strip() for c in df.columns]

    # rinomina qualsivoglia colonna contenente 'rate' in modo consistente
    for c in df.columns:
        if 'rate' in c.lower():
            df.rename(columns={c: 'Rate (MB/sec)'}, inplace=True)
            break

    # rinomina 'time' se necessario
    time_col = None
    for c in df.columns:
        if 'time' in c.lower():
            time_col = c
            break
    if time_col and time_col != 'time (sec)':
        df.rename(columns={time_col: 'time (sec)'}, inplace=True)

    # assicurati tipi numerici
    if 'n' in df.columns:
        df['n'] = pd.to_numeric(df['n'], errors='coerce')
    if 'Rate (MB/sec)' in df.columns:
        df['Rate (MB/sec)'] = pd.to_numeric(df['Rate (MB/sec)'], errors='coerce')
    if 'time (sec)' in df.columns:
        df['time (sec)'] = pd.to_numeric(df['time (sec)'], errors='coerce')

    # diagnostica valori null
    if 'n' in df.columns and df['n'].isna().any():
        print("Attenzione: valori non numerici in 'n' trovati:", df[df['n'].isna()])
    if 'Rate (MB/sec)' in df.columns and df['Rate (MB/sec)'].isna().any():
        print("Attenzione: valori non numerici in 'Rate (MB/sec)' trovati:", df[df['Rate (MB/sec)'].isna()])

    print("Colonne finali:", df.columns.tolist())
    return df

def plot_files(files):
    plt.figure(figsize=(9,6))
    any_plotted = False
    for label, path in files.items():
        if not os.path.exists(path):
            print(f"File non trovato: {path}")
            continue
        try:
            df = read_send_csv(path)
        except Exception as e:
            print(f"Errore leggendo {path}: {e}")
            continue
        if 'n' in df.columns:
            df = df.sort_values('n')
        if 'n' in df.columns and 'Rate (MB/sec)' in df.columns:
            any_plotted = True
            if 'Kind' in df.columns:
                for kind, grp in df.groupby('Kind'):
                    plt.plot(grp['n'], grp['Rate (MB/sec)'], marker='o', linestyle='-', label=f"{label} - {kind}")
            else:
                plt.plot(df['n'], df['Rate (MB/sec)'], marker='o', linestyle='-', label=label)
        else:
            print(f"Colonne mancanti per il plot in {path}: {df.columns.tolist()}")

    if not any_plotted:
        print("Nessuna serie valida per il plot. Controlla i CSV.")
        return

    plt.xscale('log', base=2)
    plt.xlabel('n (bytes)')
    plt.ylabel('Rate (MB/sec)')
    plt.title('Confronto throughput')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(list(files.values())[0]), 'send_rates_comparison.png')
    plt.savefig(out_png, dpi=150)
    print(f"Plot salvato in: {out_png}")

    try:
        if os.environ.get('DISPLAY'):
            subprocess.Popen(['xdg-open', out_png], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("DISPLAY non impostata: immagine salvata ma non aperta (headless).")
    except Exception as e:
        print("Impossibile aprire il file con xdg-open:", e)
    finally:
        plt.close()

if __name__ == "__main__":
    plot_files(FILES)
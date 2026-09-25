import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np
import os
import platform
import subprocess

# ─────────────────────────────────────────
# 1. КОМПЬЮТЕРИЙН МЭДЭЭЛЭЛ
# ─────────────────────────────────────────

def get_system_info():
    info = {}
    info['os'] = platform.system() + ' ' + platform.release()
    info['python'] = platform.python_version()

    # CPU нэр
    try:
        if platform.system() == 'Linux':
            result = subprocess.check_output(
                "cat /proc/cpuinfo | grep 'model name' | head -1",
                shell=True
            ).decode().strip()
            info['cpu'] = result.split(':')[-1].strip()
        elif platform.system() == 'Windows':
            result = subprocess.check_output(
                'wmic cpu get Name', shell=True
            ).decode().strip().split('\n')[-1].strip()
            info['cpu'] = result
        else:
            info['cpu'] = platform.processor()
    except Exception:
        info['cpu'] = platform.processor() or 'Unknown'

    # CPU цөмийн тоо
    try:
        import psutil
        info['physical_cores'] = psutil.cpu_count(logical=False)
        info['logical_cores']  = psutil.cpu_count(logical=True)
        mem = psutil.virtual_memory()
        info['ram_gb'] = round(mem.total / (1024 ** 3), 1)
    except ImportError:
        import multiprocessing
        info['physical_cores'] = multiprocessing.cpu_count()
        info['logical_cores']  = multiprocessing.cpu_count()
        info['ram_gb'] = 'N/A (pip install psutil)'

    return info

# ─────────────────────────────────────────
# 2. ӨГӨГДӨЛ УНШИХ
# ─────────────────────────────────────────

base_path = '/home/detsu/Documents/vscode/Parallel-programming/lab1/csv/'

def get_threads_speedup(mode):
    seq_file = os.path.join(base_path, f'csvsequential_{mode}.csv')
    th_file  = os.path.join(base_path, f'csvthreads_{mode}.csv')

    df_seq = pd.read_csv(seq_file)
    df_th  = pd.read_csv(th_file)

    t_seq   = df_seq['elapsed_ms'].mean()
    avg_th  = df_th.groupby('threads')['elapsed_ms'].mean()
    speedup = t_seq / avg_th
    return speedup, t_seq, avg_th

speedup_bal,  t_seq_bal,  avg_th_bal  = get_threads_speedup('performance')   # balanced горим
speedup_perf, t_seq_perf, avg_th_perf = get_threads_speedup('balanced')       # performance горим

# ─────────────────────────────────────────
# 3. ЯЛГААНЫ ТАЙЛБАР (текст)
# ─────────────────────────────────────────

def print_analysis(speedup_bal, speedup_perf, t_seq_bal, t_seq_perf):
    print("=" * 65)
    print("         BALANCED vs PERFORMANCE ГОРИМЫН ХАРЬЦУУЛАЛТ")
    print("=" * 65)

    max_th = min(speedup_bal.index.max(), speedup_perf.index.max())
    sb_max = speedup_bal[max_th]
    sp_max = speedup_perf[max_th]

    print(f"\n📌 Sequential суурь хугацаа:")
    print(f"   Balanced  горимын seq  : {t_seq_bal:.2f} ms")
    print(f"   Performance горимын seq: {t_seq_perf:.2f} ms")

    print(f"\n📌 {max_th} thread дээрх speedup:")
    print(f"   Balanced   : {sb_max:.2f}x")
    print(f"   Performance: {sp_max:.2f}x")

    winner = "Performance" if sp_max > sb_max else "Balanced"
    diff   = abs(sp_max - sb_max)
    print(f"\n✅ Илүү хурдан горим ({max_th} thread): {winner} (+{diff:.2f}x давуу)")

    print("\n📖 ТАЙЛБАР:")
    print("""
  ┌─────────────────┬────────────────────────────────────────────────┐
  │ BALANCED горим  │ CPU-ийн давтамж болон хүчдлийг тэнцвэртэй      │
  │                 │ барьж, халуун болон батарей хэрэглээг хянана.   │
  │                 │ → Оффис, суурин ажил, серверт тохиромжтой.     │
  ├─────────────────┼────────────────────────────────────────────────┤
  │ PERFORMANCE     │ CPU-ийг дээд давтамж дээр ажиллуулж, Turbo     │
  │ горим           │ Boost идэвхжүүлнэ. Халалт ихсэж болно.         │
  │                 │ → Тооцоолол шаардсан ажил, render, sim-д сайн. │
  └─────────────────┴────────────────────────────────────────────────┘

  Яагаад speedup ялгаатай вэ?
  • Performance горимд CPU өндөр давтамжтай учир sequential суурь
    хугацаа богино байдаг → speedup харьцангуй өөр харагдана.
  • Balanced горимд CPU throttle хийгдсэн үед олон thread ашиглах нь
    нэгж цагт илүү ажил гүйцэтгэж, харьцангуй өндөр speedup өгнө.
  • Ideal speedup (y=x шугам)-аас хол байх нь thread overhead,
    cache contention, эсвэл synchronization хойшлолт байгааг илтгэнэ.
""")

# ─────────────────────────────────────────
# 4. КОМПЬЮТЕРИЙН МЭДЭЭЛЭЛ ХЭВЛЭХ
# ─────────────────────────────────────────

sys_info = get_system_info()

print("\n" + "=" * 65)
print("               КОМПЬЮТЕРИЙН МЭДЭЭЛЭЛ")
print("=" * 65)
print(f"  🖥️  CPU    : {sys_info['cpu']}")
print(f"  🔢  Физик цөм  : {sys_info['physical_cores']}")
print(f"  🔢  Логик цөм  : {sys_info['logical_cores']}")
print(f"  💾  RAM    : {sys_info['ram_gb']} GB")
print(f"  🖱️  OS     : {sys_info['os']}")
print(f"  🐍  Python : {sys_info['python']}")
print("=" * 65 + "\n")

print_analysis(speedup_bal, speedup_perf, t_seq_bal, t_seq_perf)

# ─────────────────────────────────────────
# 5. ГРАФИК
# ─────────────────────────────────────────

fig = plt.figure(figsize=(14, 10), facecolor='#0f1117')
fig.patch.set_facecolor('#0f1117')

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

ax_main = fig.add_subplot(gs[0, :])   # Дээр: гол speedup
ax_time = fig.add_subplot(gs[1, 0])   # Доор зүүн: хугацаа
ax_eff  = fig.add_subplot(gs[1, 1])   # Доор баруун: efficiency

COLOR_BG    = '#0f1117'
COLOR_PANEL = '#1a1d27'
COLOR_GREEN = '#00e676'
COLOR_ORG   = '#ff9100'
COLOR_IDEAL = '#ffffff'
COLOR_TEXT  = '#e0e0e0'
COLOR_GRID  = '#2a2d3a'

for ax in [ax_main, ax_time, ax_eff]:
    ax.set_facecolor(COLOR_PANEL)
    ax.tick_params(colors=COLOR_TEXT, labelsize=9)
    ax.spines['bottom'].set_color(COLOR_GRID)
    ax.spines['left'].set_color(COLOR_GRID)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.3, color=COLOR_GRID)
    ax.title.set_color(COLOR_TEXT)
    ax.xaxis.label.set_color(COLOR_TEXT)
    ax.yaxis.label.set_color(COLOR_TEXT)

# ── Гол график ──
threads = speedup_bal.index
ax_main.fill_between(threads, speedup_bal,  alpha=0.15, color=COLOR_GREEN)
ax_main.fill_between(threads, speedup_perf, alpha=0.15, color=COLOR_ORG)
ax_main.plot(threads, speedup_bal,  marker='o', label='Balanced Mode',    color=COLOR_GREEN, linewidth=2.5, markersize=7)
ax_main.plot(threads, speedup_perf, marker='s', label='Performance Mode', color=COLOR_ORG,   linewidth=2.5, markersize=7)
ax_main.plot(threads, threads,      'k--',       label='Ideal Speedup',    color=COLOR_IDEAL, linewidth=1.5, alpha=0.4)

for x, yb, yp in zip(threads, speedup_bal, speedup_perf):
    ax_main.annotate(f'{yb:.1f}x', (x, yb), textcoords='offset points',
                     xytext=(0, 8), ha='center', fontsize=8, color=COLOR_GREEN)
    ax_main.annotate(f'{yp:.1f}x', (x, yp), textcoords='offset points',
                     xytext=(0, -15), ha='center', fontsize=8, color=COLOR_ORG)

ax_main.set_title('Threads Speedup: Balanced vs Performance', fontsize=14, fontweight='bold', pad=12)
ax_main.set_xlabel('Thread тоо')
ax_main.set_ylabel('Speedup (× дахин)')
ax_main.legend(facecolor=COLOR_PANEL, edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, fontsize=9)

# ── Тайлбарын хэсэг (текст panel) ──
ax_time.axis('off')

max_th  = min(speedup_bal.index.max(), speedup_perf.index.max())
sb_max  = speedup_bal[max_th]
sp_max  = speedup_perf[max_th]
winner  = "Performance" if sp_max > sb_max else "Balanced"
diff    = abs(sp_max - sb_max)
eff_b   = (speedup_bal[max_th]  / max_th) * 100
eff_p   = (speedup_perf[max_th] / max_th) * 100

title_props  = dict(fontsize=10.5, fontweight='bold', color=COLOR_TEXT,
                    transform=ax_time.transAxes, va='top')
body_props   = dict(fontsize=8.5,  color='#b0b8cc',
                    transform=ax_time.transAxes, va='top', linespacing=1.7)
accent_green = dict(fontsize=8.5,  color=COLOR_GREEN,
                    transform=ax_time.transAxes, va='top', fontweight='bold')
accent_org   = dict(fontsize=8.5,  color=COLOR_ORG,
                    transform=ax_time.transAxes, va='top', fontweight='bold')

ax_time.text(0.0, 1.00, '⚡ BALANCED  горим', **title_props)
ax_time.text(0.0, 0.90,
    '• CPU давтамжийг автоматаар хянаж,\n'
    '  халалт болон эрчим хүч хэмнэнэ.\n'
    '• Thread нэмэх тусам CPU throttle\n'
    '  хийгддэггүй учир харьцангуй\n'
    '  тогтвортой speedup өгнө.\n'
    '• Серверийн урт хугацааны ачааллд\n'
    '  тохиромжтой.',
    **body_props)

ax_time.text(0.0, 0.52, '🔥 PERFORMANCE  горим', **title_props)
ax_time.text(0.0, 0.42,
    '• Turbo Boost идэвхтэй, CPU дээд\n'
    '  давтамж дээр ажиллана.\n'
    '• Sequential суурь хугацаа богино\n'
    '  → speedup тооцоо өөрчлөгдөнө.\n'
    '• Олон thread дээр thermal throttle\n'
    '  тохиолдвол speedup унана.\n'
    '• Богино, эрч хүчтэй тооцоололд сайн.',
    **body_props)

ax_time.text(0.0, 0.04,
    f'★  {max_th} thread: {winner} горим {diff:.2f}x давуу  '
    f'| Eff — Bal: {eff_b:.0f}%  Perf: {eff_p:.0f}%',
    fontsize=8, color='#ffee58', fontweight='bold',
    transform=ax_time.transAxes, va='bottom',
    bbox=dict(facecolor='#22263a', edgecolor='#ffee5855', boxstyle='round,pad=0.35'))

ax_time.set_title('Горимын тайлбар', fontsize=11, fontweight='bold', color=COLOR_TEXT, pad=8)

# ── Efficiency = Speedup / threads ──
eff_bal  = speedup_bal  / threads
eff_perf = speedup_perf / threads
ax_eff.plot(threads, eff_bal  * 100, marker='o', color=COLOR_GREEN, linewidth=2.5, markersize=7, label='Balanced')
ax_eff.plot(threads, eff_perf * 100, marker='s', color=COLOR_ORG,   linewidth=2.5, markersize=7, label='Performance')
ax_eff.axhline(100, color=COLOR_IDEAL, linestyle='--', linewidth=1.5, alpha=0.4, label='Ideal (100%)')
ax_eff.set_title('Parallel Efficiency (%)', fontsize=11, fontweight='bold')
ax_eff.set_xlabel('Thread тоо')
ax_eff.set_ylabel('Efficiency (%)')
ax_eff.legend(facecolor=COLOR_PANEL, edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, fontsize=8)

# ── Системийн мэдээлэл (баруун дээд) ──
sys_text = (
    f"🖥  {sys_info['cpu']}\n"
    f"Физик цөм: {sys_info['physical_cores']}  |  Логик: {sys_info['logical_cores']}\n"
    f"RAM: {sys_info['ram_gb']} GB  |  OS: {sys_info['os']}"
)
fig.text(0.5, 0.965, sys_text, ha='center', va='top', fontsize=8.5,
         color='#aaaaaa', style='italic',
         bbox=dict(facecolor='#1a1d27', edgecolor='#2a2d3a', boxstyle='round,pad=0.4'))

output_path = 'threads_speedup_analysis.png'
plt.savefig(output_path, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\n✅ График '{output_path}' нэрээр хадгалагдлаа.")
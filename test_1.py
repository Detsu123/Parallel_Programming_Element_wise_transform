import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os

base_path = './csv/'

# ── Өгөгдөл унших ──
df_t  = pd.read_csv(os.path.join(base_path, 'csvtransposed_omp.csv'))
df_nt = pd.read_csv(os.path.join(base_path, 'csvno_transpose_omp.csv'))

avg_t  = df_t.groupby('threads')['elapsed_ms'].mean()
avg_nt = df_nt.groupby('threads')['elapsed_ms'].mean()

# Sequential суурь: 1 thread-ийн no_transpose утга
t_seq = avg_nt[1]

speedup_t  = t_seq / avg_t
speedup_nt = t_seq / avg_nt

threads = avg_t.index

# ── Консол тайлбар ──
print("=" * 60)
print("   TRANSPOSE  vs  NO-TRANSPOSE  (OpenMP)")
print("=" * 60)
print(f"\n{'Threads':<10} {'Transposed (ms)':<20} {'No-Transpose (ms)':<20} {'Хурдасгал %'}")
print("-" * 60)
for t in threads:
    gain = (avg_nt[t] - avg_t[t]) / avg_nt[t] * 100
    print(f"{t:<10} {avg_t[t]:<20.1f} {avg_nt[t]:<20.1f} {gain:+.1f}%")

print("\n📖 ТАЙЛБАР:")
print("""
  Transpose хийсэн тохиолдолд:
  • B матрицын баганад биш МӨРӨНД хандана (row-major)
  • CPU cache miss эрс буурна → L1/L2 cache-г үр ашигтай ашиглана
  • Thread тус бүр тасралтгүй санах ойн хэсгийг уншина

  Transpose хийгээгүй тохиолдолд:
  • B[k][j] — k өөрчлөгдөх тусам санах ойн алгасалт (stride = n)
  • Cache line дахин дахин дуусч, RAM-аас татах болно
  • Thread тоо нэмсэн ч cache bottleneck-ийг давж чадахгүй
""")

# ── График ──
COLOR_BG    = '#0f1117'
COLOR_PANEL = '#1a1d27'
COLOR_BLUE  = '#40c4ff'
COLOR_RED   = '#ff5252'
COLOR_IDEAL = '#ffffff'
COLOR_TEXT  = '#e0e0e0'
COLOR_GRID  = '#2a2d3a'

fig = plt.figure(figsize=(14, 9), facecolor=COLOR_BG)
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

ax_sp  = fig.add_subplot(gs[0, :])   # Speedup (том)
ax_ms  = fig.add_subplot(gs[1, 0])   # Хугацаа (ms)
ax_txt = fig.add_subplot(gs[1, 1])   # Тайлбар

for ax in [ax_sp, ax_ms]:
    ax.set_facecolor(COLOR_PANEL)
    ax.tick_params(colors=COLOR_TEXT, labelsize=9)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']: ax.spines[sp].set_color(COLOR_GRID)
    ax.grid(True, linestyle='--', alpha=0.3, color=COLOR_GRID)
    ax.title.set_color(COLOR_TEXT)
    ax.xaxis.label.set_color(COLOR_TEXT)
    ax.yaxis.label.set_color(COLOR_TEXT)

ax_txt.set_facecolor(COLOR_PANEL)
ax_txt.axis('off')
for sp in ax_txt.spines.values(): sp.set_color(COLOR_GRID)

# ── Speedup ──
ax_sp.fill_between(threads, speedup_t,  alpha=0.12, color=COLOR_BLUE)
ax_sp.fill_between(threads, speedup_nt, alpha=0.12, color=COLOR_RED)
ax_sp.plot(threads, speedup_t,  marker='o', color=COLOR_BLUE, linewidth=2.5, markersize=7, label='Transposed (cache-friendly)')
ax_sp.plot(threads, speedup_nt, marker='s', color=COLOR_RED,  linewidth=2.5, markersize=7, label='No-Transpose (cache-unfriendly)')
ax_sp.plot(threads, threads,    linestyle='--', color=COLOR_IDEAL, linewidth=1.5, alpha=0.35, label='Ideal Speedup')

for x, yt, yn in zip(threads, speedup_t, speedup_nt):
    ax_sp.annotate(f'{yt:.1f}x', (x, yt), textcoords='offset points', xytext=(0, 8),  ha='center', fontsize=8, color=COLOR_BLUE)
    ax_sp.annotate(f'{yn:.1f}x', (x, yn), textcoords='offset points', xytext=(0,-14), ha='center', fontsize=8, color=COLOR_RED)

ax_sp.set_title('OpenMP Speedup: Transposed vs No-Transpose', fontsize=14, fontweight='bold', pad=12)
ax_sp.set_xlabel('Thread тоо')
ax_sp.set_ylabel('Speedup (× дахин)')
ax_sp.legend(facecolor=COLOR_PANEL, edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, fontsize=9)

# ── Хугацаа (ms) bar ──
w = 0.35
ax_ms.bar(threads - w/2, avg_t,  width=w, color=COLOR_BLUE, alpha=0.85, label='Transposed')
ax_ms.bar(threads + w/2, avg_nt, width=w, color=COLOR_RED,  alpha=0.85, label='No-Transpose')
for x, yt, yn in zip(threads, avg_t, avg_nt):
    ax_ms.text(x - w/2, yt + 1, f'{yt:.0f}', ha='center', fontsize=7.5, color=COLOR_BLUE)
    ax_ms.text(x + w/2, yn + 1, f'{yn:.0f}', ha='center', fontsize=7.5, color=COLOR_RED)
ax_ms.set_title('Дундаж гүйцэтгэлийн хугацаа (ms)', fontsize=11, fontweight='bold')
ax_ms.set_xlabel('Thread тоо')
ax_ms.set_ylabel('ms')
ax_ms.legend(facecolor=COLOR_PANEL, edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, fontsize=8)

# ── Тайлбар panel ──
tp = dict(transform=ax_txt.transAxes, va='top')
ax_txt.text(0.0, 1.00, '🔵 Transposed — cache-friendly', fontsize=10.5, fontweight='bold', color=COLOR_BLUE, **tp)
ax_txt.text(0.0, 0.90,
    '• B матрицыг урьдчилан эргүүлнэ\n'
    '• Дотоод давталт мөр дагуу уншина\n'
    '• L1/L2 cache-г бүрэн ашиглана\n'
    '• Thread-үүд cache miss-гүй ажиллана',
    fontsize=8.8, color='#b0c8e8', linespacing=1.75, **tp)

ax_txt.text(0.0, 0.55, '🔴 No-Transpose — cache-unfriendly', fontsize=10.5, fontweight='bold', color=COLOR_RED, **tp)
ax_txt.text(0.0, 0.44,
    '• B[k][j]: k өөрчлөгдөхөд алгасан унших\n'
    '• Санах ойн stride = n × 8 байт\n'
    '• Cache line байнга шинэчлэгдэнэ\n'
    '• Thread нэмэх ч bottleneck хэвээр',
    fontsize=8.8, color='#e8b0b0', linespacing=1.75, **tp)

# Хамгийн их thread дээрх хурдасгалын хувь
max_t   = threads.max()
gain_pct = (avg_nt[max_t] - avg_t[max_t]) / avg_nt[max_t] * 100
ax_txt.text(0.0, 0.06,
    f'★  {max_t} thread дээр Transposed {gain_pct:.1f}% хурдан',
    fontsize=8.5, color='#ffee58', fontweight='bold',
    transform=ax_txt.transAxes, va='bottom',
    bbox=dict(facecolor='#22263a', edgecolor='#ffee5855', boxstyle='round,pad=0.35'))

ax_txt.set_title('Cache ашиглалтын тайлбар', fontsize=11, fontweight='bold', color=COLOR_TEXT, pad=8)

plt.savefig('transpose_vs_notranspose.png', dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
print("\n✅ График 'transpose_vs_notranspose.png' хадгалагдлаа.")
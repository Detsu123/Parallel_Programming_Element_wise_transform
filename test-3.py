import pandas as pd
import matplotlib.pyplot as plt
import os

# Таны CSV файлуудын байршил
base_path = '/home/detsu/Documents/vscode/Parallel-programming/lab1/csv/'

# Файлуудыг унших функц
def get_threads_speedup(mode):
    # Sequential файл нь threads болон openmp-д адилхан тул үүнийг ашиглана
    seq_file = os.path.join(base_path, f'csvsequential_{mode}.csv')
    th_file = os.path.join(base_path, f'csvthreads_{mode}.csv')
    
    df_seq = pd.read_csv(seq_file)
    df_th = pd.read_csv(th_file)
    
    # Sequential-ийн дундаж хугацаа
    t_seq = df_seq['elapsed_ms'].mean()
    
    # Threads-ийн дундаж хугацаа (thread тус бүрээр)
    avg_th = df_th.groupby('threads')['elapsed_ms'].mean()
    
    # Speedup = Sequential / Parallel
    speedup = t_seq / avg_th
    return speedup

# Өгөгдлүүдийг авах
speedup_bal = get_threads_speedup('performance')
speedup_perf = get_threads_speedup('balanced')

# График зурах
plt.figure(figsize=(10, 6))

plt.plot(speedup_bal.index, speedup_bal, marker='o', label='Balanced Mode', color='green', linewidth=2)
plt.plot(speedup_perf.index, speedup_perf, marker='s', label='Performance Mode', color='orange', linewidth=2)

# Ideal speedup (шулуун шугам)
plt.plot(speedup_bal.index, speedup_bal.index, 'k--', label='Ideal Speedup', alpha=0.5)

plt.title('Threads Speedup Comparison')
plt.xlabel('Number of Threads')
plt.ylabel('Speedup (x times)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)

# Зураг болгон хадгалах
plt.savefig('threads_speedup.png', dpi=300)
print("Speedup график 'threads_speedup.png' нэрээр хадгалагдлаа.")
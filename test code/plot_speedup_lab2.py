import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('benchmark_results_lab2.csv')

avg_times = df.groupby(['impl', 'threads'])['elapsed_ms'].mean().reset_index()

serial_time = avg_times[avg_times['impl'] == 'serial']['elapsed_ms'].mean()

openmp_data = avg_times[avg_times['impl'] == 'openmp'].copy()
threads_data = avg_times[avg_times['impl'] == 'threads'].copy()

openmp_data['speedup'] = serial_time / openmp_data['elapsed_ms']
threads_data['speedup'] = serial_time / threads_data['elapsed_ms']

plt.figure(figsize=(10, 6))

plt.plot(openmp_data['threads'], openmp_data['speedup'], 
         marker='o', linestyle='-', linewidth=2, markersize=6, 
         label='OpenMP', color='green')
plt.plot(threads_data['threads'], threads_data['speedup'], 
         marker='s', linestyle='-', linewidth=2, markersize=6, 
         label='std::thread', color='blue')

plt.xlabel('Number of Threads', fontsize=12)
plt.ylabel('Speedup', fontsize=12)
plt.title('Хурдны өсөлтийн харуулсан график (sin compute)', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend(loc='lower right', fontsize=10)

max_threads = max(openmp_data['threads'].max(), threads_data['threads'].max())
plt.xlim(0, max_threads + 1)
plt.ylim(0, max(openmp_data['speedup'].max(), threads_data['speedup'].max()) + 1)

plt.tight_layout()
plt.savefig('speedup_graph_lab2.png', dpi=300, bbox_inches='tight')
print("График амжилттай үүсгэгдлээ: speedup_graph_lab2.png")

print("\nOpenMP Speedup:")
print(openmp_data[['threads', 'speedup']].to_string(index=False))
print("\nstd::thread Speedup:")
print(threads_data[['threads', 'speedup']].to_string(index=False))

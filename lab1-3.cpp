#include <iostream>
#include <fstream>
#include <vector>
#include <thread>
#include <chrono>
#include <cmath>
#include <omp.h>

using namespace std;
using namespace std::chrono;


void transpose(const double *b, double *b_t, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            b_t[j * n + i] = b[i * n + j];
}

void compute_sequential(const double *a, const double *b_t, double *c, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) sum += a[i * n + k] * b_t[j * n + k];
            c[i * n + j] = sum;
        }
}

void compute_openmp(const double *a, const double *b_t, double *c, int n, int num_threads) {
    #pragma omp parallel for num_threads(num_threads) schedule(static)
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) sum += a[i * n + k] * b_t[j * n + k];
            c[i * n + j] = sum;
        }
}

void compute_thread_rows(const double *a, const double *b_t, double *c, int n, int start_row, int end_row) {
    for (int i = start_row; i < end_row; i++)
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) sum += a[i * n + k] * b_t[j * n + k];
            c[i * n + j] = sum;
        }
}

void compute_threads(const double *a, const double *b_t, double *c, int n, int num_threads) {
    vector<thread> threads;
    int rows_per_thread = n / num_threads;
    for (int i = 0; i < num_threads; i++) {
        int start = i * rows_per_thread;
        int end = (i == num_threads - 1) ? n : (i + 1) * rows_per_thread;
        threads.emplace_back(compute_thread_rows, a, b_t, c, n, start, end);
    }
    for (auto &t : threads) t.join();
}

void benchmark_matrix(int runs, int max_threads, int n, const double *a, const double *b, double *c, const string &cpuMode) {
    double *b_t = new double[n * n];
    transpose(b, b_t, n);

    string folder = "./csv";
    string suffix = "_" + cpuMode + ".csv";

    
    ofstream seq_file(folder + "sequential" + suffix);
    seq_file << "workload,impl,threads,size,run,elapsed_ms,mode\n";
    for (int r = 1; r <= runs; r++) {
        auto t1 = steady_clock::now();
        compute_sequential(a, b_t, c, n);
        auto t2 = steady_clock::now();
        seq_file << "matrix,sequential,1," << n << "," << r << "," << duration_cast<milliseconds>(t2 - t1).count() << "," << cpuMode << "\n";
    }
    seq_file.close();

    
    ofstream omp_file(folder + "openmp" + suffix);
    omp_file << "workload,impl,threads,size,run,elapsed_ms,mode\n";
    for (int r = 1; r <= runs; r++)
        for (int t = 1; t <= max_threads; t += 2) {
            auto t1 = steady_clock::now();
            compute_openmp(a, b_t, c, n, t);
            auto t2 = steady_clock::now();
            omp_file << "matrix,openmp," << t << "," << n << "," << r << "," << duration_cast<milliseconds>(t2 - t1).count() << "," << cpuMode << "\n";
        }
    omp_file.close();

    
    ofstream th_file(folder + "threads" + suffix);
    th_file << "workload,impl,threads,size,run,elapsed_ms,mode\n";
    for (int r = 1; r <= runs; r++)
        for (int t = 1; t <= max_threads; t += 2) {
            auto t1 = steady_clock::now();
            compute_threads(a, b_t, c, n, t);
            auto t2 = steady_clock::now();
            th_file << "matrix,threads," << t << "," << n << "," << r << "," << duration_cast<milliseconds>(t2 - t1).count() << "," << cpuMode << "\n";
        }
    th_file.close();

    delete[] b_t;
    cout << "Файлууд " << folder << " хавтсанд " << cpuMode << " нэрээр хадгалагдлаа." << endl;
}

int main() {
    int n, max_threads;
    string cpuMode;
    cout << "Enter n: "; cin >> n;
    cout << "Max threads: "; cin >> max_threads;
    cout << "Enter CPU mode (e.g., balanced or performance): "; cin >> cpuMode;

    double *a = new double[n * n]; double *b = new double[n * n]; double *c = new double[n * n];
    fill(a, a + n * n, 1.0); fill(b, b + n * n, 1.0);

    benchmark_matrix(10, max_threads, n, a, b, c, cpuMode);

    delete[] a; delete[] b; delete[] c;
    return 0;
}
#include <iostream>
#include <fstream>
#include <vector>
#include <thread>
#include <chrono>
#include <algorithm>
#include <omp.h>

using namespace std;
using namespace std::chrono;

// Naive: Transpose хийгээгүй
void compute_naive(const double *a, const double *b, double *c, int n, int num_threads, bool use_omp) {
    if (use_omp) {
        #pragma omp parallel for num_threads(num_threads)
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                double sum = 0.0;
                for (int k = 0; k < n; k++) sum += a[i * n + k] * b[k * n + j];
                c[i * n + j] = sum;
            }
    } else {
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                double sum = 0.0;
                for (int k = 0; k < n; k++) sum += a[i * n + k] * b[k * n + j];
                c[i * n + j] = sum;
            }
    }
}

// Optimized: Transpose хийсэн
void compute_optimized(const double *a, const double *b_t, double *c, int n, int num_threads, bool use_omp) {
    if (use_omp) {
        #pragma omp parallel for num_threads(num_threads)
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                double sum = 0.0;
                for (int k = 0; k < n; k++) sum += a[i * n + k] * b_t[j * n + k];
                c[i * n + j] = sum;
            }
    } else {
        vector<thread> threads;
        int chunk = n / num_threads;
        for (int t = 0; t < num_threads; t++) {
            threads.emplace_back([&, t]() {
                int start = t * chunk;
                int end = (t == num_threads - 1) ? n : (t + 1) * chunk;
                for (int i = start; i < end; i++)
                    for (int j = 0; j < n; j++) {
                        double sum = 0.0;
                        for (int k = 0; k < n; k++) sum += a[i * n + k] * b_t[j * n + k];
                        c[i * n + j] = sum;
                    }
            });
        }
        for (auto &t : threads) t.join();
    }
}

int main() {
    int n, max_threads;
    cout << "Enter n and max_threads: "; cin >> n >> max_threads;
    
    double *a = new double[n * n]; double *b = new double[n * n]; double *c = new double[n * n];
    double *b_t = new double[n * n];
    fill(a, a + n * n, 1.0); fill(b, b + n * n, 1.0);
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) b_t[j * n + i] = b[i * n + j];

    ofstream file("./csv/final_results.csv");
    file << "impl,threads,is_transpose,ms\n";

    for (int t = 1; t <= max_threads; t++) {
        // Sequential (t=1 үед)
        if (t == 1) {
            auto t1 = steady_clock::now();
            compute_naive(a, b, c, n, 1, false);
            file << "sequential,1,0," << duration_cast<milliseconds>(steady_clock::now() - t1).count() << "\n";
            
            t1 = steady_clock::now();
            compute_optimized(a, b_t, c, n, 1, false);
            file << "sequential,1,1," << duration_cast<milliseconds>(steady_clock::now() - t1).count() << "\n";
        }
        // OpenMP
        auto t1 = steady_clock::now();
        compute_naive(a, b, c, n, t, true);
        file << "openmp," << t << ",0," << duration_cast<milliseconds>(steady_clock::now() - t1).count() << "\n";
        
        t1 = steady_clock::now();
        compute_optimized(a, b_t, c, n, t, true);
        file << "openmp," << t << ",1," << duration_cast<milliseconds>(steady_clock::now() - t1).count() << "\n";
        
        // Threads
        t1 = steady_clock::now();
        compute_optimized(a, b_t, c, n, t, false);
        file << "threads," << t << ",1," << duration_cast<milliseconds>(steady_clock::now() - t1).count() << "\n";
    }
    file.close();
    delete[] a; delete[] b; delete[] c; delete[] b_t;
    cout << "Үр дүн ./csv/final_results.csv файлд хадгалагдлаа." << endl;
    return 0;
}
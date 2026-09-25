#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <omp.h>

using namespace std;
using namespace std::chrono;

// ── Transpose хийх ──
void transpose(const double *b, double *b_t, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            b_t[j * n + i] = b[i * n + j];
}

// ── OpenMP + Transpose (cache-friendly) ──
void compute_openmp_transposed(const double *a, const double *b_t, double *c, int n, int num_threads) {
    #pragma omp parallel for num_threads(num_threads) schedule(static)
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) sum += a[i * n + k] * b_t[j * n + k];
            c[i * n + j] = sum;
        }
}

// ── OpenMP + Transpose хийлгүй (cache-unfriendly column access) ──
void compute_openmp_no_transpose(const double *a, const double *b, double *c, int n, int num_threads) {
    #pragma omp parallel for num_threads(num_threads) schedule(static)
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) sum += a[i * n + k] * b[k * n + j]; // column access!
            c[i * n + j] = sum;
        }
}

int main() {
    int n, max_threads, runs;
    cout << "Enter n (matrix size): ";       cin >> n;
    cout << "Max threads: ";                  cin >> max_threads;
    cout << "Runs per config: ";              cin >> runs;

    double *a   = new double[n * n];
    double *b   = new double[n * n];
    double *b_t = new double[n * n];
    double *c   = new double[n * n];

    fill(a, a + n * n, 1.0);
    fill(b, b + n * n, 1.0);

    // Transpose-г нэг удаа урьдчилан тооцоолно
    transpose(b, b_t, n);

    string folder = "./csv/";

    // ── Transpose ашигласан ──
    ofstream f_trans(folder + "csvtransposed_omp.csv");
    f_trans << "impl,threads,size,run,elapsed_ms\n";

    for (int r = 1; r <= runs; r++) {
        for (int t = 1; t <= max_threads; t += 2) {
            auto t1 = steady_clock::now();
            compute_openmp_transposed(a, b_t, c, n, t);
            auto t2 = steady_clock::now();
            f_trans << "transposed," << t << "," << n << "," << r << ","
                    << duration_cast<milliseconds>(t2 - t1).count() << "\n";
        }
    }
    f_trans.close();
    cout << "✅ csvtransposed_omp.csv хадгалагдлаа\n";

    // ── Transpose хийлгүй ──
    ofstream f_notrans(folder + "csvno_transpose_omp.csv");
    f_notrans << "impl,threads,size,run,elapsed_ms\n";

    for (int r = 1; r <= runs; r++) {
        for (int t = 1; t <= max_threads; t += 2) {
            auto t1 = steady_clock::now();
            compute_openmp_no_transpose(a, b, c, n, t);
            auto t2 = steady_clock::now();
            f_notrans << "no_transpose," << t << "," << n << "," << r << ","
                      << duration_cast<milliseconds>(t2 - t1).count() << "\n";
        }
    }
    f_notrans.close();
    cout << "✅ csvno_transpose_omp.csv хадгалагдлаа\n";

    delete[] a; delete[] b; delete[] b_t; delete[] c;
    return 0;
}
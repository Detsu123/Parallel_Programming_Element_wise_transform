#include <iostream>
#include <thread>
#include <vector>
#include <chrono>
using namespace std;
using namespace std::chrono;

// Нэг thread-д хуваарилагдсан хэсгийн нийлбэрийг тооцоолох
void compute_partial_sum(double *array, int start, int end, double *result) {
    double sum = 0.0;
    for (int i = start; i < end; i++) {
        sum += array[i];
    }
    *result = sum;
}

double compute_multithread(double *array, int array_size, int num_threads) {
    vector<thread> threads;
    vector<double> partial_sums(num_threads, 0.0);
    
    int chunk_size = array_size / num_threads;
    
    // Thread бүрийг үүсгэх
    for (int i = 0; i < num_threads; i++) {
        int start = i * chunk_size;
        int end = (i == num_threads - 1) ? array_size : (i + 1) * chunk_size;
        
        threads.push_back(thread(compute_partial_sum, array, start, end, &partial_sums[i]));
    }
    
    // Бүх thread дуусахыг хүлээх
    for (auto &t : threads) {
        t.join();
    }
    
    // Хэсэгчилсэн нийлбэрүүдийг нэгтгэх
    double total_sum = 0.0;
    for (double partial : partial_sums) {
        total_sum += partial;
    }
    
    return total_sum;
}

int main() {
    int array_size = 8000000;
    double *array = new double[array_size];
    
    // Массивыг эхлүүлэх
    auto start = high_resolution_clock::now();
    for (int i = 0; i < array_size; i++) {
        array[i] = 1.0;
    }
    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(stop - start);
    cout << "Time taken by sequential loop: " << duration.count() << " microseconds" << endl;
    
    // Hardware-ын цөмийн тоог олох
    int num_threads = thread::hardware_concurrency();
    cout << "Using " << num_threads << " threads" << endl;
    
    // Multithread тооцоолол
    auto t1 = high_resolution_clock::now();
    double sum_multithread = compute_multithread(array, array_size, num_threads);
    auto t2 = high_resolution_clock::now();
    auto d1 = duration_cast<microseconds>(t2 - t1);
    
    cout << "Time taken by multithread compute: " << d1.count() << " microseconds" << endl;
    cout << "Count by multithread: " << sum_multithread << endl;
    
    delete[] array;
    return 0;
}
#include<iostream>
#include<chrono>
#include<thread>
#include<vector>
#include<fstream>
using namespace std;
using namespace std::chrono;

double compute_sequential(double *array, int array_size){
    double sum = 0.0;
    for (int i=0; i< array_size; i++){
        sum +=array[i];
    }
    return sum;
}

double compute_openmp(double *array, int array_size, int num_thread){
    double sum = 0.0;
    #pragma omp parallel for reduction(+:sum) num_threads(num_thread)
    for (int i= 0; i<array_size; i++){
        sum +=array[i];
    }
    return sum;
}
void compute_thread(double *array, int start, int end, double *result){
    double sum = 0.0;
    for(int i = start; i<end; i++){
        sum += array[i];
    }
    *result = sum;
}

double compute_threads(double *array, int array_size, int num_threads){
    vector<thread> threads;
    vector<double> treads_sum(num_threads, 0.0);
    int chunk_size = array_size / num_threads;
    for (int i=0; i< num_threads; i++){
        int start = i * chunk_size;
        int end = (i==num_threads-1)? array_size : (i+1)*chunk_size;
        threads.push_back(thread(compute_thread, array, start, end, &treads_sum[i]));
    }
    for (auto &t : threads){
        t.join();
    }
    double sum = 0.0;
    for(double st : treads_sum ){
        sum += st;
    }
    return sum;
}
// workload - impl - threads - size - run_i - elapsed_ms - notes
void compute_sequential_function(int sum_run, int max_threads, int array_size, double *array){
    string file_path = "./csv/result_sequential.csv";
    ofstream file(file_path);

    for(int run_i=1; run_i <= sum_run; run_i++){
        auto t1 = steady_clock::now();
        double sum_thread = compute_sequential(array, array_size);
        auto t2 = steady_clock::now();
        auto duration = duration_cast<milliseconds>(t2-t1);
        file << "sum" << "," << "sequential" << "," << 1 << "," << array_size << "," << run_i << "," << duration.count() << "," << sum_thread << endl;
    }
    file.close();
}

void compute_openmp_function(int sum_run, int max_threads, int array_size, double *array){
    string file_path = "./csv/result_openmp.csv";
    ofstream file(file_path);

    for(int run_i=1; run_i <= sum_run; run_i++){
        auto t1 = steady_clock::now();
        double sum_thread = compute_openmp(array, array_size, 1);
        auto t2 = steady_clock::now();
        auto duration = duration_cast<milliseconds>(t2-t1);
        file << "sum" << "," << "openmp" << "," << 1 << "," << array_size << "," << run_i << "," << duration.count() << "," << sum_thread << endl;

        for (int thread = 2; thread <= max_threads; thread += 2){
            auto t3 = steady_clock::now();
            double sum_parallel = compute_openmp(array, array_size, thread);
            auto t4 = steady_clock::now();
            auto duration_parallel = duration_cast<milliseconds>(t4-t3);
            file << "sum" << "," << "openmp" << "," << thread << "," << array_size << "," << run_i << "," << duration_parallel.count() << "," << sum_parallel << endl;
        }
    }
    file.close();
}
void compute_threads_function(int sum_run, int max_threads, int array_size, double *array){
    string file_path = "./csv/result_threads.csv";
    ofstream file(file_path);

    for(int run_i=1; run_i <= sum_run; run_i++){
        auto t1 = steady_clock::now();
        double sum_thread = compute_threads(array, array_size, 1);
        auto t2 = steady_clock::now();
        auto duration = duration_cast<milliseconds>(t2-t1);
        file << "sum" << "," << "threads" << "," << 1 << "," << array_size << "," << run_i << "," << duration.count() << "," << sum_thread << endl;

        for (int thread = 2; thread <= max_threads; thread += 2){
            auto t3 = steady_clock::now();
            double sum_parallel = compute_threads(array, array_size, thread);
            auto t4 = steady_clock::now();
            auto duration_parallel = duration_cast<milliseconds>(t4-t3);
            file << "sum" << "," << "threads" << "," << thread << "," << array_size << "," << run_i << "," << duration_parallel.count() << "," << sum_parallel << endl;
        }
    }
    file.close();
}

int main(){
    int array_size=80000000;
    double *array = new double[array_size];
    int num_thread;
    cout << "Write num thread: ";
    cin >> num_thread;
    cout << "Num thread: " << num_thread << endl;
    for (int i=0;i<array_size;i++){
        array[i]=1.0;
    };
    int choise_method;
    cout << "Choise method" << endl << "1. Sequantial" << endl << "2. OpenMP" << endl << "3. std::threads" << endl;
    cin >> choise_method;
    if( choise_method == 1){
        compute_sequential_function( 10,num_thread,array_size, array);
        cout << "Sequential compute complete. Haved csv/result_sequential.csv"<< endl;
    } else if( choise_method == 2){
        compute_openmp_function( 10,num_thread,array_size, array);
        cout << "OpenMP compute complete. Haved csv/result_openmp.csv"<< endl;
    } else if(choise_method == 3){
        compute_threads_function( 10,num_thread,array_size, array);
        cout << "std:threads compute complete. Haved csv/result_threads.csv"<< endl;
    }
    delete[] array;
    return 0;
}












    // int array_size=80000000;
    // double *array = new double[array_size];
    // int num_thread;
    // cout << "Write num thread: ";
    // cin >> num_thread;
    // cout << "Num thread: " << num_thread << endl;
    // for (int i=0;i<array_size;i++){
    //     array[i]=1.0;
    // }
    // // //-------------------sequentail-------------------
    // // auto t5 = steady_clock::now();
    // // double sum_sequantial = compute_sequential(array, array_size);
    // // auto t6 = steady_clock::now();
    // // auto d3 = duration_cast<milliseconds>(t6-t5);
    // // std::cout.imbue(std::locale(""));
    // // cout << "Time taken by sequential compute " <<  d3.count() << " milliseconds " << endl;
    // // cout << "Count by sequential: " << sum_sequantial << endl;      
    // // //--------------------OpenMP----------------------
    // // auto t1 = steady_clock::now();
    // // double sum_openmp = compute_openmp(array, array_size, num_thread);
    // // auto t2 = steady_clock::now();
    // // auto d1 = duration_cast<milliseconds>(t2-t1);
    // // std::cout.imbue(std::locale(""));
    // // cout << "Time taken by OpenMP compute " <<  d1.count() << " milliseconds " << endl;
    // // cout << "Count by OpenMP: " << sum_openmp << endl;
    // //--------------------thread------------------------
    // // auto t3 = steady_clock::now();
    // // double sum_thread = compute_threads(array, array_size, num_thread);
    // // auto t4 = steady_clock::now();
    // // auto d2 = duration_cast<milliseconds>(t4-t3);
    // // std::cout.imbue(std::locale(""));
    // // cout << "Time taken by thread compute " <<  d2.count() << " milliseconds " << endl;
    // // cout << "Count by thread: " << sum_thread << endl;
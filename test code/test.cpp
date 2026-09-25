// #include <omp.h>
// #include <iostream>

// int main() {
//     // Энгийн параллель хэсэг
//     #pragma omp parallel
//     {
//         int thread_id = omp_get_thread_num();
//         #pragma omp critical
//         std::cout << "Сайн уу thread " << thread_id << "-с" << std::endl;
//     }
    
//     // Параллель давталт
//     #pragma omp parallel for
//     for(int i = 0; i < 10; i++) {
//         #pragma omp critical
//         std::cout << "Итерация " << i << std::endl;
//     }
    
//     return 0;
// }#include <omp.h>
// #include <iostream>

// int main() {
//     // Энгийн параллель хэсэг
//     #pragma omp parallel
//     {
//         int thread_id = omp_get_thread_num();
//         #pragma omp critical
//         std::cout << "Сайн уу thread " << thread_id << "-с" << std::endl;
//     }
    
//     // Параллель давталт
//     #pragma omp parallel for
//     for(int i = 0; i < 10; i++) {
//         #pragma omp critical
//         std::cout << "Итерация " << i << std::endl;
//     }
    
//     return 0;
// }
#include <iostream>

int main() {
    int arr[] = {10, 20, 30, 40, 50, 60};
    // Calculate the number of elements
    int arrSize = sizeof(arr[0]); 

    std::cout << "The size of the array is: " << arrSize << std::endl;

    return 0;
}

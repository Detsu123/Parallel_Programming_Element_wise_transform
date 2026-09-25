#include <iostream>
#include <thread>
#include <vector>

// Thread дээр ажиллах функц
void print_message(int id) {
    std::cout << "Thread " << id << " ажиллаж байна" << std::endl;
}

void calculate(int start, int end, int* result) {
    int sum = 0;
    for(int i = start; i < end; i++) {
        sum += i;
    }
    *result = sum;
}

int main() {
    // Энгийн жишээ
    std::thread t1(print_message, 1);
    std::thread t2(print_message, 2);
    
    // Thread-үүд дуусахыг хүлээх
    t1.join();
    t2.join();
    
    // Олон thread-үүдтэй ажиллах
    std::vector<std::thread> threads;
    std::vector<int> results(4);
    
    for(int i = 0; i < 4; i++) {
        threads.push_back(std::thread(calculate, i*25, (i+1)*25, &results[i]));
    }
    
    // Бүх thread дуусахыг хүлээх
    for(auto& t : threads) {
        t.join();
    }
    
    // Үр дүнг нэгтгэх
    int total = 0;
    for(int r : results) {
        total += r;
    }
    std::cout << "Нийт дүн: " << total << std::endl;
    
    return 0;
}
#pragma once

#include <chrono>

class Stopwatch {
 public:
  Stopwatch() : start_(std::chrono::steady_clock::now()) {}

  void restart() { start_ = std::chrono::steady_clock::now(); }

  double elapsedMilliseconds() const {
    const std::chrono::duration<double, std::milli> elapsed =
        std::chrono::steady_clock::now() - start_;
    return elapsed.count();
  }

 private:
  std::chrono::steady_clock::time_point start_;
};

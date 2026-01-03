#pragma once

#include <string>

namespace appwindows::core {

class Point {
 public:
  Point(int x, int y);
  Point operator+(const Point& other) const;
  Point operator-(const Point& other) const;
  Point operator*(const Point& other) const;
  Point operator/(const Point& other) const;
  bool operator==(const Point& other) const;
  bool operator!=(const Point& other) const;
  [[nodiscard]] int get_x() const;
  [[nodiscard]] int get_y() const;
  [[nodiscard]] std::string to_string() const noexcept {
    return "Point(x = " + std::to_string(x_) + ", y = " + std::to_string(y_) +
           ")";
  };

 private:
  int x_;
  int y_;
};

}  // namespace appwindows::core
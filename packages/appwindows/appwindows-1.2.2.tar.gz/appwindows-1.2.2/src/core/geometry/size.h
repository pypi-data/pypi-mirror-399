#pragma once

#include <string>

namespace appwindows::core {

class Size {
 public:
  Size(int width, int height);

  bool operator==(const Size& other) const;
  bool operator!=(const Size& other) const;

  [[nodiscard]] int get_width() const noexcept { return width_; };
  [[nodiscard]] int get_height() const noexcept { return height_; };
  [[nodiscard]] std::string to_string() const noexcept {
    return "Size(width = " + std::to_string(width_) +
           ", height = " + std::to_string(height_) + ")";
  };

 private:
  int width_;
  int height_;
};

}  // namespace appwindows::core
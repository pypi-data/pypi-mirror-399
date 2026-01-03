#include "size.h"

#include "../exceptions/invalid_size.h"

namespace appwindows::core {

Size::Size(const int width, const int height) : width_(width), height_(height) {
  if (width <= 0) throw exceptions::InvalidSizeException(width, height);
  if (height <= 0) throw exceptions::InvalidSizeException(width, height);
}

bool Size::operator==(const Size& other) const {
  return width_ == other.get_width() && height_ == other.get_height();
}

bool Size::operator!=(const Size& other) const {
  return width_ != other.get_width() || height_ != other.get_height();
}


}  // namespace appwindows::core
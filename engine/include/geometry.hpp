#pragma once

#include <cmath>

struct Vec2 {
  double x = 0.0;
  double y = 0.0;

  Vec2 operator+(const Vec2& other) const { return {x + other.x, y + other.y}; }
  Vec2 operator-(const Vec2& other) const { return {x - other.x, y - other.y}; }
  Vec2 operator*(double factor) const { return {x * factor, y * factor}; }
  Vec2& operator+=(const Vec2& other) {
    x += other.x;
    y += other.y;
    return *this;
  }
  Vec2& operator-=(const Vec2& other) {
    x -= other.x;
    y -= other.y;
    return *this;
  }
};

inline double dot(const Vec2& a, const Vec2& b) { return a.x * b.x + a.y * b.y; }
inline double squaredNorm(const Vec2& a) { return dot(a, a); }
inline double norm(const Vec2& a) { return std::sqrt(squaredNorm(a)); }

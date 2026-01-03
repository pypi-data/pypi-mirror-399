#include "gtest/gtest.h"
#include "3dmath/Vector.h"
#include "3dmath/SupportingTypes.h"
#include <vector>
using namespace std;
using namespace math3d;

TEST(Extent, ConstructionAndGetters) {
    Extent<float> extent{10, 10};
    ASSERT_FLOAT_EQ(extent.min, 10);
    ASSERT_FLOAT_EQ(extent.max, 10);
    ASSERT_FLOAT_EQ(extent.length(), 0);
    ASSERT_FLOAT_EQ(extent.center(), 10);
}

TEST(Bounds3D, UninitializedBounds) {
    Bounds3D<float> bounds;
    ASSERT_FLOAT_EQ(bounds.x.min, numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.y.min, numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.y.min, numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.x.max, -numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.y.max, -numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.y.max, -numeric_limits<float>::max());
}

TEST(Bounds3D, InitializedBounds) {
    Bounds3D<float> bounds1{{-1,-1,-1},{+1,+1,+1}};
    ASSERT_FLOAT_EQ(bounds1.x.length(), 2);
    ASSERT_FLOAT_EQ(bounds1.y.length(), 2);
    ASSERT_FLOAT_EQ(bounds1.z.length(), 2);


    Bounds3D<float> bounds2d{{-1,-1},{+1,+1}};
    ASSERT_FLOAT_EQ(bounds2d.x.length(), 2);
    ASSERT_FLOAT_EQ(bounds2d.y.length(), 2);
}

TEST(Bounds3D, Getters) {
    Bounds3D<float> bounds{{-1,-1,-1},{+1,+1,+1}};
    ASSERT_FLOAT_EQ(bounds.center().x, 0.f);
    ASSERT_FLOAT_EQ(bounds.center().y, 0.f);
    ASSERT_FLOAT_EQ(bounds.center().z, 0.f);
    ASSERT_FLOAT_EQ(bounds.length(), 2*sqrt(3));
}

TEST(Bounds3D, SymmetricBounds) {
    Bounds3D<float> bounds(1.f);
    ASSERT_FLOAT_EQ(bounds.center().x, 0.f);
    ASSERT_FLOAT_EQ(bounds.center().y, 0.f);
    ASSERT_FLOAT_EQ(bounds.center().z, 0.f);
    ASSERT_FLOAT_EQ(bounds.x.length(), 1);
    ASSERT_FLOAT_EQ(bounds.y.length(), 1);
    ASSERT_FLOAT_EQ(bounds.z.length(), 1);
    ASSERT_FLOAT_EQ(bounds.x.min, -0.5);
    ASSERT_FLOAT_EQ(bounds.x.max, +0.5);
    ASSERT_FLOAT_EQ(bounds.y.min, -0.5);
    ASSERT_FLOAT_EQ(bounds.y.max, +0.5);
    ASSERT_FLOAT_EQ(bounds.z.min, -0.5);
    ASSERT_FLOAT_EQ(bounds.z.max, +0.5);
}

TEST(Bounds3D, Reset) {
    Bounds3D<float> bounds{{-1,-1,-1},{+1,+1,+1}};
    bounds.reset();
    ASSERT_FLOAT_EQ(bounds.x.min, +std::numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.x.max, -std::numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.y.min, +std::numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.y.max, -std::numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.z.min, +std::numeric_limits<float>::max());
    ASSERT_FLOAT_EQ(bounds.z.max, -std::numeric_limits<float>::max());
}


TEST(Bounds3D, Contains) {
    Bounds3D<float> bounds{{-1,-1,-1},{+1,+1,+1}};
    ASSERT_TRUE(bounds.contains({-1,-1,-1}));
    ASSERT_TRUE(bounds.contains({+1,+1,+1}));
    ASSERT_TRUE(bounds.contains({0,0,0}));
    ASSERT_FALSE(bounds.contains({-5, 0, 0}));
    ASSERT_FALSE(bounds.contains({0, -5, 0}));
    ASSERT_FALSE(bounds.contains({0, 0, -5}));
}

TEST(Bounds3D, ConstructFrom2DBounds) {
    Bounds3D<float> bounds{{-1,-1},{+1,+1}};
    ASSERT_FLOAT_EQ(bounds.z.length(), 0.f);
    ASSERT_FLOAT_EQ(bounds.x.length(), 2.f);
    ASSERT_FLOAT_EQ(bounds.y.length(), 2.f);
}

TEST(Bounds3D, UniformScaling) {
    Bounds3D<float> bounds{{-1, -1, -1},
                           {+1, +1, +1}};
    auto oldLength = bounds.length();
    bounds.scale(1.5f);
    ASSERT_FLOAT_EQ(bounds.length(), oldLength * 1.5f);
}

TEST(Bounds3D, NonUniformScaling) {
    Bounds3D<float> bounds{{-1, -1, -1},
                           {+1, +1, +1}};
    auto xLen = bounds.x.length();
    auto yLen = bounds.y.length();
    auto zLen = bounds.z.length();
    bounds.scale(1.5f, Bounds3D<float>::Direction::y);
    ASSERT_FLOAT_EQ(bounds.x.length(), xLen);
    ASSERT_FLOAT_EQ(bounds.y.length(), yLen*1.5f);
    ASSERT_FLOAT_EQ(bounds.z.length(), zLen);
    bounds.scale(1.5f, Bounds3D<float>::Direction::x);
    ASSERT_FLOAT_EQ(bounds.x.length(), xLen*1.5f);
    ASSERT_FLOAT_EQ(bounds.y.length(), yLen*1.5f);
    ASSERT_FLOAT_EQ(bounds.z.length(), zLen);
    bounds.scale(1.5f, Bounds3D<float>::Direction::z);
    ASSERT_FLOAT_EQ(bounds.x.length(), xLen*1.5f);
    ASSERT_FLOAT_EQ(bounds.y.length(), yLen*1.5f);
    ASSERT_FLOAT_EQ(bounds.z.length(), zLen*1.5f);
}

TEST(Bounds3D, Validity) {
    ASSERT_FALSE(Bounds3D<float>{}.isValid()) << "Uninitialized bounds should have been classified as invalid";
    Bounds3D<float> bounds{{-0.5, -0.5, -0.5},
                           {+0.5, +0.5, +0.5}};
    ASSERT_TRUE(bounds.isValid()) << "Bounds initialized with a unit cube must have been classified as valid";
}

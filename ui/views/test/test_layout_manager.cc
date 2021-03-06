// Copyright 2016 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "ui/views/test/test_layout_manager.h"

namespace views {
namespace test {

TestLayoutManager::TestLayoutManager() {}

TestLayoutManager::~TestLayoutManager() {}

void TestLayoutManager::Layout(View* host) {}

gfx::Size TestLayoutManager::GetPreferredSize(const View* host) const {
  return preferred_size_;
}

int TestLayoutManager::GetPreferredHeightForWidth(const View* host,
                                                  int width) const {
  return preferred_height_for_width_;
}

}  // namespace test
}  // namespace views

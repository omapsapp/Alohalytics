/*******************************************************************************
 The MIT License (MIT)

 Copyright (c) 2015 Alexander Zolotarev <me@alex.bio> from Minsk, Belarus

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
 *******************************************************************************/

// Calculates GPU statistics.

#include "../include/processor.h"

#include <algorithm>
#include <map>
#include <string>
#include <vector>

using namespace alohalytics;
using namespace std;

int main(int, char **) {
  map<string, size_t> gpu;
  size_t counter = 0;
  Processor([&](const AlohalyticsIdServerEvent *, const AlohalyticsKeyEvent * e) {
    const AlohalyticsKeyValueEvent * kve = dynamic_cast<const AlohalyticsKeyValueEvent *>(e);
    if (kve && kve->key == "GPU") {
      ++gpu[kve->value];
      ++counter;
    }
  });
  
  vector<pair<size_t, string>> v;
  v.reserve(gpu.size());
  for (pair<string, size_t> p : gpu) {
    v.push_back(make_pair(p.second, p.first));
  }
  sort(v.begin(), v.end(), [](const pair<size_t, string> & p1, const pair<size_t, string> & p2) {
    return p1.first > p2.first;
  });

  cerr << "GPU statistics (GPU: app launch count, percentage):" << endl;
  int i = 1;
  for (const auto & gpu : v) {
    const float percent = 100.0f * gpu.first / static_cast<float>(counter);
    cerr << i << ". " << gpu.second << ": " << gpu.first << " (" << setprecision(4) << percent << "%)" << endl;
    ++i;
  }
  return 0;
}

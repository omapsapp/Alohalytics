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

// Calculates statistics for connection state (roaming, wifi, offline).

#include "../Alohalytics/src/processor.h"

#include <set>
#include <string>

using namespace alohalytics;
using namespace std;

int main(int, char **) {
  map<string, set<string>> users;
  Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    if (se->id[0] != 'A') {
      return;  // ignore iOS events.
    }
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && kpe->key == "$launch") {
      auto & u = users[se->id];
      for (auto const & kv : kpe->pairs) {
        u.insert(kv.first + "=" + kv.second);
      }
    }
  }).PrintStatistics();

  map<string, size_t> counters;
  for (auto const & user : users) {
    for (auto const & e : user.second) {
      ++counters[e];
    }
  }
  size_t const total = users.size();
  cout << "Total users analyzed: " << total << endl;
  for (auto const & u : counters) {
    cout << u.first << " " << 100. * u.second / total << "%" << endl;
  }
  return 0;
}

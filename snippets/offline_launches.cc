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

// Calculates how many sessions were launched while in offline.

#include "../Alohalytics/src/processor.h"

#include <set>
#include <string>

using namespace alohalytics;
using namespace std;

int main(int, char **) {
  uint64_t launches_count = 0, connected = 0, not_connected = 0, nulls = 0;
  Processor([&](const AlohalyticsIdServerEvent *, const AlohalyticsKeyEvent * e) {
    // At the moment of writing (13 Oct 2015) only android $launch events had connected=yes/no support.
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && kpe->key == "$launch") {
      for (auto const & kv : kpe->pairs) {
        if (kv.first == "connected") {
          if (kv.second == "yes") {
            ++connected;
          } else {
            ++not_connected;
          }
          ++launches_count;
        } else if (kv.first == "null") {
          // On Android, when there is no any network info, we have null=activeNetwork.
          ++nulls;
          ++launches_count;
        }
      }
    }
  }).PrintStatistics();

  // Display statistics.
  cout << "Total launches: " << launches_count << endl;
  cout << "Online launches: " << connected << " (" << connected * 100. / launches_count << "%)" << endl;
  cout << "Not connected: " << not_connected << " (" << not_connected * 100. / launches_count << "%)" << endl;
  cout << "Nulls: " << nulls << " (" << nulls * 100. / launches_count << "%)" << endl;
  return 0;
}

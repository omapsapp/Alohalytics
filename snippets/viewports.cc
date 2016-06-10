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

// Calculates map viewport statistics, for Framework::EnterBackground event.
// Dumps zoom,sessionSeconds,lat,lon in CSV format to stdout.

#include "../Alohalytics/src/processor.h"

#include <set>
#include <string>

using namespace alohalytics;
using namespace std;

int main(int, char **) {
  map<int, size_t> zooms, sessions;
  Processor([&](const AlohalyticsIdServerEvent *, const AlohalyticsKeyEvent * e) {
    const AlohalyticsKeyPairsLocationEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsLocationEvent *>(e);
    if (kpe && kpe->key == "Framework::EnterBackground") {
      int zoom = -1, seconds = -1;
      for (auto const & kv : kpe->pairs) {
        if (kv.first == "zoom") {
          zoom = stoi(kv.second);
        } else if (kv.first == "foregroundSeconds") {
          seconds = stoi(kv.second);
        }
      }
      ++zooms[zoom];
      ++sessions[seconds];
      cout << zoom << ',' << seconds << ',' << kpe->location.latitude_deg_ << ',' << kpe->location.longitude_deg_
           << endl;
    }
  }).PrintStatistics();

  cerr << "Zoom levels statistics (zoom, count):" << endl;
  for (auto const & zoom : zooms) {
    cerr << zoom.first << " " << zoom.second << endl;
  }
  cerr << "Session lengths statistics (seconds, count):" << endl;
  for (auto const & session : sessions) {
    cerr << session.first << " " << session.second << endl;
  }
  return 0;
}

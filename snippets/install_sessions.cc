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

// Calculates statistics for very first sessions (immediately after app install).
// Session is a continuous events flow with no more than <X> seconds interval between events,
// specified from command line.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include <algorithm>
#include <unordered_map>
#include <vector>

using namespace alohalytics;
using namespace std;

struct Stats {
  string version;
  uint64_t install_ms;
  uint64_t last_event_ms;
  uint32_t Seconds() const { return static_cast<uint32_t>((last_event_ms - install_ms) / 1000); }
};

uint32_t Average(const vector<uint32_t> & v) {
  if (v.size() == 0) {
    return 0;
  }
  uint64_t average = 0;
  for (auto s : v) {
    average += s;
  }
  return average / v.size();
}

int main(int argc, char ** argv) {
  if (argc < 2) {
    cout << "Usage: " << argv[0] << " <seconds interval between events in the flow>" << endl;
    return -1;
  }
  const uint64_t milliseconds = stoull(argv[1]) * 1000;
  unordered_map<string, Stats> users;

  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr, server_id;
  while (true) {
    try {
      ar(ptr);
    } catch (const cereal::Exception & ex) {
      if (string("Failed to read 4 bytes from input stream! Read 0") != ex.what()) {
        // The exception above is a normal one, Cereal lacks to detect the end of the stream.
        cerr << ex.what() << endl;
      }
      break;
    }

    const AlohalyticsKeyEvent * e = dynamic_cast<const AlohalyticsKeyEvent *>(ptr.get());
    if (!e) {
      const AlohalyticsIdServerEvent * se = dynamic_cast<const AlohalyticsIdServerEvent *>(ptr.get());
      if (se) {
        server_id = move(ptr);
        continue;
      }
      cerr << "Critical Error: not a key event in the stream!" << endl;
      continue;
    }
    // Processing code.
    if (e->key == "$install") {
      Stats & s = users[static_cast<const AlohalyticsIdServerEvent *>(server_id.get())->id];
      s.install_ms = s.last_event_ms = e->timestamp;
      s.version = static_cast<const AlohalyticsIdServerEvent *>(server_id.get())->uri;
      continue;
    }
    auto found = users.find(static_cast<const AlohalyticsIdServerEvent *>(server_id.get())->id);
    if (found == users.end()) {
      continue;
    }
    if ((e->timestamp - found->second.last_event_ms) < milliseconds) {
      found->second.last_event_ms = e->timestamp;
      continue;
    }
  }

  cout << "Found " << users.size() << " users with install sessions." << endl;

  unordered_map<string, vector<uint32_t>> versions;
  for (const auto & user : users) {
    versions[user.second.version].emplace_back(user.second.Seconds());
  }

  cout << "Version,Users,Avg,Median,Avg(no 0),Median(no 0)" << endl;
  for (auto & v : versions) {
    cout << v.first << ',';
    cout << v.second.size() << ',';
    // Need to sort vectors for medians.
    sort(v.second.begin(), v.second.end());
    cout << Average(v.second) << ',';
    cout << v.second[v.second.size()/2] << ',';
    // There are a lot of zero session lengths, filter them out.
    v.second.erase(remove(v.second.begin(), v.second.end(), 0), v.second.end());
    cout << Average(v.second) << ',';
    cout << v.second[v.second.size()/2];
    cout << endl;
  }
  return 0;
}

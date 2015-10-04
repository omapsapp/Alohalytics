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

#include"../include/processor.h"

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

  Processor([&](const AlohalyticsIdServerEvent * ie, const AlohalyticsKeyEvent * e){
    if (e->key[0] != '$') {
      return;
    }
    if (e->key == "$install") {
      Stats & s = users[ie->id];
      s.install_ms = s.last_event_ms = e->timestamp;
      s.version = ie->uri;
      return;
    }
    auto found = users.find(ie->id);
    if (found == users.end()) {
      return;
    }
    if ((e->timestamp - found->second.last_event_ms) < milliseconds) {
      found->second.last_event_ms = e->timestamp;
      return;
    }
  }).PrintStatistics();

  cout << "Found " << users.size() << " users with install sessions." << endl;

  unordered_map<string, vector<uint32_t>> versions;
  for (const auto & user : users) {
    versions[user.second.version].emplace_back(user.second.Seconds());
  }

  for (auto & v : versions) {
    cout << "Version: " << v.first << endl;
    cout << "Users with install events: " << v.second.size() << endl;
    // Need to sort vectors for medians.
    sort(v.second.begin(), v.second.end());
    cout << "Average install session length: " << Average(v.second) << " seconds."<< endl;
    cout << "Median session length: " << v.second[v.second.size()/2] << " seconds." << endl;
    // There are a lot of zero session lenghts, filter them out.
    v.second.erase(remove(v.second.begin(), v.second.end(), 0), v.second.end());
    cout << "Average install session length (no zero sessions): " << Average(v.second) << " seconds."<< endl;
    cout << "Median session length (no zero sessions): " << v.second[v.second.size()/2] << " seconds." << endl;
    cout << endl;
  }
  return 0;
}

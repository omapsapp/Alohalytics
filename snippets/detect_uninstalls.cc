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

// Prints <installation date>,<user ID>,<number of downloaded maps>,<number of failed maps>,<seconds between install and latest app usage>
// Lines are sorted ascending by seconds, so it would be easy to cut off all
// users who probably uninstalled the app after using it no more than X seconds.

#include "../include/processor_light.h"

#include <algorithm>
#include <ctime>
#include <iostream>
#include <unordered_map>
#include <vector>

using namespace std;

struct Counters {
  uint64_t install_time = 0;
  uint64_t last_usage_time = 0;
  uint64_t downloaded_maps = 0;
  uint64_t failed_maps = 0;
  string InstallDate() const {
    char buff[20] = {0};
    const time_t timet = install_time / 1000;
    strftime(buff, 20, "%Y-%m-%d", gmtime(&timet));
    return buff;
  }
  uint64_t UsageSeconds() const { return (last_usage_time - install_time) / 1000; }
};

int main(int, char **) {
  unordered_map<string, Counters> users;
  // TODO(AlexZ): Faster impl if parse raw stream and seek only new server events in a map.
  alohalytics::ProcessorLight([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    if (e->key == "$install") {
      users[se->id].install_time = e->timestamp;
    } else {
      const auto found = users.find(se->id);
      if (found != users.end()) {
        auto & lut = found->second.last_usage_time;
        if (lut < e->timestamp) {
          lut = e->timestamp;
        }
        // Also calculate downloaded countries.
        if (e->key == "$OnMapDownloadFinished") {
          const auto kpe = static_cast<const AlohalyticsKeyPairsEvent *>(e);
          const auto status = kpe->pairs.find("status");
          if (status != kpe->pairs.end()) {
            if (status->second == "ok") {
              ++found->second.downloaded_maps;
            } else {
              ++found->second.failed_maps;
            }
          }
        }
      }
    }
  });

  // Sort results.
  typedef vector<pair<string, Counters>> TContainer;
  TContainer sorted;
  for (const auto & user : users) {
    sorted.emplace_back(user.first, user.second);
  }
  sort(sorted.begin(), sorted.end(), [](TContainer::value_type const & e1, TContainer::value_type const & e2){
    return e1.second.UsageSeconds() < e2.second.UsageSeconds();
  });

  // Print results to stdout.
  for (const auto & user : sorted) {
    cout << user.second.InstallDate() << ',' << user.first << ','
         << user.second.downloaded_maps << ',' << user.second.failed_maps << ','
         << user.second.UsageSeconds() << endl;
  }
  return 0;
}

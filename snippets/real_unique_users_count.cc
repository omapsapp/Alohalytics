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

// If user reinstalls the app, unique user ids in the statistics are generated again.
// So we count the same user as a new one. This script tells how many users actually are the same
// who used app previously but reinstalled it.
// It is done by comparing android_id, google_play_id, UDID and VID - they should not change after reinstall.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"
#include "../include/processor.h"

#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>

using namespace std;

int main(int, char **) {
  // <"identifierForVendor", <"it's value", set<"alohalytics unique id">>>
  map<string, map<string, set<string>>> containers;
  alohalytics::Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (!kpe) {
      return;
    }
    if (kpe->key == "$iosDeviceIds" || kpe->key == "$androidIds") {
      for (const auto & pair : kpe->pairs) {
        if (pair.first == "isAdvertisingTrackingEnabled") {
          continue; // Skip this value for iOS.
        }
        containers[pair.first][pair.second].insert(se->id);
      }
    }
  }).PrintStatistics();
  for (const auto & counter : containers) {
    cout << counter.first << " has " << counter.second.size() << " real unique users out of ";
    size_t sum = 0;
    typedef vector<pair<string, set<string>>> TVector;
    TVector sorted_by_reinstalls;
    for (const auto & user : counter.second) {
      sum += user.second.size();
      sorted_by_reinstalls.push_back(user);
    }
    cout << sum << " (" << 100. - counter.second.size() / static_cast<double>(sum) * 100. << "% of users has reinstalled the app)" << endl;
    sort(sorted_by_reinstalls.begin(), sorted_by_reinstalls.end(), [](const TVector::value_type & v1, const TVector::value_type & v2){
      return v1.second.size() > v2.second.size();
    });
    const size_t kTopReinstallsToPrint = 10;
    cout << "Top " << kTopReinstallsToPrint << " reinstalls:" << endl;
    for (size_t i = 0; i < kTopReinstallsToPrint; ++i) {
      cout << sorted_by_reinstalls[i].first << " has reinstalled " << sorted_by_reinstalls[i].second.size() << " times." << endl;
    }
  }
  return 0;
}

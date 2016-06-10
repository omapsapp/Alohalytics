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

// Calculates total sum of all sessions in the events flow.

#include "../Alohalytics/src/processor.h"

#include <algorithm>
#include <iostream>
#include <utility>
#include <vector>

using namespace std;

struct Counters {
  uint64_t total_seconds = 0;
  uint64_t number_of_sessions = 0;
};

uint64_t invalid_seconds_count = 0;

int ToSeconds(const string & str) {
  const int seconds = stoi(str);
  if (seconds > 86400) {
    ++invalid_seconds_count;
    return 1;
  }
  return seconds;
}

int main(int, char **) {
  Counters framework, ios, android;
  vector<int> median_framework, median_ios, median_android;
  alohalytics::Processor([&](const AlohalyticsIdServerEvent *, const AlohalyticsKeyEvent * ke) {
    if (ke->key == "Framework::EnterBackground") {
      const AlohalyticsKeyPairsEvent * kpe = static_cast<const AlohalyticsKeyPairsEvent *>(ke);
      auto found = kpe->pairs.find("foregroundSeconds");
      if (found != kpe->pairs.end()) {
        const int seconds = ToSeconds(found->second);
        framework.total_seconds += seconds;
        ++framework.number_of_sessions;
        median_framework.push_back(seconds);
      }
    } else if (ke->key == "$applicationWillResignActive") {
      const AlohalyticsKeyValueEvent * kve = dynamic_cast<const AlohalyticsKeyValueEvent *>(ke);
      if (kve) {
        const int seconds = ToSeconds(kve->value);
        ios.total_seconds += seconds;
        ++ios.number_of_sessions;
        median_ios.push_back(seconds);
      }
    } else if (ke->key == "$endSession") {
      const AlohalyticsKeyValueEvent * kve = dynamic_cast<const AlohalyticsKeyValueEvent *>(ke);
      if (kve) {
        const int seconds = ToSeconds(kve->value);
        android.total_seconds += seconds;
        ++android.number_of_sessions;
        median_android.push_back(seconds);
      }
    }
  }).PrintStatistics();

  // Calculate & print results.
  cout << "Invalid seconds count: " << invalid_seconds_count << endl;
  sort(median_android.begin(), median_android.end());
  sort(median_ios.begin(), median_ios.end());
  sort(median_framework.begin(), median_framework.end());
  cout << "Framework Background statistics:" << endl;
  cout << "Sessions: " << framework.number_of_sessions << endl;
  cout << "Total seconds: " << framework.total_seconds << endl;
  cout << "Average session length: " << framework.total_seconds / framework.number_of_sessions << endl;
  if (median_framework.size()) {
    cout << "Median session length: " << median_framework[median_framework.size() / 2] << endl;
  }

  cout << "iOS statistics:" << endl;
  cout << "Sessions: " << ios.number_of_sessions << endl;
  cout << "Total seconds: " << ios.total_seconds << endl;
  cout << "Average session length: " << ios.total_seconds / ios.number_of_sessions << endl;
  if (median_ios.size()) {
    cout << "Median session length: " << median_ios[median_ios.size() / 2] << endl;
  }

  cout << "Android statistics:" << endl;
  cout << "Sessions: " << android.number_of_sessions << endl;
  cout << "Total seconds: " << android.total_seconds << endl;
  cout << "Average session length: " << android.total_seconds / android.number_of_sessions << endl;
  if (median_android.size()) {
    cout << "Median session length: " << median_android[median_android.size() / 2] << endl;
  }

  return 0;
}

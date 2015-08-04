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

// Prints events count for every minute during a day.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"
#include "../Alohalytics/queries/processor.h"

#include <chrono>
#include <ctime>
#include <iostream>
#include <map>
#include <set>
#include <string>

using namespace std;

uint64_t TimestampToHourAndMinute(uint64_t timestamp) {
  const time_t timet = static_cast<time_t>(timestamp / 1000);
  const struct tm * stm = gmtime(&timet);
  return stm->tm_hour * 100 + stm->tm_min;
}

int main(int, char **) {
  map<uint64_t, size_t> counters;
  alohalytics::Processor([&counters](const AlohalyticsIdServerEvent *,
                                                      const AlohalyticsBaseEvent * e) {
    ++counters[TimestampToHourAndMinute(e->timestamp)];
  }).PrintStatistics();

  // Print results.
  typedef pair<uint64_t, size_t> TElem;
  const auto comparator = [](const TElem & e1, const TElem & e2){ return e1.second > e2.second; };
  set<TElem, decltype(comparator)> sorted(comparator);
  for (const auto & counter : counters) {
    cout << counter.first << " " << counter.second << endl;
    sorted.insert(counter);
  }
  size_t top_count = 100;
  cout << endl << "Top " << top_count << " minutes of the day with most number of events:";
  for (const auto & counter : sorted) {
    cout << counter.first << " " << counter.second << endl;
    if (--top_count == 0) {
      break;
    }
  }
  return 0;
}

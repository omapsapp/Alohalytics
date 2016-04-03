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

// Calculates percent of users who used Long Tap on a map.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include "../include/processor_light.h"

#include <iostream>
#include <iomanip>
#include <typeinfo>

using namespace std;

int main(int, char **) {

  constexpr const char * kLongTapEvent = "$GetUserMark";
  constexpr const char * kKey = "isLongPress";
  constexpr const char * kYesValue = "1";
//  constexpr const char * kNoValue = "0";

  map<AlohaID, size_t> users;

  alohalytics::ProcessorLight([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && kpe->key == kLongTapEvent) {
      auto & u = users[se->id];
      auto const found = kpe->pairs.find(kKey);
      if (found != kpe->pairs.end()) {
        if (found->second == kYesValue) {
          ++u;
        }
      }
    }
  });

  size_t longtap = 0;
  for (const auto & u : users) {
    if (u.second) {
      ++longtap;
    }
  }

  cout << "Total unique users: " << users.size() << endl;
  cout << "Users with at least one long tap event: " << longtap << " (" << 100. * longtap / users.size() << "%)" << endl;

  return 0;
}

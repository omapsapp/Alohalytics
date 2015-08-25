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

// Prints detailed device info for users with specified events.

#include "../include/processor.h"

#include <map>
#include <set>
#include <vector>

using namespace alohalytics;
using namespace std;

void PrintUserInfo(const pair<string, map<string, string>> & user) {
  cout << "ID: " << user.first << endl;
  for (const auto & kv : user.second) {
    cout << kv.first << ": " << kv.second << endl;
  }
}

int main(int argc, char ** argv) {
  if (argc < 2) {
    cout << "Usage: " << argv[0] << " [--all] [event_key1] [event_key2] [..]" << endl;
    cout << "       Prints detailed info about all users if --all key was specified." << endl;
    cout << "       Prints detailed info about users who has given events (keys) in the flow." << endl;
    return -1;
  }

  vector<string> keys_required_in_user_events;
  if (argv[1] != string("--all")) {
    keys_required_in_user_events.assign(argv + 1, argv + argc);
  }

  // <ID, <info key, value>>
  map<string, map<string, string>> info;
  // <ID, <event, number of matched events>>
  map<string, map<string, size_t>> matched_user_ids;

  Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    // Store IDs of users with specified keys.
    for (const auto & key : keys_required_in_user_events) {
      if (e->key == key) {
        ++matched_user_ids[se->id][key];
      }
    }
    // Extract detailed device info.
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && (kpe->key == "$androidIds" || kpe->key == "$androidDeviceInfo" || kpe->key == "$iosDeviceInfo" ||
                kpe->key == "$iosDeviceIds")) {
      for (const auto & pair : kpe->pairs) {
        info[se->id][pair.first] = pair.second;
      }
      info[se->id]["serverUserAgent"] = se->user_agent;
    }
  }).PrintStatistics();

  if (keys_required_in_user_events.empty()) {
    // Print all results if no filtering was given.
    for (const auto & user : info) {
      PrintUserInfo(user);
      cout << endl;
    }
  } else {
    // Print only info about users with specified events.
    if (matched_user_ids.empty()) {
      cout << "There are no users with specified events." << endl;
    }
    for (const auto & id : matched_user_ids) {
      const auto found = info.find(id.first);
      if (found != info.end()) {
        cout << "Matched events: ";
        for (const auto & e : id.second) {
          cout << e.first << "(" << e.second << ") ";
        }
        cout << endl;
        PrintUserInfo(*found);
        cout << endl;
      }
    }
  }

  return 0;
}

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

#include "../include/processor_light.h"
#include "../include/time_helpers.h"

#include <fstream>
#include <iostream>
#include <set>
#include <string>
#include <unordered_map>

using namespace std;

typedef std::string AlohaID;

struct UserInfo {
  // Last time when user was seen as active.
  uint64_t timestamp = 0;
  // Google id or IDFA.
  string id;
};

int main(int argc, char ** argv) {

  if (argc < 2) {
    cout << "Prints IDFAs/Google IDS of users who did not use app after specified date." << endl;
    cout << "Usage: " << argv[0] << " YYYY-MM-DD [out-ios-ids.txt] [out-android-ids.txt]" << endl;
    return -1;
  }

  // Throws on parsing error.
  uint64_t const last_usage_date = time_helpers::TimestampFromDate(argv[1]);

  string ios_out_file, android_out_file;
  if (argc > 2)
    ios_out_file = argv[2];
  else
    ios_out_file = string("ActiveBeforeDateIosIds-") + argv[1] + string(".txt");
  if (argc > 3)
    android_out_file = argv[3];
  else
    android_out_file = string("ActiveBeforeDateAndroidIds-") + argv[1] + string(".txt");

  unordered_map<AlohaID, UserInfo> users;
  alohalytics::ProcessorLight([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e){

    uint64_t valid_timestamp;
    // Replace invalid client timestamps with valid ones from the server.
    if (time_helpers::IsEventTimestampValid(e->timestamp)) {
      valid_timestamp = e->timestamp;
    } else {
      valid_timestamp = se->timestamp;
    }

    // Update to the newest timestamp.
    auto & ts = users[se->id].timestamp;
    if (ts < valid_timestamp)
      ts = valid_timestamp;

    // Find ids.
    if (e->key == "$androidIds") {
      const auto & pairs = static_cast<const AlohalyticsKeyPairsEvent *>(e)->pairs;
      const auto found = pairs.find("google_advertising_id");
      if (found != pairs.end()) {
        users[se->id].id = found->second;
      }
    } else if (e->key == "$iosDeviceIds") {
      const auto & pairs = static_cast<const AlohalyticsKeyPairsEvent *>(e)->pairs;
      const auto found = pairs.find("advertisingIdentifier");
      if (found != pairs.end()) {
        users[se->id].id = found->second;
      }
    }
  });

  cout << "Total users count: " << users.size() << endl;

  // Check all collected data and leave only users who did not use the app after given date.
  // Also filter out users without any IDFA or Google ID.
  size_t users_after_date = 0, empty_ids = 0, empty_and_after = 0;
  set<string> ios, android;
  for (const auto & user : users) {
    if (user.second.id.empty()) {
      ++empty_ids;
      if (user.second.timestamp > last_usage_date) {
        ++empty_and_after;
      }
      continue;
    }
    if (user.second.timestamp > last_usage_date) {
      ++users_after_date;
      continue;
    }
    if (user.first[0] == 'A')
      android.insert(user.second.id);
    else
      ios.insert(user.second.id);
  }

  cout << "Users with empty ids: " << empty_ids << endl;
  cout << "Users with non-empty ids who used app after " << argv[1] << ": " << users_after_date << endl;
  cout << "Total users who used app after " << argv[1] << ": " << users_after_date + empty_and_after << endl;

  // Output results.
  cout << "Storing " << ios.size() << " iOS ids to " << ios_out_file << endl;
  {
    ofstream out(ios_out_file);
    for (const auto & id : ios)
      out << id << endl;
  }
  cout << "Storing " << android.size() << " Android ids to " << android_out_file << endl;
  {
    ofstream out(android_out_file);
    for (const auto & id : android)
      out << id << endl;
  }
  return 0;
}

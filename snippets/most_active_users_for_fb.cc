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

// Dumps slightly filtered sessions for most active users during a long time period.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"
#include "../Alohalytics/src/file_manager.h"

#include <chrono>
#include <iomanip>
#include <iostream>
#include <memory>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>

using namespace std;

bool HasKey(const char * key, const unique_ptr<AlohalyticsBaseEvent> & e) {
  const AlohalyticsKeyEvent * key_event = dynamic_cast<const AlohalyticsKeyEvent *>(e.get());
  if (key_event && key_event->key == key) {
    return true;
  }
  return false;
}

// bool HasKeyValue(const char * key, const char * value, const unique_ptr<AlohalyticsBaseEvent> & e) {
//  const AlohalyticsKeyValueEvent * kv_event = dynamic_cast<const AlohalyticsKeyValueEvent *>(e.get());
//  if (kv_event && kv_event->key == key && kv_event->value == value) {
//    return true;
//  }
//  return false;
//}

// bool HasPair(const char * pair_key, const char * pair_value, const unique_ptr<AlohalyticsBaseEvent> & e) {
//  const AlohalyticsKeyPairsEvent * pairs_event = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e.get());
//  if (pairs_event) {
//    const auto found = pairs_event->pairs.find(pair_key);
//    if (found != pairs_event->pairs.end() && found.second == pair_value) {
//      return true;
//    }
//  }
//  return false;
//}

// Event finders.
struct TimestampSorter {
  bool operator()(const unique_ptr<AlohalyticsBaseEvent> & e1, const unique_ptr<AlohalyticsBaseEvent> & e2) const {
    return e1->timestamp < e2->timestamp;
  }
};
typedef set<unique_ptr<AlohalyticsBaseEvent>, TimestampSorter> TEventsContainer;
bool HasInstallEvent(const TEventsContainer & events) {
  for (const auto & e : events) {
    if (HasKey("$install", e)) {
      return true;
    }
  }
  return false;
}

// int IndexOfFirstKey(const char * key, const TEventsContainer & events) {
//  int index = 0;
//  for (const auto & e : events) {
//    if (HasKey(key, e)) {
//      return index;
//    }
//    ++index;
//  }
//  return -1;
//}

// int IndexOfFirstKeyValue(const char * key, const char * value, const TEventsContainer & events) {
//  int index = 0;
//  for (const auto & e : events) {
//    if (HasKeyValue(key, value, e)) {
//      return index;
//    }
//    ++index;
//  }
//  return -1;
//}

// bool IsKeyBeforeKeyValue(const char * key,
//                         const char * after_key,
//                         const char * after_value,
//                         const TEventsContainer & events) {
//  int key_index = -1, after_key_index = -1;
//  for (size_t i = 0; i < events.size(); ++i) {
//    if (key_index == -1) {
//      if (HasKey(key, events[i])) {
//        key_index = static_cast<int>(i);
//        continue;
//      }
//    }
//    if (after_key_index == -1) {
//      if (HasKeyValue(after_key, after_value, events)) {
//        after_key_index = static_cast<int>(i);
//        continue;
//      }
//    }
//  }
//  return
//}

// bool HasTwoConsequentKeyValuePairs(
//    const char * key1, const char * value1, const char * key2, const char * value2, const TEventsContainer & events) {
//  for (size_t i = 0; i < events.size(); ++i) {
//    if (HasKeyValue(key1, value1, events[i])) {
//      if (i + 1 != events.size() && HasKeyValue(key2, value2, events[i + 1])) {
//        return true;
//      }
//    }
//  }
//  return false;
//}

int main(int argc, char ** argv) {
  if (argc < 2) {
    cout << "Usage: " << argv[0] << " <directory to store user sessions>" << endl;
    return -1;
  }
  string directory = argv[1];
  alohalytics::FileManager::AppendDirectorySlash(directory);
  string current_user_id;
  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr;
  uint64_t total_events_processed = 0;
  unordered_map<string, TEventsContainer> users;
  const char * filtered_keys[] = {"Android_Parse_Installation_Id",
                                  "$androidIds",
                                  "Android_Parse_Device_Token",
                                  "iOSPushDeviceToken",
                                  "$iosDeviceIds",
                                  "$browserUserAgent"};
  auto const start_time = chrono::system_clock::now();
  while (true) {
    try {
      ar(ptr);
    } catch (const cereal::Exception & ex) {
      if (string("Failed to read 4 bytes from input stream! Read 0") != ex.what()) {
        // The exception above is a normal one, Cereal lacks to detect the end of the stream.
        cout << ex.what() << endl;
      }
      break;
    }
    AlohalyticsIdServerEvent const * id_event = dynamic_cast<AlohalyticsIdServerEvent const *>(ptr.get());
    if (id_event) {
      current_user_id = id_event->id;
    } else {
      // Skip filtered events.
      for (const char * key : filtered_keys) {
        if (HasKey(key, ptr)) {
          goto LSkip;
        }
      }
      // Filter Android-specific duplicate events.
      if (HasKey("$onResume", ptr) || HasKey("$onPause", ptr)) {
        if (string::npos != static_cast<const AlohalyticsKeyValueEvent *>(ptr.get())->value.find("Fragment")) {
          goto LSkip;
        }
      }
      users[current_user_id].emplace(move(ptr));
    LSkip:;
    }
    ++total_events_processed;
  }

  const auto longest_activity_sorter = [](const TEventsContainer & c1, const TEventsContainer & c2) {
    return c2.rbegin()->get()->timestamp - c2.begin()->get()->timestamp <
           c1.rbegin()->get()->timestamp - c1.begin()->get()->timestamp;
  };
  set<TEventsContainer, decltype(longest_activity_sorter)> sorted_by_activity(longest_activity_sorter);
  for (auto & user : users) {
    // Filter out short sessions.
    if (user.second.size() <= 7) {
      continue;
    }
    // Filter out sessions without install events.
    if (!HasInstallEvent(user.second)) {
      continue;
    }

    // Store "large" sessions and sort them by the longest user activity.
    sorted_by_activity.emplace(move(user.second));
    /*
    const int onMapDownloadFinished_index = IndexOfFirstKey("OnMapDownloadFinished", user.second);
    const int onMenuClick_index = IndexOfFirstKeyValue("$onClick", "menu", user.second);
    const int onSearchClick_index = IndexOfFirstKeyValue("$onClick", "search", user.second);
    const int onDownloaderClick_index = IndexOfFirstKeyValue("$onClick", "search", user.second);
    const bool search = onMenuClick_index > 0 && (onMenuClick_index + 1) == onSearchClick_index;
    const bool downloader = onMenuClick_index > 0 && (onMenuClick_index + 1) == onDownloaderClick_index;

    if (onMapDownloadFinished_index > 0) {
      if (search && onSearchClick_index > onMapDownloadFinished_index && ) {
        // loaded from map
      }
    }
*/  //    cout << "User " << user.first << " has " << user.second.size() << " events." << endl;
    //    for (const auto & event : user.second) {
    //        cout << event << endl;
    //      }
    //      cout << endl;
    //    }
  }
  cerr << "Total unique users: " << users.size() << endl;
  cerr << "Total processing time: "
       << std::chrono::duration_cast<std::chrono::seconds>(chrono::system_clock::now() - start_time).count()
       << " seconds." << endl;
  cerr << "Total events processed: " << total_events_processed << endl;

  // Take top-200 from all most active users for analysis.
  const int kUsersLimit = 200;
  int current_user = 0;
  for (const auto & user : sorted_by_activity) {
    ostringstream osstream;
    osstream << "user-" << setw(3) << setfill('0') << current_user;
    ofstream ofile(directory + osstream.str());
    for (const auto & e : user) {
      ofile << e->ToString() << endl;
    }
    ++current_user;
    if (current_user >= kUsersLimit) {
      break;
    }
  }

  return 0;
}

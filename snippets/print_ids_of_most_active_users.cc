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

// Calculates statistics about all users and prints to stdout the top of
// most active by date.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include <algorithm>
#include <chrono>
#include <ctime>
#include <iostream>
#include <map>
#include <string>
#include <vector>

using namespace std;

template <typename ContainerT, typename PredicateT>
void Erase_If(ContainerT & container, const PredicateT & predicate) {
  for (auto it = container.begin(), ite = container.end(); it != ite;) {
    if (predicate(*it)) {
      it = container.erase(it);
    } else {
      ++it;
    }
  }
}

// Events before that date have invalid timestamp.
uint64_t StatisticsWasReleasedTimestampMSFromEpoch() {
  time_t timet = time(nullptr);
  struct tm * stm;
  stm = gmtime(&timet);
  stm->tm_year = 2015 - 1900;  // 2015 year
  stm->tm_mon = 2 - 1;         // February
  stm->tm_mday = 27;           // 27th
  timet = mktime(stm);
  return timet * 1000;
}

// Events after this date have invalid timestamp set.
uint64_t ReasonableFutureBoundForTimestampMSFromEpoch() {
  time_t timet = time(nullptr);
  timet += 24 * 60 * 60;  // Now + 1 day, to handle different time zones.
  return timet * 1000;
}

struct Counters {
  bool has_obligatory_key = false;
  //  size_t events_count = 0;
  uint64_t first_event_timestamp = uint64_t(-1);
  uint64_t last_event_timestamp = 0;
};

int main(int argc, char ** argv) {
  if (argc < 2) {
    cout << "Usage: " << argv[0]
         << " <number of top users to print> [event key which should exist in top users sessions]" << endl;
    cout << "       E.g. you can optionally specify $install as a key to include only users with full sessions."
         << endl;
    return -1;
  }
  int maximum_users = std::stoi(argv[1]);
  const string obligatory_key = argc >= 3 ? argv[2] : "";

  string current_user_id;
  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr;
  size_t total_events_processed = 0;
  typedef map<string, Counters> TUsersContainer;
  TUsersContainer users;
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
    // Every sequence of events from one user starts with a special 'id' event.
    AlohalyticsIdServerEvent const * id_event = dynamic_cast<AlohalyticsIdServerEvent const *>(ptr.get());
    if (id_event) {
      current_user_id = id_event->id;
    } else {
      Counters & c = users[current_user_id];
      if (!obligatory_key.empty() && !c.has_obligatory_key) {
        const AlohalyticsKeyEvent * key_event = dynamic_cast<const AlohalyticsKeyEvent *>(ptr.get());
        c.has_obligatory_key = (key_event && key_event->key == argv[2]);
      }
      //      ++c.events_count;
      const uint64_t ts = ptr->timestamp;
      if (c.first_event_timestamp > ts) {
        c.first_event_timestamp = ts;
      } else if (c.last_event_timestamp < ts) {
        c.last_event_timestamp = ts;
      }
      ++total_events_processed;
    }
  }
  cerr << "Total unique users: " << users.size() << endl;
  cerr << "Total events processed: " << total_events_processed << endl;

  if (!obligatory_key.empty()) {
    // Remove users without obligatory events.
    Erase_If(users, [](const TUsersContainer::value_type & user) { return user.second.has_obligatory_key == false; });
    cerr << "Users with " << obligatory_key << " event: " << users.size() << endl;
  }

  // Filter out invalid timestamps.
  const uint64_t start_bound = StatisticsWasReleasedTimestampMSFromEpoch();
  Erase_If(users, [start_bound](const TUsersContainer::value_type & user) {
    return user.second.first_event_timestamp < start_bound;
  });
  cerr << "Users left after filtering out wrong first event dates: " << users.size() << endl;
  const uint64_t end_bound = ReasonableFutureBoundForTimestampMSFromEpoch();
  Erase_If(users, [end_bound](const TUsersContainer::value_type & user) {
    return user.second.last_event_timestamp == 0 || user.second.last_event_timestamp > end_bound;
  });
  cerr << "Users left after filtering out wrong last event dates: " << users.size() << endl;

  // Sort users by the longest activity period, descending.
  typedef pair<string, Counters> TElement;
  vector<TElement> sorted;
  for (auto & user : users) {
    sorted.emplace_back(move(user));
  }
  const auto sort_lambda = [](const TElement & e1, const TElement & e2) {
    return e1.second.last_event_timestamp - e1.second.first_event_timestamp >
           e2.second.last_event_timestamp - e2.second.first_event_timestamp;
  };
  sort(sorted.begin(), sorted.end(), sort_lambda);

  cerr << "Total processing time: "
       << std::chrono::duration_cast<std::chrono::seconds>(chrono::system_clock::now() - start_time).count()
       << " seconds." << endl;

  // Print top user IDs.
  for (const auto & user : sorted) {
    cout << user.first << endl;
    if (--maximum_users <= 0) {
      break;
    }
  }
  return 0;
}

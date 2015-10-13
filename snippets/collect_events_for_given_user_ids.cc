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

// Stores given user's events in a separate file (one file per user).
// Events also sorted by timestamp.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"
#include "../Alohalytics/src/file_manager.h"

#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

int main(int argc, char ** argv) {
  if (argc < 3) {
    cerr << "Usage: " << argv[0] << " <input file with user ids> <output directory to store users' events>" << endl;
    return -1;
  }

  unordered_set<string> ids_to_match;
  {
    ifstream ifile(argv[1]);
    string line;
    while (ifile) {
      getline(ifile, line);
      if (!line.empty()) {
        ids_to_match.insert(line);
      }
    }
  }
  if (ids_to_match.empty()) {
    cerr << "ERROR: Can't load user ids from " << argv[1] << endl;
    return -1;
  }

  string out_directory = argv[2];
  alohalytics::FileManager::AppendDirectorySlash(out_directory);
  if (!alohalytics::FileManager::IsDirectoryWritable(out_directory)) {
    cerr << "ERROR: Directory " << out_directory << " is not writable." << endl;
    return -1;
  }

  string current_user_id;
  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr;
  size_t total_events_processed = 0;
  map<string, vector<unique_ptr<AlohalyticsBaseEvent>>> users;
  map<string, unique_ptr<AlohalyticsBaseEvent>> ids;
  bool collect_events_for_this_user = false;
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
      collect_events_for_this_user = ids_to_match.find(current_user_id) != ids_to_match.end();
      if (collect_events_for_this_user) {
        ids[current_user_id] = move(ptr);
      }
    } else {
      ++total_events_processed;
      if (collect_events_for_this_user) {
        users[current_user_id].emplace_back(move(ptr));
      }
    }
  }

  // Sort all collected events by their timestamp.
  // TODO(AlexZ): do we really need this sorting? Timestamps should be already guaranteed to always grow up.
  const auto sorter = [](const unique_ptr<AlohalyticsBaseEvent> & e1, const unique_ptr<AlohalyticsBaseEvent> & e2) {
    return e1->timestamp < e2->timestamp;
  };
  for (auto it = users.begin(), ite = users.end(); it != ite; ++it) {
    stable_sort(it->second.begin(), it->second.end(), sorter);
  }

  for (const auto & user : users) {
    ofstream ofile(out_directory + user.first, ofstream::out | ofstream::binary | ofstream::trunc);
    { cereal::BinaryOutputArchive(ofile) << ids[user.first]; }
    for (const auto & e : user.second) {
      // Serialize event back into a binary form.
      { cereal::BinaryOutputArchive(ofile) << e; }
    }
  };

  cerr << "Found events for " << users.size() << " out of " << ids_to_match.size() << " users." << endl;
  cerr << "Total processing time: "
       << std::chrono::duration_cast<std::chrono::seconds>(chrono::system_clock::now() - start_time).count()
       << " seconds." << endl;
  cerr << "Total events processed: " << total_events_processed << endl;

  return 0;
}

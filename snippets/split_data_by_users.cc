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

// Stores each user's events in a separate file (one file per unique user).
// Please note, that all events are not sorted by timestamp.
// Sorting can be done separately by using ...

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

typedef map<string, vector<unique_ptr<AlohalyticsBaseEvent>>> TUsersAndEventsContainer;

inline string FilePathFromUserId(const string & id, const string & ios_dir, const string & android_dir) {
  return id[0] == 'A' ? android_dir + id : ios_dir + id;
}

int main(int argc, char ** argv) {
  if (argc < 3) {
    cout << "Usage: " << argv[0] << " <iOS users dir> <Android users dir>" << endl;
    cout << "       Warning! Make sure that directories are empty." << endl;
    cout << "       This snippet dumps all created file names to stdout." << endl;
    return -1;
  }
  string ios_directory = argv[1], android_directory = argv[2];
  alohalytics::FileManager::AppendDirectorySlash(ios_directory);
  alohalytics::FileManager::AppendDirectorySlash(android_directory);

  const auto events_flusher = [&ios_directory, &android_directory](const TUsersAndEventsContainer & users) {
    for (const auto & user : users) {
      ofstream file(FilePathFromUserId(user.first, ios_directory, android_directory),
                    ofstream::out | ofstream::binary | ofstream::app);
      for (const auto & e : user.second) {
        // Serialize event back into a binary form.
        ostringstream sstream;
        { cereal::BinaryOutputArchive(sstream) << e; }
        file << sstream.str();
      }
    }
  };

  string current_user_id;
  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr;
  size_t total_events_processed = 0;
  const size_t kFlushUsersLimit = 100000;
  TUsersAndEventsContainer users;
  set<string> user_ids;
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
      // Just to count unique users.
      user_ids.insert(current_user_id);
      users[current_user_id].emplace_back(move(ptr));
      ++total_events_processed;
      // Flush data to disk to avoid high memory consumption.
      if (users.size() > kFlushUsersLimit) {
        events_flusher(users);
        users.clear();
      }
    }
  }
  // Flush remaining events.
  events_flusher(users);
  users.clear();

  cerr << "Total unique users: " << user_ids.size() << endl;
  cerr << "Total processing time: "
       << std::chrono::duration_cast<std::chrono::seconds>(chrono::system_clock::now() - start_time).count()
       << " seconds." << endl;
  cerr << "Total events processed: " << total_events_processed << endl;

  // Dump all file paths to stdout for easier future access.
  for (const auto & id : user_ids) {
    cout << FilePathFromUserId(id, ios_directory, android_directory) << endl;
  }

  return 0;
}

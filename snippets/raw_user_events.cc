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

// This snippet simply dumps to stdout every matched event with a given key.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include <chrono>
#include <iostream>
#include <unordered_map>
#include <memory>
#include <string>

using namespace std;

int main(int argc, char ** argv) {
  if (argc < 2) {
    cout << "Usage: cat <data files> | " << argv[0] << endl;
    return -1;
  }
  string current_user_id;
  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr;
  uint64_t total_events_processed = 0;
  unordered_map<string, vector<string>> events;
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
      events[current_user_id].emplace_back(move(ptr->ToString()));
    }
    ++total_events_processed;
  }

  for (const auto & user : events) {
    cout << "User " << user.first << " has " << user.second.size() << " events." << endl;
    for (const auto & event : user.second) {
      cout << event << endl;
    }
    cout << endl;
  }

  cerr << "Total processing time: "
       << std::chrono::duration_cast<std::chrono::seconds>(chrono::system_clock::now() - start_time).count()
       << " seconds." << endl;
  cerr << "Total events processed: " << total_events_processed << endl;
  return 0;
}

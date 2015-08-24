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

// Removes all events except those from Android users with given IMEIs and Android IDs.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

typedef vector<unique_ptr<AlohalyticsBaseEvent>> TEventsContainer;

void SerializeEvents(TEventsContainer & events) {
  for (const auto & e : events) {
    cereal::BinaryOutputArchive(std::cout) << e;
  }
}

int main(int argc, char * argv[]) {
  if (argc < 2) {
    cerr << "Usage: " << argv[0] << " <IMEI + optional android_id file>" << endl;
    cerr << "  Please use commas or spaces to separate id from IMEI" << endl;
    return -1;
  }
  // Load list of "IMEI[ android_id]\n" from file.
  // Maps are mirrored, and used for faster match by imei and by android_id.
  map<string, string> imeis, android_ids;
  {
    ifstream file(argv[1]);
    string line;
    while (file) {
      getline(file, line);
      if (line.empty()) {
        continue;
      }
      size_t separator = line.find(',');
      if (separator == string::npos) {
        separator = line.find(' ');
        if (separator == string::npos) {
          imeis[line] = string();
          continue;
        }
      }
      const string imei(line.substr(0, separator));
      const string aid(line.substr(separator + 1, string::npos));
      imeis[imei] = aid;
      android_ids[aid] = imei;
    }
  }
  // Debug output.
  cerr << "Loaded " << android_ids.size() << " Android IDs and " << imeis.size() << " IMEIs" << endl;

  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr, id_ptr;
  TEventsContainer events;
  bool matched = false;
  size_t android_id_counter = 0, imei_counter = 0;
  while (true) {
    try {
      ar(ptr);
    } catch (const cereal::Exception & ex) {
      if (string("Failed to read 4 bytes from input stream! Read 0") != ex.what()) {
        // The exception above is a normal one, Cereal lacks to detect the end of the stream.
        cerr << ex.what() << endl;
      }
      // Process the last event too.
      if (matched) {
        SerializeEvents(events);
        matched = false;
      }
      break;
    }
    AlohalyticsIdServerEvent const * id_event = dynamic_cast<AlohalyticsIdServerEvent const *>(ptr.get());
    if (id_event) {
      if (matched) {
        SerializeEvents(events);
        matched = false;
      }
      events.clear();
    } else {
      AlohalyticsKeyPairsEvent const * kpe = dynamic_cast<AlohalyticsKeyPairsEvent const *>(ptr.get());
      if (kpe && kpe->key == "$androidIds") {
        for (const auto & kv : kpe->pairs) {
          if (kv.first == "android_id") {
            if (android_ids.find(kv.second) != android_ids.end()) {
              ++android_id_counter;
              matched = true;
            }
          } else if (kv.first == "device_id") {
            if (imeis.find(kv.second) != imeis.end()) {
              ++imei_counter;
              matched = true;
            }
          }
        }
      }
    }
    events.emplace_back(move(ptr));
  }
  // Debug print.
  cerr << "Matched Android IDs: " << android_id_counter << endl;
  cerr << "Matched IMEIs: " << imei_counter << endl;
  return 0;
}

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

// Calculates statistics for very first sessions (immediately after app install).
// Throws out all events before install and all events after given seconds interval.

#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include <map>
#include <set>
#include <string>

using namespace alohalytics;
using namespace std;

int main(int argc, char ** argv) {
  if (argc < 2) {
    cout << "Usage: " << argv[0] << " <seconds after install to filter out>" << endl;
    return -1;
  }
  const uint64_t ms_after_install = stol(argv[1]) * 1000;
  map<string, vector<unique_ptr<AlohalyticsBaseEvent>>> events;
  cereal::BinaryInputArchive ar(std::cin);
  std::unique_ptr<AlohalyticsBaseEvent> ptr, id_ptr;
  string current_id;
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
    AlohalyticsIdServerEvent const * se = dynamic_cast<AlohalyticsIdServerEvent const *>(ptr.get());
    if (se) {
      current_id = se->id;
      id_ptr = move(ptr);
      continue;
    }
    AlohalyticsKeyPairsEvent const * kpe = dynamic_cast<AlohalyticsKeyPairsEvent const *>(ptr.get());
    if (kpe && kpe->key == "$install") {
      events[current_id].emplace_back(move(ptr));
      continue;
    }
    auto found = events.find(current_id);
    if (found != events.end()) {
      const uint64_t install_timestamp = found->second[0]->timestamp;
      if (ptr->timestamp < install_timestamp + ms_after_install) {
        found->second.emplace_back(move(ptr));
      }
    }
  }

  cout << "Found " << events.size() << " users with install sessions." << endl;
  for (const auto & user : events) {
    for (const auto & event : user.second) {
      cout << event->ToString() << endl;
    }
    cout << endl;
  }
  return 0;
}

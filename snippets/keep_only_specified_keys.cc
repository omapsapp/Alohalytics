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

// Removes all keys except specified and writes them to stdout.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include <iostream>
#include <vector>

using namespace std;

int main(int argc, char * argv[]) {
  if (argc < 2) {
    cerr << "Usage: " << argv[0] << " <key to retain> [another key to retain] ..." << endl;
    return -1;
  }
  const vector<string> keys_to_retain(argv + 1, argv + argc);
  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr, server_id;
  while (true) {
    try {
      ar(ptr);
    } catch (const cereal::Exception & ex) {
      if (string("Failed to read 4 bytes from input stream! Read 0") != ex.what()) {
        // The exception above is a normal one, Cereal lacks to detect the end of the stream.
        cerr << ex.what() << endl;
      }
      break;
    }
    AlohalyticsIdServerEvent const * event = dynamic_cast<AlohalyticsIdServerEvent const *>(ptr.get());
    if (event) {
      // ID event should be first one in the output in the only one case:
      // if any of given keys was matched.
      server_id = move(ptr);
    } else {
      AlohalyticsKeyEvent const * event = dynamic_cast<AlohalyticsKeyEvent const *>(ptr.get());
      if (!event) {
        continue;
      }
      for (const auto & key : keys_to_retain) {
        if (event->key == key) {
          // Key has matched, write server_id event once.
          if (server_id) {
            cereal::BinaryOutputArchive(std::cout) << server_id;
            server_id.reset(nullptr);
          }
          cereal::BinaryOutputArchive(std::cout) << ptr;
        }
      }
    }
  }
  return 0;
}

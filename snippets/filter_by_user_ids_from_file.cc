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

// Removes all events except those with given user ids loaded from file.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include <fstream>
#include <iostream>
#include <string>
#include <set>

using namespace std;

int main(int argc, char * argv[]) {
  if (argc < 2) {
    cerr << "Usage: " << argv[0] << " <text file with one user id per line>" << endl;
    return -1;
  }
  set<string> user_ids;
  {
    ifstream file(argv[1]);
    string line;
    while (file) {
      getline(file, line);
      if (line.empty()) {
        continue;
      }
      user_ids.insert(line);
    }
  }
  // Debug output.
  cerr << "Loaded " << user_ids.size() << " unique User IDs." << endl;

  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr;
  bool matched = false;
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
    AlohalyticsIdServerEvent const * id_event = dynamic_cast<AlohalyticsIdServerEvent const *>(ptr.get());
    if (id_event) {
      if (user_ids.find(id_event->id) != user_ids.end()) {
        matched = true;
        cereal::BinaryOutputArchive(std::cout) << ptr;
      } else {
        matched = false;
      }
    } else {
      if (matched) {
        cereal::BinaryOutputArchive(std::cout) << ptr;
      }
    }
  }
  return 0;
}

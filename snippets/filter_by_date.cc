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

// Removes events outside of given date range.
// NOTE: ID events timestamp is ignored, only generated events timestamp is checked.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include "../include/time_helpers.h"

#include <iostream>
#include <vector>

#include <string.h>


using namespace std;
using namespace time_helpers;

class InvalidDateException : std::exception {};

const string kStartPrefix = "--start=";
const string kEndPrefix = "--end=";
const uint64_t kMSInOneDay = 24 * 60 * 60 * 1000;

int main(int argc, char * argv[]) {
  if (argc < 2) {
    cerr << "Usage: " << argv[0] << " [--start=2015-06-03] [--end=2015-07-12]" << endl;
    cerr << "  If both start and end are specified, only events in between are left." << endl;
    cerr << "  If only start is specified, all events before start date are removed." << endl;
    cerr << "  If only end is specified, all events after the end date are removed." << endl;
    return -1;
  }
  // Parse command line arguments.
  uint64_t start_ms_from_epoch = 0, end_ms_from_epoch = uint64_t(-1);
  const string argv1(argv[1]);
  if (argv1.find(kStartPrefix) == 0) {
    start_ms_from_epoch = TimestampFromDate(argv1.substr(kStartPrefix.size()));
  } else if (argv1.find(kEndPrefix) == 0) {
    end_ms_from_epoch = TimestampFromDate(argv1.substr(kEndPrefix.size()));
    // Last day should be fully included.
    end_ms_from_epoch += kMSInOneDay;
  } else {
    cerr << "ERROR: Please specify start or end date in valid format." << endl;
    return -1;
  }
  if (argc >= 3) {
    const string argv2(argv[2]);
    if (argv2.find(kEndPrefix) == 0) {
      end_ms_from_epoch = TimestampFromDate(argv2.substr(kEndPrefix.size()));
      // Last day should be fully included.
      end_ms_from_epoch += kMSInOneDay;
    } else if (argv2.find(kStartPrefix) == 0) {
      start_ms_from_epoch = TimestampFromDate(argv2.substr(kStartPrefix.size()));
    } else {
      cerr << "ERROR: Please specify start or end date in valid format." << endl;
      return -1;
    }
  }

  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr, id_ptr;
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
      id_ptr = move(ptr);
    } else {
      if (ptr->timestamp >= start_ms_from_epoch && ptr->timestamp <= end_ms_from_epoch) {
        // id event should be serialized first, and only once.
        if (id_ptr) {
          cereal::BinaryOutputArchive(std::cout) << id_ptr;
          id_ptr.reset();
        }
        cereal::BinaryOutputArchive(std::cout) << ptr;
      }
    }
  }
  return 0;
}

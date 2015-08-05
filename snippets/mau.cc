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

// Calculates total number of unique active users.
// Dumps one user id per line if launched with --print_ids argument.
//
// NOTE: Pass events to this snippet after filter_by_date.cc to correctly calculate MAU for given time period.
// Example: $ cat alohalytics_messages | ./filter_by_date --start=2015-06-01 --end=2015-06-30 | ./mau

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"
#include "../Alohalytics/queries/processor.h"

#include <iostream>

using namespace std;

int main(int argc, char ** argv) {
  alohalytics::Processor processor([](const AlohalyticsIdServerEvent *, const AlohalyticsBaseEvent *){
    // Empty lambda body, because Processor allready calculates active users.
  });

  if (argc > 1 && string(argv[1]) == "--print_ids") {
    for (const auto & id : processor.unique_user_ids) {
      cout << id << endl;
    }
  } else {
    cout << "Total unique active users count: " << processor.unique_user_ids.size() << endl;
  }
  return 0;
}

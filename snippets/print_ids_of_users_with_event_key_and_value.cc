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

// Prints to stdout ids of users who have specified events with key and value in them.
// Value is matched as a substring.
// User ids are not unique and can repeat itself!

#include "../Alohalytics/src/processor.h"

using namespace std;

int main(int argc, char ** argv) {
  if (argc < 4) {
    cout << "Usage: " << argv[0] << " <event name> <key> <value substring>" << endl;
    return -1;
  }
  const string name = argv[1];
  const string key = argv[2];
  const string value = argv[3];

  alohalytics::Processor([&](const AlohalyticsIdServerEvent * ie, const AlohalyticsKeyEvent * e) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && kpe->key == name) {
      const auto found = kpe->pairs.find(key);
      if (found != kpe->pairs.end() && found->second.find(value) != string::npos) {
        cout << ie->id << endl;
      }
    }
  }).PrintStatistics();
  return 0;
}

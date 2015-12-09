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

#include "../include/processor.h"

#include <iostream>
#include <map>

using namespace std;

int main(int argc, char ** argv) {
  map<string, pair<uint64_t, size_t>> users;
  alohalytics::Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    auto & p = users[se->id];
    if (p.first > e->timestamp) {
      ++p.second;
      p.first = e->timestamp;
    }
  }).PrintStatistics();

  size_t num_users = 0, num_events = 0;
  for (const auto & user : users) {
    if (user.second.second) {
      ++num_users;
      num_events += user.second.second;
    }
  }
  cout << "Users with bad event timestamps: " << num_users << " total events: " << num_events << endl;

  return 0;
}

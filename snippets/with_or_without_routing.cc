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

// Calculates daily statistics about map downloads with and without routing files.

#include "../include/processor.h"

#include <iostream>
#include <map>

using namespace std;

struct Stats {
  size_t MapOnly = 0;
  size_t CarRouting = 0;
  size_t MapWithCarRouting = 0;
};

int main(int, char **) {
  map<string, Stats> versions;
  alohalytics::Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * ke) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(ke);
    if (kpe && kpe->key == "$OnMapDownloadFinished") {
      const auto found = kpe->pairs.find("option");
      if (found == kpe->pairs.end()) {
        cerr << "Err: no options in event?" << endl;
        return;
      }
      const string opt = found->second;
      if (opt == "MapOnly") {
        ++versions[se->uri].MapOnly;
      } else if (opt == "MapWithCarRouting") {
        ++versions[se->uri].MapWithCarRouting;
      } else if (opt == "CarRouting") {
        ++versions[se->uri].CarRouting;
      }
    }
  }).PrintStatistics();

  for (const auto & version : versions) {
    cout << "Version: " << version.first << endl;
    const size_t total = version.second.MapOnly + version.second.CarRouting +
        version.second.MapWithCarRouting;
    cout << "Map only    : " << std::fixed << std::setprecision(1) << version.second.MapOnly * 100. / total << "%" << endl;
    cout << "Map+Routing : " << std::fixed << std::setprecision(1) << version.second.MapWithCarRouting * 100. / total << "%" << endl;
    cout << "Routing only: " << std::fixed << std::setprecision(1) << version.second.CarRouting * 100. / total << "%" << endl;
    cout << endl;
  }
  return 0;
}

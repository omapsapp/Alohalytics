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
  size_t Nothing = 0;
};

int main(int argc, char **) {
  bool success_only = true;
  if (argc > 1) {
    success_only = false;
  }
  map<string, Stats> versions;
  alohalytics::Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * ke) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(ke);
    if (kpe && kpe->key == "$OnMapDownloadFinished") {
      if (success_only) {
        const auto found = kpe->pairs.find("status");
        if (found == kpe->pairs.end()) {
          cerr << "Err: status not found." << endl;
          return;
        }
        if (found->second != "ok") {
          return;
        }
      }
      const auto found = kpe->pairs.find("option");
      if (found == kpe->pairs.end()) {
        cerr << "Err: no options in event?" << endl;
        return;
      }
      const string opt = found->second;
      if (opt == "Map" || opt == "MapOnly") {
        ++versions[se->uri].MapOnly;
      } else if (opt == "MapWithCarRouting") {
        ++versions[se->uri].MapWithCarRouting;
      } else if (opt == "CarRouting") {
        ++versions[se->uri].CarRouting;
      } else if (opt == "Nothing") {
        ++versions[se->uri].Nothing;
      } else {
        cerr << "Err: unknown option " << opt << endl;
      }
    }
  }).PrintStatistics();

  for (const auto & version : versions) {
    cout << "Version: " << version.first << endl;
    const size_t total = version.second.MapOnly + version.second.CarRouting +
        version.second.MapWithCarRouting + version.second.Nothing;
    cout << "Map only    : " << std::fixed << std::setprecision(1) << version.second.MapOnly * 100. / total << "% (" << version.second.MapOnly << ")" << endl;
    cout << "Map+Routing : " << version.second.MapWithCarRouting * 100. / total << "% (" << version.second.MapWithCarRouting << ")" << endl;
    cout << "Routing only: " << version.second.CarRouting * 100. / total << "% (" << version.second.CarRouting << ")" << endl;
    cout << "Nothing     : " << version.second.Nothing * 100. / total << "% (" << version.second.Nothing << ")" << endl;
    cout << endl;
  }
  return 0;
}

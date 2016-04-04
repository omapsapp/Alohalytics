/*******************************************************************************
 The MIT License (MIT)

 Copyright (c) 2016 Alexander Zolotarev <me@alex.bio> from Minsk, Belarus

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

// Prints statistics about successfully downloaded mwm files.

#include "../include/mapsme_events.h"
#include "../include/mapsme_helpers.h"
#include "../include/processor_light.h"
#include "../include/time_helpers.h"

#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <string>

using namespace std;

int main(int, char **) {

  map<string, set<AlohaID>> maps;
  alohalytics::ProcessorLight([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e){

    if (e->key == COUNTRY_DOWNLOAD_FINISHED) {
      const auto & pairs = static_cast<const AlohalyticsKeyPairsEvent *>(e)->pairs;
      const auto mwm = pairs.find("name");
      const auto status = pairs.find("status");
      if (mwm != pairs.end() && status != pairs.end() && status->second == "ok") {
        maps[mapsme_helpers::NormalizeDownloadedCountry(mwm->second)].insert(se->id);
      }
    }
  });

  uint64_t total = 0;
  for (const auto & map : maps) {
    cout << map.first << ": " << map.second.size() << endl;
    total += map.second.size();
  }

  cout << "Total maps downloaded: " << total << endl;
  return 0;
}

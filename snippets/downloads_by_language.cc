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

// Prints download stats, one user per line:
// ID;Language;Austria[2015-06-01]Belgium[2015-07-22]...
// Further stats can be easily calculated with grep.
// Note: failed map download attempts are not filtered out.

#include "../include/mapsme_helpers.h"
#include "../include/processor_light.h"
#include "../include/time_helpers.h"

#include <fstream>
#include <iostream>
#include <set>
#include <string>
#include <unordered_map>

using namespace std;

struct UserInfo {
  string language;
  // <map name, download date>
  map<string, uint64_t> maps;
};

int main(int, char **) {

  unordered_map<AlohaID, UserInfo> users;
  alohalytics::ProcessorLight([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e){

    if (e->key == "$iosDeviceInfo") {
      const auto & pairs = static_cast<const AlohalyticsKeyPairsEvent *>(e)->pairs;
      const auto found = pairs.find("localeIdentifier");
      if (found != pairs.end()) {
        users[se->id].language = found->second;
      }
    } else if (e->key == "$androidDeviceInfo") {
      const auto & pairs = static_cast<const AlohalyticsKeyPairsEvent *>(e)->pairs;
      const auto found = pairs.find("locale_language");
      if (found != pairs.end()) {
        users[se->id].language = found->second;
      }
    } else if (e->key == "$OnMapDownloadFinished") {
      const auto & pairs = static_cast<const AlohalyticsKeyPairsEvent *>(e)->pairs;
      auto found = pairs.find("name");
      if (found != pairs.end()) {
        users[se->id].maps[found->second] =
            time_helpers::FixInvalidClientTimestampIfNeeded(e->timestamp, se->timestamp);
      }
    }
  });

  // Print only users who downloaded at least one map.
  size_t total_maps_downloaded = 0, users_with_at_least_one_download = 0;
  for (const auto & user : users) {
    if (user.second.maps.empty()) {
      continue;
    }
    users_with_at_least_one_download++;
    cout << user.first << ';' << user.second.language << ';';
    for (const auto & m : user.second.maps) {
      cout << m.first << '[' << time_helpers::TimestampToDate(m.second) << ']';
      ++total_maps_downloaded;
    }
  }

  cout << "Total users count: " << users.size() << endl;
  cout << "Users with at least one downloaded map: " << users_with_at_least_one_download << endl;
  cout << "Total maps downloaded: " << total_maps_downloaded << endl;
  return 0;
}

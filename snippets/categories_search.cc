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

// Calculates search by category statistics.

#include "../include/processor.h"

#include "search.h"

#include <map>
#include <set>
#include <string>

using namespace alohalytics;
using namespace std;

int main(int argc, char ** argv) {
  if (argc < 2) {
    cout << "Usage: " << argv[0] << " <categories.txt file to analyze>" << endl;
    cout << "       Please note, you can leave only needed categories in the file." << endl;
    return -1;
  }
  const TCategories categories = LoadCategoriesFromFile(argv[1]);
  map<string, set<string>> users_queries_;
  SearchFilter filter(
      [&users_queries_](const string & user, const string & query, size_t) { users_queries_[user].insert(query); });
  Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && kpe->key == "searchEmitResults") {
      filter.ProcessQuery(se->id, kpe->pairs.begin()->first, 0 /* ignore results count */);
    }
  }).PrintStatistics();

  set<string> users_who_searched_by_category;
  // <category, users count>
  map<string, size_t> counters;
  for (const auto & user : users_queries_) {
    for (const auto & query : user.second) {
      for (const auto & category : categories) {
        for (const auto & synonym : category.second) {
          if (query == synonym) {
            ++counters[category.first];
            users_who_searched_by_category.insert(user.first);
            break;
          }
        }
      }
    }
  }
  const size_t uc = users_queries_.size();
  cout << "Users with at least one searchEmitResults event: " << uc << endl;
  cout << "Users with at least one category search: " << users_who_searched_by_category.size() << endl;

  multimap<size_t, string> sorted_by_count;
  for (const auto & c : counters) {
    sorted_by_count.emplace(c.second, c.first);
  }
  for (auto it = sorted_by_count.rbegin(); it != sorted_by_count.rend(); ++it) {
    cout << it->first << " " << it->second << endl;
  }
  return 0;
}

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

// Calculates statistics for all search queries.

#include "../include/processor.h"

#include "search.h"

#include <map>
#include <set>
#include <string>

using namespace alohalytics;
using namespace std;

struct TQuery {
  string query_;
  size_t results;
  bool operator<(const TQuery & other) const { return query_ < other.query_; }
};

int main(int argc, char ** argv) {
  if (argc < 2) {
    cout << "Usage: " << argv[0] << " <categories.txt file to analyze>" << endl;
    cout << "       Please note, you can leave only needed categories in the file." << endl;
    return -1;
  }
  const TCategories categories = LoadCategoriesFromFile(argv[1]);
  map<string, multiset<TQuery>> users_queries_;
  SearchFilter filter([&users_queries_](const string & user, const string & query, size_t results) {
    TQuery q = {query, results};
    users_queries_[user].emplace(q);
  });
  Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && kpe->key == "searchEmitResults") {
      const auto it = kpe->pairs.begin();
      filter.ProcessQuery(se->id, it->first, static_cast<size_t>(stoi(it->second)));
    }
  }).PrintStatistics();

  cout << "Users with at least one searchEmitResults event: " << users_queries_.size() << endl;

  // <query, <total queries count from all users, sum of all results for this query>>
  map<string, pair<size_t, size_t>> queries_counters;
  for (const auto & user : users_queries_) {
    for (const auto & q : user.second) {
      ++queries_counters[q.query_].first;
      queries_counters[q.query_].second += q.results;
    }
  }
  cout << "Total number of unique search queries: " << queries_counters.size() << endl;

  // The same data but sorted by queries count.
  multimap<size_t, pair<string, size_t>> sorted_by_count;
  for (const auto & query : queries_counters) {
    sorted_by_count.emplace(query.second.first, make_pair(query.first, query.second.second));
  }
  for (auto it = sorted_by_count.rbegin(); it != sorted_by_count.rend(); ++it) {
    const string category = GetQueryCategory(it->second.first, categories, true /* with all synonyms */);
    cout << it->first << " " << it->second.first << " (total results:" << it->second.second;
    if (category.empty()) {
      cout << ")" << endl;
    } else {
      cout << ", " << category << ")" << endl;
    }
  }

  return 0;
}

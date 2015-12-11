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

// This snippet may be used for sampling search queries.
// Example usage:
// cat /mnt/disk1/alohalytics/by_date/alohalytics_messages-20151201.gz | gzip -d | ./build/search_samples --random --top

#include "../include/processor.h"

#include "search.h"

#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstdio>
#include <functional>
#include <map>
#include <random>
#include <set>
#include <string>

using namespace alohalytics;
using namespace std;

// We do not reuse SearchFilter in order not to break current behaviour
// of the scripts relying on it.
struct QueryProcessor {
  const int kTopCount = 100;

  QueryProcessor() = default;

  void AddQuery(const string & user, string query, int numResults) {
    CaseFoldingAndNormalize(query);
    Trim(query);
    if (query.empty()) {
      return;
    }
    if (user != prev_user_) {
      Flush();
      prev_user_ = user;
      prev_query_ = query;
      prev_results_ = numResults;
      return;
    }
    if (StartsWith(query, prev_query_)) {
      prev_query_ = query;
      prev_results_ = numResults;
      return;
    }
    if (StartsWith(prev_query_, query)) {
      return;
    }
    Flush();
    prev_query_ = query;
    prev_results_ = numResults;
  }

  void Flush() {
    if (prev_results_ >= 0) {
      Process(prev_user_, prev_query_, prev_results_);
      prev_user_ = string();
      prev_query_ = string();
      prev_results_ = -1;
    }
  }

  void Process(string user, const string & query, int results) { m_[query].emplace_back(user, results); }

  void PrintEverything() {
    Flush();

    if (printRandom_) {
      PrintRandomSample(kTopCount);
    }
    if (printTop_) {
      PrintTopQueries(kTopCount);
    }
  }

  // Prints at most n random queries.
  void PrintRandomSample(int n) {
    if (m_.empty()) {
      printf("No data.\n");
      return;
    }
    auto seed = chrono::high_resolution_clock::now().time_since_epoch().count();
    mt19937 rng(seed);
    uniform_int_distribution<int> randomDistribution(0, m_.size() - 1);
    vector<string> allQueries;
    allQueries.reserve(m_.size());
    for (auto const & entry : m_) {
      allQueries.emplace_back(entry.first);
    }
    vector<string> res(n);
    for (int i = 0; i < n; i++) {
      res[i] = allQueries[randomDistribution(rng)];
    }
    sort(res.begin(), res.end());
    allQueries.resize(unique(res.begin(), res.end()) - res.begin());
    printf("%d random queries:\n", static_cast<int>(res.size()));
    for (size_t i = 0; i < res.size(); ++i) {
      printf("%s\n", res[i].data());
    }
    printf("\n");
  }

  // Prints top n (by user count) unique queries. Every query is counted at most once for each user.
  // Note that a user's results may vary if the search accounts for anything other
  // than the query string (e.g. for the viewport position) so the number of results
  // that the user got for a query is basically a useless parameter.
  void PrintTopQueries(int n) {
    vector<pair<int, string>> v;
    set<string> allUsers;
    for (auto const & entry : m_) {
      set<string> uniqueUsers;
      for (auto const & p : entry.second) {
        uniqueUsers.insert(p.first);
      }
      allUsers.insert(uniqueUsers.begin(), uniqueUsers.end());
      v.emplace_back(uniqueUsers.size(), entry.first);
    }
    sort(v.begin(), v.end(), greater<pair<int, string>>());
    printf("Top %d queries by unique user count:\n", n);
    for (size_t i = 0; i < static_cast<size_t>(n) && i < v.size(); i++) {
      double percentage = 100.0 * static_cast<double>(v[i].first) / static_cast<double>(allUsers.size());
      printf("%s\t%d (%lf%%)\n", v[i].second.data(), v[i].first, percentage);
    }
    printf("\n");
  }

  map<string, vector<pair<string, int>>> m_;  // query -> [{user, results}]

  string prev_user_;
  string prev_query_;
  int prev_results_ = -1;

  bool printRandom_ = false;
  bool printTop_ = false;
  string printLocale_;      // todo(@m) If not empty, print only the queries in |locale|.
  TCategories categories_;  // todo(@m) Use it.
};

void Usage(char * prog) {
  printf("usage: %s [--random] [--top] [--categories <file>] [--locale <locale>]\n", prog);
  exit(0);
}

void ParseFlags(int argc, char ** argv, QueryProcessor & proc) {
  if (argc < 2) {
    Usage(argv[0]);
  }
  string cmd = argv[0];
  for (int i = 1; i < argc; ++i) {
    string flag(argv[i]);
    if (flag == "-h" || flag == "--help") {
      Usage(argv[0]);
    }
    if (flag == "--random") {
      proc.printRandom_ = true;
      continue;
    }
    if (flag == "--top") {
      proc.printTop_ = true;
      continue;
    }
    assert(i + 1 < argc);
    if (flag == "--categories") {
      proc.categories_ = LoadCategoriesFromFile(argv[i + 1]);
      ++i;
    }
    if (flag == "--locale") {
      proc.printLocale_ = argv[i + 1];
      ++i;
    }
  }
}

int main(int argc, char ** argv) {
  QueryProcessor proc;
  ParseFlags(argc, argv, proc);

  Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && kpe->key == "searchEmitResults") {
      const auto it = kpe->pairs.begin();
      proc.AddQuery(se->id /* user */, it->first /* query */, static_cast<size_t>(stoi(it->second)) /* numResults */);
    }
  }).PrintStatistics();

  proc.PrintEverything();

  return 0;
}

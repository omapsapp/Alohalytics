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
// cat /mnt/disk1/alohalytics/by_date/alohalytics_messages-20160315.gz | gzip -d | ./build/search_samples --random --top
//
// This sample is tailored to be used with the kSearchEmitResultsAndCoords event
// that was introduced around Feb 2016.

#include "../include/mapsme_events.h"
#include "../include/processor.h"
#include "../include/search.h"

#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstdio>
#include <functional>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <string>

using namespace alohalytics;
using namespace std;

const string kSearchEmitResultsAndCoords(SEARCH_EMIT_RESULTS_AND_COORDS);

struct PointD {
  double x_ = 0;
  double y_ = 0;
};

struct RectD {
  double minX_ = 0;
  double minY_ = 0;
  double maxX_ = 0;
  double maxY_ = 0;
};

double ReadDouble(string const & s) {
  istringstream iss(s);
  double x;
  iss >> x;
  return x;
}

void Split(string const & s, char delim, vector<string> & parts) {
  istringstream iss(s);
  string part;
  while (getline(iss, part, delim)) {
    parts.push_back(part);
  }
}

// We do not reuse SearchFilter in order not to break current behaviour
// of the scripts relying on it.
struct QueryProcessor {
  const int kTopCount = 100;

  struct Info {
    PointD pos_;
    RectD viewport_;
    vector<string> results_;

    string ToString() const {
      ostringstream oss;
      oss << "pos=(" << pos_.x_ << "," << pos_.y_ << ")";
      oss << " viewport=("
          << "minX=" << viewport_.minX_ << ","
          << "minY=" << viewport_.minY_ << ","
          << "maxX=" << viewport_.maxX_ << ","
          << "maxY=" << viewport_.maxY_ << ")";
      oss << " results=(";
      for (size_t i = 0; i < results_.size(); ++i) {
        if (i > 0) {
          oss << ",";
        }
        oss << results_[i];
      }
      oss << ")";
      return oss.str();
    }
  };

  void AddQuery(const string & user, string & query, const Info & info) {
    FoldCaseAndNormalize(query);
    Trim(query);
    if (query.empty()) {
      return;
    }
    if (user != prev_user_) {
      Flush();
      prev_user_ = user;
      prev_query_ = query;
      prev_info_ = info;
      needs_flushing_ = true;
      return;
    }
    if (StartsWith(query, prev_query_)) {
      prev_query_ = query;
      prev_info_ = info;
      needs_flushing_ = true;
      return;
    }
    if (StartsWith(prev_query_, query)) {
      return;
    }
    Flush();
    prev_query_ = query;
    prev_info_ = info;
    needs_flushing_ = true;
  }

  // kpe_pairs is the value type of AlohalyticsKeyPairsEvent.
  void AddEmitResultsAndCoordsQuery(const string & user, map<string, string> kpe_pairs) {
    string query;
    Info info;

    // It's better to copy a map than cope with consts here.
    info.pos_.x_ = ReadDouble(kpe_pairs["posX"]);
    info.pos_.y_ = ReadDouble(kpe_pairs["posY"]);
    info.viewport_.minX_ = ReadDouble(kpe_pairs["viewportMinX"]);
    info.viewport_.minY_ = ReadDouble(kpe_pairs["viewportMinY"]);
    info.viewport_.maxX_ = ReadDouble(kpe_pairs["viewportMaxX"]);
    info.viewport_.maxY_ = ReadDouble(kpe_pairs["viewportMaxY"]);
    query = kpe_pairs["query"];
    Split(kpe_pairs["results"], '\t', info.results_);

    AddQuery(user, query, info);
  }

  void Flush() {
    if (!needs_flushing_) {
      return;
    }
    Process(prev_user_, prev_query_, prev_info_);
    prev_user_.clear();
    prev_query_.clear();
    needs_flushing_ = false;
  }

  void Process(string user, const string & query, const Info & info) { m_[query].emplace_back(user, info); }

  void PrintEverything() {
    Flush();

    if (print_all_) {
      PrintAllQueries();
    }
    if (print_random_) {
      PrintRandomSample(kTopCount);
    }
    if (print_top_) {
      PrintTopQueries(kTopCount);
    }
  }

  // Prints all collected queries.
  void PrintAllQueries() {
    for (auto const & entry : m_) {
      for (auto const & p : entry.second) {
        printf("%s\t%s\n", entry.first.data(), p.second.ToString().data());
      }
    }
  }

  // Prints at most n random queries with distinct query strings.
  void PrintRandomSample(int n) {
    if (m_.empty()) {
      return;
    }
    vector<pair<string, Info>> allQueries;
    allQueries.reserve(m_.size());
    for (auto const & entry : m_) {
      for (auto const & p : entry.second) {
        allQueries.emplace_back(entry.first, p.second);
      }
    }

    auto cmp =
        [](const pair<string, Info> & lhs, const pair<string, Info> & rhs) -> bool { return lhs.first < rhs.first; };
    auto eq =
        [](const pair<string, Info> & lhs, const pair<string, Info> & rhs) -> bool { return lhs.first == rhs.first; };

    sort(allQueries.begin(), allQueries.end(), cmp);
    allQueries.resize(unique(allQueries.begin(), allQueries.end(), eq) - allQueries.begin());

    mt19937 rng(seed_);
    shuffle(allQueries.begin(), allQueries.end(), rng);

    n = min(n, static_cast<int>(allQueries.size()));
    for (size_t i = 0; i < static_cast<size_t>(n); ++i) {
      printf("%s\t%s\n", allQueries[i].first.data(), allQueries[i].second.ToString().data());
    }
  }

  // Prints top n (by user count) unique queries. Every query is counted at most once for each user.
  // Note that a user's results may vary if the search accounts for anything other
  // than the query string (e.g. for the viewport position) so it makes no sense
  // to look at the info parameter here.
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
    n = min(n, static_cast<int>(v.size()));
    if (n == 0) {
      return;
    }
    sort(v.begin(), v.end(), greater<pair<int, string>>());
    for (size_t i = 0; i < static_cast<size_t>(n); ++i) {
      double percentage = 100.0 * static_cast<double>(v[i].first) / static_cast<double>(allUsers.size());
      printf("%s\t%d (%lf%%)\n", v[i].second.data(), v[i].first, percentage);
    }
  }

  map<string, vector<pair<string, Info>>> m_;  // query -> [{user, info}]

  string prev_user_;
  string prev_query_;
  Info prev_info_;
  int seed_ = chrono::high_resolution_clock::now().time_since_epoch().count();

  bool needs_flushing_ = false;

  bool print_all_ = false;
  bool print_random_ = false;
  bool print_top_ = false;
  string print_locale_;     // todo(@m) If not empty, print only the queries in |locale|.
  TCategories categories_;  // todo(@m) Use it.
};

void PrintUsageAndExit(char * prog) {
  printf("usage: %s [--help] [--random] [--top] [--categories <file>] [--locale <locale>] [--seed <n>]\n", prog);
  exit(0);
}

void ParseFlags(int argc, char ** argv, QueryProcessor & proc) {
  if (argc < 2) {
    PrintUsageAndExit(argv[0]);
  }
  for (int i = 1; i < argc; ++i) {
    const string flag(argv[i]);
    if (flag == "-h" || flag == "--help") {
      PrintUsageAndExit(argv[0]);
    }
    if (flag == "--all") {
      proc.print_all_ = true;
      continue;
    }
    if (flag == "--random") {
      proc.print_random_ = true;
      continue;
    }
    if (flag == "--top") {
      proc.print_top_ = true;
      continue;
    }
    assert(i + 1 < argc);
    if (flag == "--categories") {
      proc.categories_ = LoadCategoriesFromFile(argv[i + 1]);
      ++i;
    }
    if (flag == "--locale") {
      proc.print_locale_ = argv[i + 1];
      ++i;
    }
    if (flag == "--seed") {
      sscanf(argv[i + 1], "%d", &proc.seed_);
      ++i;
    }
  }
}

int main(int argc, char ** argv) {
  QueryProcessor proc;
  ParseFlags(argc, argv, proc);

  Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && kpe->key == kSearchEmitResultsAndCoords) {
      proc.AddEmitResultsAndCoordsQuery(se->id /* user */, kpe->pairs);
    }
  }).PrintStatistics();

  proc.PrintEverything();

  return 0;
}

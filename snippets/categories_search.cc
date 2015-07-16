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

#include "../Alohalytics/queries/processor.h"
#include "../3party/utf8proc/utf8proc.h"

#include <fstream>
#include <map>
#include <set>
#include <string>

using namespace alohalytics;
using namespace std;

typedef map<string, set<string>> TCategories;

void CaseFoldingAndNormalize(string & s) {
  utf8proc_uint8_t * buf = nullptr;
  const utf8proc_ssize_t ssize = utf8proc_map(reinterpret_cast<const utf8proc_uint8_t *>(s.data()), s.size(), &buf,
                                              static_cast<utf8proc_option_t>(UTF8PROC_COMPAT | UTF8PROC_DECOMPOSE | UTF8PROC_CASEFOLD));
  if (ssize > 0) {
    s.assign(reinterpret_cast<const string::value_type *>(buf), ssize);
  }
  if (buf) {
    free(buf);
  }
}

TCategories LoadCategoriesFromFile(const char * path) {
  enum class State { EParseTypes, EParseLanguages } state = State::EParseTypes;
  TCategories categories;
  string line, current_types;
  ifstream file(path);
  while (file) {
    getline(file, line);
    switch (state) {
      case State::EParseTypes: {
        current_types = line;
        if (!current_types.empty()) state = State::EParseLanguages;
      } break;
      case State::EParseLanguages: {
        size_t pos = line.find(':');
        if (pos == string::npos) {
          state = State::EParseTypes;
          continue;
        }
        while (pos != string::npos) {
          size_t end_pos = line.find('|', pos + 1);
          string name = line.substr(pos + 1, end_pos == string::npos ? end_pos : end_pos - pos - 1);
          pos = end_pos;
          // Fix hint char count number.
          if (name[0] >= '0' && name[0] <= '9') {
            name = name.substr(1);
          }
          CaseFoldingAndNormalize(name);
          categories[current_types].insert(name);
        }
      } break;
    }
  }
  return categories;
}

// <user, query>
typedef std::function<void(const std::string &, const std::string &)> TOnSearchQueryLambda;

class SearchFilter {
  TOnSearchQueryLambda lambda_;
  std::string prev_query_;
  std::string prev_user_;

public:
  SearchFilter(TOnSearchQueryLambda lambda) : lambda_(lambda) {}

  void ProcessQuery(const std::string & user, std::string query) {
    CaseFoldingAndNormalize(query);
    if (prev_query_.empty()) {
      prev_user_ = user;
      prev_query_ = query;
      return;
    }
    if (prev_user_ != user) {
      lambda_(prev_user_, prev_query_);
      prev_user_ = user;
      prev_query_ = query;
      return;
    }
    if (query.find(prev_query_) == 0) {
      prev_user_ = user;
      prev_query_ = query;
      return;
    }
    if (prev_query_.find(query) == string::npos) {
      lambda_(prev_user_, prev_query_);
      prev_user_ = user;
      prev_query_ = query;
      return;
    }
  }
};

int main(int argc, char ** argv) {
  if (argc < 2) {
    cout << "Usage: " << argv[0] << " <categories.txt file to analyze>" << endl;
    cout << "       Please note, you can leave only needed categories in the file." << endl;
    return -1;
  }
  const TCategories categories = LoadCategoriesFromFile(argv[1]);
  map<string, set<string>> users_queries_;
  SearchFilter filter([&users_queries_](const string & user, const string & query) {
    users_queries_[user].insert(query);
  });
  Processor([&](const AlohalyticsIdServerEvent * se, const AlohalyticsBaseEvent * e) {
    const AlohalyticsKeyPairsEvent * kpe = dynamic_cast<const AlohalyticsKeyPairsEvent *>(e);
    if (kpe && kpe->key == "searchEmitResults") {
      filter.ProcessQuery(se->id, kpe->pairs.begin()->first);
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

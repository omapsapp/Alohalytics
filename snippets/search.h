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

// Helpers to work with search queries.

#include "../3party/utf8proc/utf8proc.h"

#include <fstream>
#include <map>
#include <set>
#include <string>

typedef std::map<std::string, std::set<std::string>> TCategories;

void CaseFoldingAndNormalize(std::string & s) {
  utf8proc_uint8_t * buf = nullptr;
  const utf8proc_ssize_t ssize =
      utf8proc_map(reinterpret_cast<const utf8proc_uint8_t *>(s.data()), s.size(), &buf,
                   static_cast<utf8proc_option_t>(UTF8PROC_COMPAT | UTF8PROC_DECOMPOSE | UTF8PROC_CASEFOLD));
  if (ssize > 0) {
    s.assign(reinterpret_cast<const std::string::value_type *>(buf), ssize);
  }
  if (buf) {
    free(buf);
  }
}

inline TCategories LoadCategoriesFromFile(const char * path) {
  enum class State { EParseTypes, EParseLanguages } state = State::EParseTypes;
  TCategories categories;
  std::string line, current_types;
  std::ifstream file(path);
  while (file) {
    std::getline(file, line);
    switch (state) {
      case State::EParseTypes: {
        current_types = line;
        if (!current_types.empty()) {
          state = State::EParseLanguages;
        }
      } break;
      case State::EParseLanguages: {
        size_t pos = line.find(':');
        if (pos == std::string::npos) {
          state = State::EParseTypes;
          continue;
        }
        while (pos != std::string::npos) {
          size_t end_pos = line.find('|', pos + 1);
          std::string name = line.substr(pos + 1, end_pos == std::string::npos ? end_pos : end_pos - pos - 1);
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

// This filter helps to get real user queries from detailed typing logs.
// For example, for this log for the same user:
// h
// ho
// hot
// hote
// hotel
// hote
// hot
// bar
// ba
// b
// this filter will find 'hotel' and 'bar' queries only.
// It will also correctly takes into an account if next query is from different user.
class SearchFilter {
  TOnSearchQueryLambda lambda_;
  std::string prev_query_;
  std::string prev_user_;
  size_t prev_results_;

 public:
  SearchFilter(TOnSearchQueryLambda lambda) : lambda_(lambda) {}

  void ProcessQuery(const std::string & user, std::string query, size_t results) {
    CaseFoldingAndNormalize(query);
    if (prev_query_.empty()) {
      prev_user_ = user;
      prev_query_ = query;
      prev_results_ = results;
      return;
    }
    if (prev_user_ != user) {
      lambda_(prev_user_, prev_query_, prev_results_);
      prev_user_ = user;
      prev_query_ = query;
      prev_results_ = results;
      return;
    }
    if (query.find(prev_query_) == 0) {
      prev_user_ = user;
      prev_query_ = query;
      prev_results_ = results;
      return;
    }
    if (prev_query_.find(query) == std::string::npos) {
      lambda_(prev_user_, prev_query_, prev_results_);
      prev_user_ = user;
      prev_query_ = query;
      prev_results_ = results;
      return;
    }
  }
};

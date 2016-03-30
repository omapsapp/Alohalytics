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
// TODO(AlexZ): Should use original code from MAPS.ME for consistency.

#include "../3party/utf8proc/utf8proc.h"

#include <algorithm>
#include <fstream>
#include <map>
#include <set>
#include <string>
#include <vector>

// <category name, set of translations>
typedef std::map<std::string, std::set<std::string>> TCategories;

void FoldCaseAndNormalize(std::string & s) {
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

// TODO(AlexZ): Real trimming (tokens delimeters) are much more complex in MAPS.ME. Should use them.
void Trim(std::string & s, const std::string & whitespaces = " \n\t\r") {
  const auto isSeparator =
      [&whitespaces](std::string::value_type c) -> bool { return whitespaces.find_first_of(c) != std::string::npos; };
  const auto left = std::find_if_not(s.begin(), s.end(), isSeparator);
  const auto right = std::find_if_not(s.rbegin(), s.rend(), isSeparator).base();
  if (right <= left) {
    s.clear();
  } else {
    s = std::string(left, right);
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
          FoldCaseAndNormalize(name);
          Trim(name);
          categories[current_types].insert(name);
        }
      } break;
    }
  }
  return categories;
}

// Returns the name of matched category or empty string if query does not match any category.
std::string GetQueryCategory(const std::string & query, const TCategories & categories, bool include_synonyms = false) {
  std::string merged;
  for (const auto & category : categories) {
    for (const auto & translation : category.second) {
      if (translation == query) {
        if (include_synonyms) {
          if (!merged.empty()) {
            merged += " ";
          }
          merged += category.first;
        } else {
          return category.first;
        }
      }
    }
  }
  return std::string();
}

// Returns true if and only if |a| starts with |b|.
inline bool StartsWith(const std::string & a, const std::string & b) {
  return a.size() >= b.size() && a.compare(0, b.size(), b) == 0;
}

// <user, query, results count>
typedef std::function<void(const std::string &, const std::string &, size_t)> TOnSearchQueryLambda;

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
    FoldCaseAndNormalize(query);
    Trim(query);
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
    if (StartsWith(query, prev_query_)) {
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

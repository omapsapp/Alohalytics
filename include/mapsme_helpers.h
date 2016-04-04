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

#include <string>

namespace mapsme_helpers {
// Returns true if given package id is for production releases.
inline bool IsProductionPackageId(const std::string & package_or_bundle_id) {
  return package_or_bundle_id == "com.mapswithme.maps.pro" || package_or_bundle_id == "com.mapswithme.full";
}

// Removes .mwm suffix from downloaded countries values. It was added by mistake in the code
// after refactoring downloader.
inline std::string NormalizeDownloadedCountry(const std::string & name) {
  const auto s = name.size();
  if (s < 4) {
    return name;
  }
  std::string n(name);
  if (n[s - 4] == '.' && n[s - 3] == 'm' && n[s - 2] == 'w' && n[s - 1] == 'm') {
    n.resize(s - 4);
  }
  return n;
}
} // namespace mapsme_helpers

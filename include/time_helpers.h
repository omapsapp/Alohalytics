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

#include <stdexcept>
#include <string>
#include <time.h>  // strptime is POSIX-only.

namespace time_helpers {
// Returns timestamp in ms from unix epoch.
// @param date is "YEAR-MM-DD".
inline uint64_t TimestampFromDate(const std::string & date) {
  struct std::tm tms;
  memset(&tms, 0, sizeof(tms));
  if (nullptr == ::strptime(date.c_str(), "%Y-%m-%d", &tms)) {
    throw std::invalid_argument(date);
  }
  const time_t timet = std::mktime(&tms);
  // mktime uses local time, not GMT one. Fix it.
  struct std::tm local = *std::localtime(&timet);
  // TODO(AlexZ): tm_gmtoff is not too portable.
  return (timet + local.tm_gmtoff) * 1000;
}
} // namespace time_helpers

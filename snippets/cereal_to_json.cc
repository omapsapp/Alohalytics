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

// Converts binary cereal events from stdin to json cereal events and writes them into stdout.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include "../Alohalytics/src/cereal/include/archives/json.hpp"

#include <iostream>
#include <memory>

using cereal::BinaryInputArchive;
using cereal::JSONOutputArchive;

int main(int, char **) {
  BinaryInputArchive ar(std::cin);
  JSONOutputArchive out(std::cout, JSONOutputArchive::Options::NoIndent());
  while (true) {
    std::unique_ptr<AlohalyticsBaseEvent> ptr;
    try {
      ar(ptr);
      out(ptr);
    } catch (const cereal::Exception & ex) {
      std::cerr << "Cereal exception" << std::endl;
      break;
    }
  }
  return 0;
}

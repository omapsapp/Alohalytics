/*******************************************************************************
 The MIT License (MIT)

 Copyright (c) 2016 Lev Dragunov <l.dragunov@corp.mail.ru> from Moscow, Russia

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

// Calculates statistics about all routing sessions and prints to stdout
// route completeness histogramm.

// This define is needed to preserve client's timestamps in events.
#define ALOHALYTICS_SERVER
#include "../Alohalytics/src/event_base.h"

#include <algorithm>
#include <chrono>
#include <ctime>
#include <iostream>
#include <map>
#include <string>
#include <vector>

using namespace std;

enum HistType { HPEDESTRIAN = 0, SHORT = 1, MID = 2, LONG = 3 };

enum EventType { CALCULATE_ROUTE = 0, CLOSE_ROUTE = 2, ROUTE_FINISHED = 3, REBUILD_ROUTE = 1 };

enum RouterType { VEHICLE, PEDESTRIAN, NOT_SET };

int constexpr kNotSet = -1;

struct RoutingData {
  RoutingData() { hist.fill(0); }

  void PrintData() {
    size_t agg = 0;
    cerr << "Rebuilds per meter:"
         << accumulate(weightedRebuild.begin(), weightedRebuild.end(), 0.0) / weightedRebuild.size() << endl;
    cerr << "Km per rebuild:"
         << weightedRebuild.size() / (1000. * accumulate(weightedRebuild.begin(), weightedRebuild.end(), 0.0)) << endl;
    for (auto i = 0; i < 10; ++i) {
      agg += hist[i];
      cerr << i * 10 << "%"
           << " - " << (i + 1) * 10 << "% = " << hist[i] << "  " << agg << endl;
    }
  }

  array<size_t, 10> hist;
  vector<double> weightedRebuild;
};

using DataStorage = array<RoutingData, 4>;

struct Event {
  EventType type;
  RouterType router;
  double percentage;
  double length;
  int rebuildCount;
  uint64_t timestamp;

  Event(EventType eType,
        uint64_t tmstp,
        RouterType rType = RouterType::NOT_SET,
        double percentage = kNotSet,
        double length = kNotSet,
        int rebuildCount = kNotSet)
      : type(eType),
        router(rType),
        percentage(percentage),
        length(length),
        rebuildCount(rebuildCount),
        timestamp(tmstp) {}

  void UpdateFromLast(Event const & rhs) {
    if (router == RouterType::NOT_SET) router = rhs.router;
    if (percentage == kNotSet) percentage = rhs.percentage;
    if (length == kNotSet) length = rhs.length;
    if (rebuildCount == kNotSet) rebuildCount = rhs.rebuildCount;
  }

  bool operator<(Event const & rhs) const { return timestamp < rhs.timestamp; }
};

class RoutingClient {
 public:
  void AddEvent(Event && event) { m_storage.emplace_back(event); }

  void Process(DataStorage & data, size_t & errors) {
    if (m_storage.size() < 2) return;
    sort(m_storage.begin(), m_storage.end());

    for (size_t i = 1; i < m_storage.size(); ++i) {
      m_storage[i].UpdateFromLast(m_storage[i - 1]);
    }

    for (auto const & event : m_storage) {
      // ROUTE_FINISHED duplicates by ROUTE_CLOSING (closing after) so we do not collect this event.
      if (event.type == EventType::CLOSE_ROUTE) {
        size_t percentage = 0;
        HistType hist_type;

        for (int i = 10; i >= 0; --i) {
          if (event.percentage > i * 10) {
            percentage = i;
            break;
          }
        }

        if (event.router == RouterType::PEDESTRIAN) {
          hist_type = HistType::HPEDESTRIAN;
        } else {
          if (event.length < 10000)
            hist_type = HistType::SHORT;
          else if (event.length < 100000)
            hist_type = HistType::MID;
          else
            hist_type = HistType::LONG;
        }
        if (event.length <= 25 || event.rebuildCount == kNotSet) {
          errors++;
          continue;
        }
        data[hist_type].hist[percentage]++;
        data[hist_type].weightedRebuild.emplace_back(event.rebuildCount / event.length);
      }
    }
  }

 private:
  vector<Event> m_storage;
};

double GetPercentage(AlohalyticsKeyPairsEvent const * event) {
  auto const found = event->pairs.find("percent");
  if (found != event->pairs.end()) return std::stod(found->second);
  return kNotSet;
}

int GetRebuildCount(AlohalyticsKeyPairsEvent const * event) {
  auto const found = event->pairs.find("rebuildCount");
  if (found != event->pairs.end()) return std::stoi(found->second);
  return kNotSet;
}

double GetPassedDistance(AlohalyticsKeyPairsEvent const * event) {
  auto const found = event->pairs.find("passedDistance");
  if (found != event->pairs.end()) return std::stod(found->second);
  return kNotSet;
}

double GetDistance(AlohalyticsKeyPairsEvent const * event) {
  auto const found = event->pairs.find("distance");
  if (found != event->pairs.end()) return std::stod(found->second);
  return kNotSet;
}

RouterType GetRouterType(AlohalyticsKeyPairsEvent const * event) {
  auto const found = event->pairs.find("router");
  if (found == event->pairs.end()) return RouterType::NOT_SET;
  if ("vehicle" == found->second) return RouterType::VEHICLE;
  return RouterType::PEDESTRIAN;
}

RouterType GetRouterTypeByName(AlohalyticsKeyPairsEvent const * event) {
  auto const found = event->pairs.find("name");
  if (found == event->pairs.end()) return RouterType::NOT_SET;
  if ("vehicle" == found->second) return RouterType::VEHICLE;
  return RouterType::PEDESTRIAN;
}

int main() {
  map<string, RoutingClient> clients;

  const string kRoutingClosedEvent = "RouteTracking_RouteClosing";
  const string kRoutingFinishedEvent = "RouteTracking_ReachedDestination";
  const string kRoutingCalculatingEvent = "Routing_CalculatingRoute";
  const string kRoutingRebuildEvent = "RouteTracking_RouteNeedRebuild";

  DataStorage data;
  size_t errors = 0;

  string current_user_id;
  cereal::BinaryInputArchive ar(std::cin);
  unique_ptr<AlohalyticsBaseEvent> ptr;
  auto const start_time = chrono::system_clock::now();
  while (true) {
    try {
      ar(ptr);
    } catch (const cereal::Exception & ex) {
      if (string("Failed to read 4 bytes from input stream! Read 0") != ex.what()) {
        // The exception above is a normal one, Cereal lacks to detect the end of the stream.
        cout << ex.what() << endl;
      }
      break;
    }
    // Every sequence of events from one user starts with a special 'id' event.
    AlohalyticsIdServerEvent const * id_event = dynamic_cast<AlohalyticsIdServerEvent const *>(ptr.get());
    if (id_event) {
      current_user_id = id_event->id;
    } else {
      const AlohalyticsKeyPairsEvent * key_event = dynamic_cast<const AlohalyticsKeyPairsEvent *>(ptr.get());
      if (!key_event) continue;
      if (key_event->key == kRoutingClosedEvent) {
        RoutingClient & client = clients[current_user_id];
        client.AddEvent(
            Event(EventType::CLOSE_ROUTE, key_event->timestamp, RouterType::NOT_SET, GetPercentage(key_event)));
      } else if (key_event->key == kRoutingRebuildEvent) {
        int rebuildCount = GetRebuildCount(key_event);
        // Fix of the wrong rebuilding count. Because in omim rebuild event called before counter increment.
        if (rebuildCount != -1) rebuildCount++;
        RoutingClient & client = clients[current_user_id];
        client.AddEvent(Event(
            EventType::REBUILD_ROUTE, key_event->timestamp, GetRouterType(key_event), kNotSet, kNotSet, rebuildCount));
      } else if (key_event->key == kRoutingFinishedEvent) {
        RoutingClient & client = clients[current_user_id];
        client.AddEvent(Event(EventType::ROUTE_FINISHED,
                              key_event->timestamp,
                              GetRouterType(key_event),
                              100.,
                              GetPassedDistance(key_event),
                              GetRebuildCount(key_event)));
      } else if (key_event->key == kRoutingCalculatingEvent) {
        RoutingClient & client = clients[current_user_id];
        client.AddEvent(Event(
            EventType::CALCULATE_ROUTE,
            key_event->timestamp,
            GetRouterTypeByName(key_event),
            kNotSet,
            GetDistance(key_event)));  // Do not use rebuildCount at 0 because this event is called on rebuild too.
      }
    }
  }

  cerr << "Data extraction done. Processing..." << endl;

  for (auto & client : clients) client.second.Process(data, errors);

  cerr << "Pedestrian stats" << endl;
  data[0].PrintData();
  cerr << "short stats" << endl;
  data[1].PrintData();
  cerr << "middle stats" << endl;
  data[2].PrintData();
  cerr << "long stats" << endl;
  data[3].PrintData();

  cerr << "Ignored events: " << errors << endl;
  cerr << "Total processing time: "
       << std::chrono::duration_cast<std::chrono::seconds>(chrono::system_clock::now() - start_time).count()
       << " seconds." << endl;

  return 0;
}

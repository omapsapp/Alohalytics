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
#include <array>
#include <chrono>
#include <ctime>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <vector>

using namespace std;

enum HistType { HPEDESTRIAN = 0, SHORT = 1, MID = 2, LONG = 3 };

enum EventType { CALCULATE_ROUTE = 0, REBUILD_ROUTE = 1, CLOSE_ROUTE = 2, ROUTE_FINISHED = 3 };

enum RouterType { VEHICLE, PEDESTRIAN, NOT_SET };

int constexpr kNotSet = -1;

struct RoutingData {
  RoutingData() { hist.fill(0); }

  void PrintData() {
    size_t agg = 0;
    const auto weighted_sum = accumulate(weightedRebuild.begin(), weightedRebuild.end(), 0.0);
    cerr << "Rebuilds per meter:"
         << weighted_sum / weightedRebuild.size() << endl;
    cerr << "Km per rebuild:"
         << weightedRebuild.size() / (1000. * weighted_sum) << endl;
    for (auto i = 0; i < 10; ++i) {
      agg += hist[i];
      cerr << i * 10 << " - " << (i + 1) * 10 << "% = " << hist[i] << "  " << agg << endl;
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
  int rebuild_count;
  uint64_t timestamp;

  Event(EventType eType,
        uint64_t tmstp,
        RouterType rType = RouterType::NOT_SET,
        double percentage = kNotSet,
        double length = kNotSet,
        int rebuild_count = kNotSet)
      : type(eType),
        router(rType),
        percentage(percentage),
        length(length),
        rebuild_count(rebuild_count),
        timestamp(tmstp) {}

  void UpdateFromLast(Event const & rhs) {
    if (router == RouterType::NOT_SET) router = rhs.router;
    if (percentage == kNotSet) percentage = rhs.percentage;
    if (length == kNotSet) length = rhs.length;
    if (rebuild_count == kNotSet) rebuild_count = rhs.rebuild_count;
  }

  bool operator<(Event const & rhs) const { return timestamp < rhs.timestamp; }
};

class RoutingClient {
 public:
  void AddEvent(Event && event) { m_events.emplace_back(move(event)); }

  void Process(DataStorage & data, size_t & errors) {
    if (m_events.size() < 2) return;
    sort(m_events.begin(), m_events.end());

    for (size_t i = 1; i < m_events.size(); ++i) {
      m_events[i].UpdateFromLast(m_events[i - 1]);
    }

    for (const auto & event : m_events) {
      // ROUTE_FINISHED duplicates by ROUTE_CLOSING (closing after) so we do not collect this event.
      if (event.type == EventType::CLOSE_ROUTE) {
        size_t percentage = 0;
        HistType hist_type;

        for (int i = 9; i >= 0; --i) {
          if (event.percentage >= i * 10) {
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
        if (event.length <= 25) {
          errors++;
          continue;
        }
        data[hist_type].hist[percentage]++;
        if (event.rebuild_count != kNotSet)
          data[hist_type].weightedRebuild.emplace_back(event.rebuild_count / event.length);
      }
    }
  }

 private:
  vector<Event> m_events;
};

double GetPercentage(AlohalyticsKeyPairsEvent const * event) {
  const auto found = event->pairs.find("percent");
  if (found != event->pairs.end()) return std::stod(found->second);
  return kNotSet;
}

int GetRebuildCount(AlohalyticsKeyPairsEvent const * event) {
  const auto found = event->pairs.find("rebuildCount");
  if (found != event->pairs.end()) return std::stoi(found->second);
  return kNotSet;
}

double GetPassedDistance(AlohalyticsKeyPairsEvent const * event) {
  const auto found = event->pairs.find("passedDistance");
  if (found != event->pairs.end()) return std::stod(found->second);
  return kNotSet;
}

double GetDistance(AlohalyticsKeyPairsEvent const * event) {
  const auto found = event->pairs.find("distance");
  if (found != event->pairs.end()) return std::stod(found->second);
  return kNotSet;
}

RouterType GetRouterType(AlohalyticsKeyPairsEvent const * event) {
  const auto found = event->pairs.find("router");
  if (found == event->pairs.end()) return RouterType::NOT_SET;
  if ("vehicle" == found->second) return RouterType::VEHICLE;
  return RouterType::PEDESTRIAN;
}

RouterType GetRouterTypeByName(AlohalyticsKeyPairsEvent const * event) {
  const auto found = event->pairs.find("name");
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
  const auto start_time = chrono::system_clock::now();
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
        int rebuild_count = GetRebuildCount(key_event);
        // Fix of the wrong rebuilding count. Because in omim rebuild event called before counter increment.
        if (rebuild_count != -1) rebuild_count++;
        RoutingClient & client = clients[current_user_id];
        client.AddEvent(Event(
            EventType::REBUILD_ROUTE, key_event->timestamp, GetRouterType(key_event), kNotSet, kNotSet, rebuild_count));
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
            GetDistance(key_event)));  // Do not set rebuild_count to 0 because this event is called on rebuild too.
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

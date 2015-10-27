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

// Routing statistics.
// RouteTracking_ReachedDestination (passedDistance, router)
// Routing_CalculatingRoute (name)

#include "../include/processor_light.h"

#include <iostream>
#include <map>

using namespace std;

struct Counters {
  size_t calculate_vehicle = 0;
  size_t calculate_pedestrian = 0;
  size_t reached_destinations_vehicle = 0;
  size_t reached_destinations_pedestrian = 0;
  double passed_vehicle = 0;
  double passed_pedestrian = 0;
};

int main(int, char **) {
  map<string, Counters> users;
  alohalytics::ProcessorLight([&](const AlohalyticsIdServerEvent * se, const AlohalyticsKeyEvent * e) {
    if (e->key == "Routing_CalculatingRoute") {
      auto kp = static_cast<const AlohalyticsKeyPairsEvent *>(e);
      auto found = kp->pairs.find("name");
      if (found != kp->pairs.end()) {
        if (found->second == "vehicle") {
          ++users[se->id].calculate_vehicle;
        } else {
          ++users[se->id].calculate_pedestrian;
        }
      }
    } else if (e->key == "RouteTracking_ReachedDestination") {
      auto kp = static_cast<const AlohalyticsKeyPairsEvent *>(e);
      const auto found = kp->pairs.find("router");
      const auto passed = kp->pairs.find("passedDistance");
      if (found != kp->pairs.end()) {
        if (found->second == "vehicle") {
          ++users[se->id].reached_destinations_vehicle;
          if (passed != kp->pairs.end()) {
            users[se->id].passed_vehicle += stod(passed->second);
          }
        } else {
          ++users[se->id].reached_destinations_pedestrian;
          if (passed != kp->pairs.end()) {
            users[se->id].passed_pedestrian += stod(passed->second);
          }
        }
      }
    }

  });

  cout << "Total users who tried to navigate: " << users.size() << endl;
  size_t calculate_vehicle_users = 0, calculate_pedestrian_users = 0;
  size_t vehicle_calc_sum = 0, pedestrian_calc_sum = 0;
  size_t reached_destinations_vehicle_users = 0, reached_destinations_pedestrian_users = 0;
  size_t vehicle_reached_sum = 0, pedestrian_reached_sum = 0;
  size_t passed_vehicle_total = 0, passed_pedestrian_total = 0;
  for (const auto & user : users) {
    if (user.second.calculate_vehicle) {
      ++calculate_vehicle_users;
      vehicle_calc_sum += user.second.calculate_vehicle;
    }
    if (user.second.calculate_pedestrian) {
      ++calculate_pedestrian_users;
      pedestrian_calc_sum += user.second.calculate_pedestrian;
    }
    if (user.second.reached_destinations_vehicle) {
      ++reached_destinations_vehicle_users;
      vehicle_reached_sum += user.second.reached_destinations_vehicle;
    }
    if (user.second.reached_destinations_pedestrian) {
      ++reached_destinations_pedestrian_users;
      pedestrian_reached_sum += user.second.reached_destinations_pedestrian;
    }
    passed_vehicle_total += user.second.passed_vehicle;
    passed_pedestrian_total += user.second.passed_pedestrian;
  }
  cout << "Car routing was calculated by " << calculate_vehicle_users << " users " << vehicle_calc_sum << " times." << endl;
  cout << "Pedestrian routing was calculated by " << calculate_pedestrian_users << " users " << vehicle_calc_sum << " times." << endl;
  cout << reached_destinations_vehicle_users << " users reached car destination " << vehicle_reached_sum << " times." << endl;
  cout << reached_destinations_pedestrian_users << " users reached pedestrian destination " << pedestrian_reached_sum << " times." << endl;
  cout << "Total passed car distance: " << passed_vehicle_total << endl;
  cout << "Total passed pedestrian distance: " << passed_pedestrian_total << endl;

  return 0;
}


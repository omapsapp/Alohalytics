// This file lists the events that we are logging with Alohalytics in MAPS.ME (http://github.com/mapsme/omim).

#pragma once

// AlohalyticsIdServerEvent contains the id of the user that started the search.
// AlohalyticsKeyPairsEvent has the pair <search query, number of found results as a string> as value.
#define SEARCH_EMIT_RESULTS "searchEmitResults"

// AlohalyticsIdServerEvent contains the id of the user that started the search.
// AlohalyticsKeyPairsEvent has as its value (query, its results, user's viewport and position)
// packed into a map.
#define SEARCH_EMIT_RESULTS_AND_COORDS "searchEmitResultsAndCoords"

#define COUNTRY_DOWNLOAD_FINISHED "$OnMapDownloadFinished"

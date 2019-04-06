# tourbuddy
Checkpoint 2

For checkpoint 2 we currently have a working version of our A* model that, given a location, returns a viable tour route between locations.
Right now we have a downloaded json file of the data returned by the Google Maps api (turin.json) that we are using to test in order to limit the amount of API calls we are doing during testing.

The model itself is structured as follows:
-
* The Tour class initializes the data and sets off the tour planning
  * Initialize loads the set of locations given either by a keyword for google or a json file
  * Filter destinations picks only the most relevant landmarks based on reviews so the size of the graph isn't too large
  * Dump Places gets the data from the json file
  * Get Places gets the data from the Google API
  * Geo_locality get the general area from the API
  * Plan sets off the tour planning process
* The Tour Planner class keeps track of the starting/ending location and runs the actual search algorithm
  * Search is the A* search algorithm used to construct the tour
* The Tour State class represents each of the states in the graph including current stops and path up to this point
  * Score gets the heuristic value for the state
  * Next States is the successor function
  * Is Plausible calculates whether the location can be reached in the remaining time. If not it gives the state a high cost
* The Stop class represents specific locations (landmarks) 

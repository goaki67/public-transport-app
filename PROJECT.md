## The project will get its data from this main sources:
1. static GTFS feed from the ministry of transportation
2. GTFS real time alerts from the MOT via a service who's URL is not publicly disclosed
3. the open bus stride api 

## Static data
The GTFS data is available from the FTP address ftp://gtfs.mot.gov.il/ or ftp://199.203.58.18/ or https://gtfs.mot.gov.il/gtfsfiles/ under the name israel-public-transportation.zip, the file is updated nightly.
More information about the GTFS format and the data given in this file is available at:
1. [MoT document](https://www.gov.il/BlobFolder/generalpage/gtfs_general_transit_feed_specifications/he/GTFS%20-%20Developer%20Information.pdf)
2. [Google's developer portal](https://developers.google.com/transit/gtfs/reference)
We'll store the data in a relational database with spatial extension like PostGIS. We use this kind of database because of the inherently relational nature of the data (e.g. a route has many trips which have many stops, etc.). The spatial extension is used for fast geographic searching.

## Real Time Data
For real time data we'll use the `https://open-bus-stride-api.hasadna.org.il/` API, which docs can be found at [docs](https://open-bus-stride-api.hasadna.org.il/docs).
The API has the following key sections:

### 1. `/siri_vehicle_locations/list`
Provides the raw, high-frequency physical parameters of every active bus on the road. This feed drives the live map graphics and serves as the baseline data for proximity math.
* **Fields for The Frontend:**
  * `lat` / `lon` *(float)*: The current GPS coordinates of the bus. Used to draw and update vehicle positions.
  * `bearing` *(int)*: Heading direction in degrees (0 to 360). Used to orient the vehicle map marker arrow in the correct direction of travel.
* **Fields for Route Calculations:**
  * `siri_ride_id` *(int)*: The identifier that links the bus to a specific operational journey.
  * `velocity` *(int)*: Instantaneous speed in km/h. Used by the backend to calculate delays, adjust ETA forecasts, and implement dead reckoning extrapolation routines between telemetry packets.
  * `recorded_at_time` *(timestamp)*: The exact moment the vehicle pinged its location. Used for filtering out old points and ensuring calculation freshness.
* **Other:**
  * `get_count=false`: Skips backend aggregation to maximize API processing and transfer speed.
  * `recorded_at_time_from` / `recorded_at_time_to`: Filters for a narrow time window to extract the most recent pings.

### 2. `/siri_rides/list`
Acts as the relational translation layer. It bridges transient live vehicle telemetry directly to our GTFS data.
* **Fields for Route Calculations:**
  * `id` *(int)*: Mapped directly against the vehicle location's `siri_ride_id`.
  * `gtfs_ride_id` *(int/string)*: This corresponds directly to the static `trip_id` inside the GTFS `trips.txt` file. This lets the backend look up the scheduled path, stop sequence order, and target arrival times for the moving bus.
  * `scheduled_start_time` *(timestamp)*: Used to determine if a run left its origin terminal delayed or ahead of schedule, adjusting ETA baselines prior to route progress math.
* **Fields for App Frontend:**
  * `vehicle_ref` *(string)*: The unique fleet number or license plate of the physical bus. Allows the user interface to show granular vehicle details or let users track a highly specific bus block across multiple routes.

### 3. `/siri_routes/list`
Provides technical operational metadata for the route associated with a live ride structure.
* **Fields for App Frontend:**
  * `line_ref` *(int)*: The absolute internal line reference identifier mapped by the MoT.
  * `operator_ref` *(int)*: The ID of the executing transit agency (e.g., Egged = 3, Dan = 5, Kavim = 15).

The data contains a continuous stream of raw variables (current GPS coordinates, direction, and instantaneous speed) broadcasting from active buses every few seconds. TO store this data we will use an in-memory cache because writing the data into disk will be a major bottleneck.

Both data types (the static and real time) have a "Journey id" that can be used to combine the live position with our static data, with this knowledge the backend would be able to calculate if the bust is early, late, or on time.

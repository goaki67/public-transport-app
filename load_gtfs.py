import sqlite3
from collections import defaultdict

db = sqlite3.connect("data/data.db")

GLOBAL_ROUTE_STOPS = {}
GLOBAL_STOP_TIMES = {}
GLOBAL_STOP_ROUTES = defaultdict(list)


def load_global_transit_network():
    print("Loading global transit network into memory...")

    query_timetable = """
    SELECT t.route_id, st.trip_id, st.stop_id, st.arrival_time, st.departure_time, st.stop_sequence
    FROM "stop_times.txt" st
    JOIN "trips.txt" t ON st.trip_id = t.trip_id
    ORDER BY t.route_id, st.trip_id, st.stop_sequence;
    """

    print("Executing timetable batch query...")
    raw_data = db.execute(query_timetable).fetchall()

    # Format: { route_id: { trip_id: [ (stop_id, arrival, departure, seq), ... ] } }
    network_builder = defaultdict(lambda: defaultdict(list))

    for route_id, trip_id, stop_id, arrival, departure, seq in raw_data:
        network_builder[route_id][trip_id].append(
            (stop_id, arrival, departure, seq))

    print("Processing structures and sorting timetables chronologically...")
    for route_id, trips_dict in network_builder.items():
        # To satisfy RAPTOR, we must sort this route's trips by the departure time of their first stop
        # trip_data[0] is the first stop of the trip, index 2 is its departure_time
        sorted_trips = sorted(trips_dict.values(),
                              key=lambda trip_data: trip_data[0][2])

        # Since all trips in a RAPTOR route share the exact same sequence of stops
        # we can just extract the stop IDs from the very first sorted trip
        GLOBAL_ROUTE_STOPS[route_id] = [stop_info[0]
                                        for stop_info in sorted_trips[0]]

        # Store a matrix of (arrival, departure) tuples for every trip on this route
        GLOBAL_STOP_TIMES[route_id] = [
            [(stop_info[1], stop_info[2]) for stop_info in single_trip]
            for single_trip in sorted_trips
        ]

    query_stop_routes = """
    SELECT DISTINCT st.stop_id, t.route_id
    FROM "stop_times.txt" st
    JOIN "trips.txt" t ON st.trip_id = t.trip_id;
    """

    print("Building stop-to-route index...")
    stop_routes_data = db.execute(query_stop_routes).fetchall()
    for stop_id, route_id in stop_routes_data:
        GLOBAL_STOP_ROUTES[stop_id].append(route_id)

    print("Load complete!")


load_global_transit_network()
db.close()

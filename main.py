import sqlite3
from collections import defaultdict

db = sqlite3.connect("data/data.db")

db.execute('CREATE INDEX IF NOT EXISTS idx_stop_times_trip_seq ON "stop_times.txt"(trip_id, stop_sequence);')
db.execute(
    'CREATE INDEX IF NOT EXISTS idx_trips_route_id ON "trips.txt"(route_id);')
db.execute(
    'CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON "stop_times.txt"(stop_id);')
db.execute('CREATE INDEX IF NOT EXISTS idx_trips_trip_id ON "trips.txt"(trip_id);')
db.execute('CREATE INDEX IF NOT EXISTS idx_stops_stop_id ON "stops.txt"(stop_id);')


def get_route_ids():
    query = """SELECT route_id from 'routes.txt'"""
    return [route_id[0] for route_id in db.execute(query).fetchall()]


def get_stop_ids():
    query = """SELECT stop_id from 'stops.txt'"""
    return [stop_id[0] for stop_id in db.execute(query).fetchall()]


def get_stop_id_from_trip_id(trip_id):
    query = """SELECT stop_id FROM "stop_times.txt"
    WHERE trip_id = ?
    ORDER BY stop_sequence;"""
    return db.execute(query, (trip_id,)).fetchall()


def get_all_route_data(route_id):
    query = """
    SELECT st.trip_id, st.arrival_time, st.departure_time
    FROM "stop_times.txt" st
    JOIN "trips.txt" t ON st.trip_id = t.trip_id
    WHERE t.route_id = ?
    ORDER BY t.trip_id, st.stop_sequence;
    """
    results = db.execute(query, (route_id,)).fetchall()

    trips_dict = defaultdict(list)
    for t_id, arrival, departure in results:
        trips_dict[t_id].append((arrival, departure))

    return list(trips_dict.keys()), list(trips_dict.values())


def get_routes_serving_stop(stop_id):
    query = """
    SELECT DISTINCT t.route_id 
    FROM "trips.txt" t
    JOIN "stop_times.txt" st ON t.trip_id = st.trip_id
    WHERE st.stop_id = ?;
    """
    return db.execute(query, (stop_id,)).fetchall()


GLOBAL_ROUTE_STOPS = {}
for route_id in get_route_ids():
    stopids = get_stop_id_from_trip_id(trip_id)
    GLOBAL_ROUTE_STOPS[route_id] = [stop[0] for stop in stopids]

GLOBAL_STOP_TIMES = {}
for route_id in get_route_ids():
    GLOBAL_STOP_TIMES[route_id] = get_all_route_data(route_id)[1]

GLOBAL_STOP_ROUTES = {}
for stop_id in get_stop_ids():
    routes_serving_stop_fetch = get_routes_serving_stop(target_stop_id)
    GLOBAL_STOP_ROUTES[stop_id] = [route[0]
                                   for route in routes_serving_stop_fetch]

db.close()

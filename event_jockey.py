from closest_search import ClosestSearch
from clustering import Cluster
from flask import Flask
import json
import closest_search

app = Flask(__name__)
cluster = Cluster()
cs = ClosestSearch()

@app.route("/event/<latitude>/<longitude>/<budget>/<category>")
def fetch_all_events(latitude, longitude, budget, category):
  cluster.store_details(latitude, longitude, budget)
  events = cluster.get_filtered_events(category)
  return json.dumps(events)

@app.route("/res_event/<cuisine>")
def fetch_res_based_on_event(cuisine):
  result = cluster.fetch_event_res_result(cuisine)
  return json.dumps(result)

@app.route("/rest/<latitude>/<longitude>/<budget>/<cuisine>")
def fetch_all_restaurants(latitude,longitude,budget,cuisine):
  cluster.store_details(latitude, longitude, budget)
  restaurants = cluster.get_filtered_restaurants(cuisine)
  result = cluster.fetch_res_result(restaurants)
  return json.dumps(restaurants)

if __name__ == "__main__":
  app.run()

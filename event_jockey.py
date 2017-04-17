from closest_search import ClosestSearch
from clustering import Cluster
from flask import Flask
import json
import closest_search

app = Flask(__name__)
cluster = Cluster()
cs = ClosestSearch()

@app.route("/event/<latitude>/<longitude>/<budget>")
def fetch_all_events(latitude, longitude, budget):
  cluster.store_details(latitude, longitude, budget)
  events = cs.get_nearby_events((latitude, longitude), 2.50)
  return json.dumps(events)

@app.route("/filt_event/<category>")
def fetch_filtered_events(category):
  events = cluster.get_filtered_events(category)
  return json.dumps(events)
'''
@app.route("/rest/<latitude>/<longitude>")
def fetch_restaurants(latitude,longitude):
  restaurants = cs.get_nearby_restaurants((latitude, longitude), 2.50)
  return json.dumps(restaurants)
'''
@app.route("/rest/<latitude>/<longitude>/<budget>")
def fetch_restaurants(latitude, longitude, budget):
  restaurants = cluster.main(latitude, longitude, budget)
  return json.dumps(restaurants)

if __name__ == "__main__":
  app.run()

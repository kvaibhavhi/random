from closest_search import ClosestSearch
from collections import OrderedDict
import mysql.connector
import json

DATABASE = 'events_jockey'

class Cluster(object):
  def __init__(self):
    self._user_location = (0,0)
    self._user_day_budget = 0
    self.cs = ClosestSearch()

  def store_details(self,latitude, longitude, day_budget):
    self._user_location = (latitude, longitude)
    self._user_day_budget = day_budget

  def get_user_budget(self):
    return float(self._user_day_budget)

  def fetch_events(self):
    events = self.cs.get_nearby_events(self._user_location, 2.50)
    return events

  def res_near_event(self, event):
    mid_lat,mid_lon = event['coord']
    restaurants = self.cs.get_nearby_restaurants((mid_lat,mid_lon), 2.50)
    return restaurants

  def get_top_three(self, restaurants):
    sorted_res = OrderedDict(sorted(restaurants.items(), key= lambda x :(-int(x[1]['score'])))[:3] )
    return sorted_res

  def get_res_id(self, restaurants):
    res_id = []
    for res in restaurants.values():
      res_id.append(res['id'])
    return res_id

  def get_ev_id(self, events):
    ev_id = []
    for ev in events.values():
      ev_id.append(ev['id'])
    return ev_id

  def compute_score(self, restaurant, ev_coord, budget):
    price = restaurant['cost']
    rating = restaurant['rating']
    lat,lon = restaurant['coord']
    name = restaurant['name']
    norm_score = 0
    distance = self.cs.dis(ev_coord, (lat,lon))
    if distance<1:
      norm_score = int( rating * (budget/float(price)))
      if rating >= 4:
        norm_score = norm_score * 2
    else:
      norm_score = int( 1/float(distance) * rating * (budget/float(price)))
    return norm_score

  def get_filtered_res(self, cuisine, restaurants, res_id):
    cnx = mysql.connector.connect(user='root',
                              password= '2411',
                              host='127.0.0.1',
                              database = DATABASE)
    cur = cnx.cursor()
    rest_id = []
    query = "select res_id from hotels where cuisines like '%"+ cuisine +"%' and res_id in ( '" + str(res_id[0]) + "'"
    for i in res_id:
      query += ",'"+ str(i) + "'"
    query += ");"
    cur.execute(query)
    rows = cur.fetchall()
    for i in rows:
      rest_id.append(i[0])
    for id in restaurants.keys():
      if int(id) not in rest_id:
        del restaurants[id]
    cnx.close()
    return restaurants

  def get_filtered_events(self,category):
    events = self.fetch_events()
    ev_id = self.get_ev_id(events)
    cnx = mysql.connector.connect(user='root',
                              password= '2411',
                              host='127.0.0.1',
                              database = DATABASE)
    cur = cnx.cursor()
    evt_id = []
    query = "select e_id from events where cats like '%"+ category +"%' and e_id in ( '" + str(ev_id[0]) + "'"
    for i in ev_id:
      query += ",'"+ str(i) + "'"
    query += ");"
    cur.execute(query)
    rows = cur.fetchall()
    for i in rows:
      evt_id.append(i[0])
    for id in events.keys():
      if id not in evt_id:
        del events[id]
    cnx.close()
    return events

  def main(self,latitude,longitude,budget):
    cluster = Cluster()
    cluster.store_details(latitude,longitude, budget)
    events = cluster.fetch_events()
    i = 1
    return_data = {}
    for event in events.values():
      event_cost = float(event['cost'])
      res_budget = cluster.get_user_budget()-event_cost

      restaurants = cluster.res_near_event(event)
      res_id = cluster.get_res_id(restaurants)
      filtered_res = cluster.get_filtered_res('Continental', restaurants, res_id)
      for restaurant in filtered_res.values():
         score = cluster.compute_score(restaurant, (12.9361480,77.6099350), res_budget)
         restaurant['score'] = score
      top_three = cluster.get_top_three(restaurants)
      for scored in top_three.values():
        event_res_map = {}
        event_res_map['event'] = event
        event_res_map['restaurant'] = scored
        return_data[str(i)] = event_res_map
        i += 1
    return return_data

if __name__ == "__main__":
  main()

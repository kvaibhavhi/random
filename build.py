import rtree.index
import mysql.connector
from subprocess import Popen, PIPE

DATABASE = 'events_jockey'
RES_INDEX = 'restaurant'
EV_INDEX = 'event'

'''Class to build the R-Tree'''
class Build():
  def __init__(self):
    self._cnx = mysql.connector.connect(user='root', password= '2411',
                              host='127.0.0.1',
                              database = DATABASE)
    self._cur = self._cnx.cursor()
    self._res_idx = rtree.index.Rtree(RES_INDEX)
    self._ev_idx = rtree.index.Rtree(EV_INDEX)

  def _get_from_db(self, table):
    query = 'select * from %s;'%(table, )
    self._cur.execute(query)
    rows = self._cur.fetchall()
    return rows

  def get_restaurant_locations(self):
    ''' Reads values from db
    Returns : A dictionary locations{'id':location} with location entry.
              location{'id':_, 'coord':(lat,long), 'name':_}
    '''
    locations = {}
    restaurants = self._get_from_db('hotels')
    for restaurant in restaurants:
      location = {}
      id = restaurant[0]
      latitude = restaurant[7]
      longitude = restaurant[8]

      location['id'] = id
      location['coord'] = (latitude,longitude)
      location['url'] = restaurant[2]
      location['address'] = restaurant[3]
      location['cuisine'] = restaurant[9]
      location['name'] = restaurant[1]
      location['rating'] = restaurant[12]
      location['cost'] = restaurant[10]
      location['locality'] = restaurant[4]
      locations[str(id)] = location
    return locations

  def get_event_locations(self):
    locations = {}
    events = self._get_from_db('events')
    for event in events:
      location = {}
      id = '0x' + event[0]
      id = int(id, 16)
      latitude = event[12]
      longitude = event[13]

      location['id'] = event[0]
      location['coord'] = (latitude,longitude)
      location['name'] = event[2]
      location['locality'] = event[10]
      location['cost'] = event[14]
      location['category'] = event[9]
      location['image'] = event[4]
      locations[str(id)] = location
    return locations

  def add_to_rtree(self, locations, loc_type):
    ''' Creates R-Tree for the given paramaeters.
    Args:
      locations : list of all locations to be added into the tree
      index-name : Name of the R-Tree
    Returns : An R-Tree with the new values given added into the
              previously built tree.
    '''
    if loc_type == 'res': idx = self._res_idx
    else : idx = self._ev_idx
    for key in locations:
      location = locations[key]
      id = int(key)
      x = float(location['coord'][0])
      y = float(location ['coord'][1])
      idx.add(id, (x,y,x,y), obj = location)
    print 'Added to r tree'

  def is_event_db(self):
    ''' Checks whether event table exists in database.'''
    query = "SELECT * FROM information_schema.tables WHERE table_schema = 'events_jockey' AND table_name = 'events' LIMIT 1;"
    self._cur.execute(query)
    rows = self._cur.fetchall()
    if len(rows) == 0:
      return False
    return True

  def remove_events(self):
    '''Removes old event data from R-Tree and database''' 
    events = self._get_from_db('events')
    for event in events:
      id = '0x' + event[0]
      id = int(id, 16)
      self._ev_idx.delete(id, (float(event[12]), float(event[13]), float(event[12]), float(event[13])))
    print 'Removed from tree'
    query = 'drop table events;'
    self._cur.execute(query)
   
  def add_events(self):
    '''Adds new event data into R-Tree and db'''
    for line in open('/home/kvaibhavhi/College/Project/data_files/events.sql').read().split(';\n'):
      self._cur.execute(line)

if __name__ == "__main__":
  build = Build()
  locations = build.get_restaurant_locations()
  build.add_to_rtree(locations, 'res')

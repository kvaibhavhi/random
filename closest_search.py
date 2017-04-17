import rtree.index
import math

RES_INDEX = 'restaurant'
EV_INDEX = 'event'
coordinate = 0.006375

class ClosestSearch():
  def __init__(self):
    self._res_idx = rtree.index.Rtree(RES_INDEX)
    self._ev_idx = rtree.index.Rtree(EV_INDEX)
    self._initial_location = None

  def get_initial_location(self):
    return self._initial_location

  def get_nearby_restaurants(self, coord, radius):
    ''' Gets all restaurants object from a list of all nearby
        locations found after querying in the given radius
    '''
    x = float(coord[0])
    y = float(coord[1])
    boundary = coordinate * radius
    nearby = list(self._res_idx.intersection((x-boundary, y-boundary, x+boundary, y+boundary), objects=True))
    restaurants = {}
    for i in nearby:
      location = i.object
      restaurants[str(location['id'])] = location
    return restaurants


  def get_nearby_events(self, coord, radius):
    ''' Gets all restaurants object from a list of all nearby
        locations found after querying in the given radius
    '''
    x = float(coord[0])
    y = float(coord[1])
    boundary = coordinate * radius
    nearby = list(self._ev_idx.intersection((x-boundary, y-boundary, x+boundary, y+boundary), objects=True))
    events = {}
    for i in nearby:
      location = i.object
      events[str(location['id'])] = location
    return events

  def dis(self, (lat1, lon1), (lat2, lon2)):
    ''' Gives distance b/w 2 geospatial locations'''
    R = 6371
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    a = math.pow(math.sin(dlat/2),2) + math.cos(lat1) * math.cos(lat2) * math.pow((math.sin(dlon/2)),2)
    c = 2 * math.atan2( math.sqrt(a), math.sqrt(1-a) )
    d = R * c
    return d

  def find_mid_point(self, locations):
    ''' For multiple locations finds the mid-point of all locations
    Args:
      locations: List of geospatial location of multiple users
    Returns: Location of calculated mid_point
    '''
    x=0
    y=0
    z=0
    for user in locations:
      lat, lon = user[0], user[1]
      lat = math.radians(lat)
      lon = math.radians(lon)
      x += math.cos(lat) * math.cos(lon)
      y += math.cos(lat) * math.sin(lon)
      z += math.sin(lat)
    x = float( x/len(locations))
    y = float( y/len(locations))
    z = float( z/len(locations))
    mid_lon = math.atan2(y, x)
    hyp = math.sqrt((x * x + y * y))
    mid_lat = math.atan2(z, hyp)
    return (math.degrees(mid_lat), math.degrees(mid_lon))

  def find_suitable_radius(self, midpoint, locations):
    ''' Finds the radius suitable for all users.
    Args
      midpoint: geospatial location of midpoint calculated
      locations: List of loactions of users.
    Returns: Mean distance of all locations from the mid-point
    '''
    if len(locations) == 1:
      return 2.50
    radius = 0
    lat1, lon1 = midpoint[0], midpoint[1]
    for location in locations:
      lat2, lon2 = location[0], location[1]
      radius += self.dis((lat1, lon1), (lat2, lon2))
    return float(radius/len(locations))

  def main(self):
    '''Testing Code'''
    query = ClosestSearch()
    print 'Checking for multiple users'
    coord1 = (12.9260347305 , 77.5504266098)
    coord2 = (12.9700138212, 77.6410577819)
    locations = [coord1, coord2]
    mid_lat,mid_lon = query.find_mid_point(locations)
    self._initial_location = (mid_lat,mid_lon)

    if len(locations) == 1: radius = 2.50
    else:                   radius = query.find_suitable_radius((mid_lat,mid_lon), locations)
    print 'Centre:', mid_lat,mid_lon
    print 'Radius:',radius

    nearby = query.find_nearby_locations((mid_lat,mid_lon), radius)
    restaurants = query.get_restaurants(nearby)
    '''
    for i in range(len(restaurants)):
      print restaurants[i]['id']
      print '%d> %s : %fl'%(i,str(restaurants[i]['name']), query.dis((mid_lat,mid_lon),(restaurants[i]['coord'][0], restaurants[i]['coord'][1])))
    '''
    return restaurants

'''
This module needs to be run on a daily basis
'''
from build import Build

def main():
  rtree = Build()
  if rtree.is_event_db():
    print 'Already present'
    rtree.remove_events()
  rtree.add_events()

  events = rtree.get_event_locations()
  rtree.add_to_rtree(events, 'event')

if __name__ == "__main__":
  main()

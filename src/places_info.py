from unittest.util import strclass
import requests


class PlacesInfo:
  def __init__(self):

    self.api_key = "5ae2e3f221c38a28845f05b63f90b0dc95f3d6cb027a33bde861766b"
    self.base_url = "https://api.opentripmap.com/0.1/en/places/"

  #Returns a list of items(dicts) of atractions near the given place, including both their name and a description
  def get_attractions(self, place_name):

    basic_info = self.send_request("geoname", "name="+place_name)

    lon = str(basic_info["lon"])
    lat = str(basic_info["lat"])

    basic_list = self.load_list(lon, lat)

    final_list = self.load_items(basic_list)

    return final_list

  def load_list(self, lon, lat):
    #radius in meters from the center of the location
    radius = 2000
    #minimum rating of an attraction to appear in the search (1-3)
    rate = 3

    query = "format=json&rate=" + \
        str(rate)+"&radius="+str(radius)+"&lon="+lon+"&lat="+lat

    return self.send_request("radius", query)

  def load_items(self, basic_list):
    #Max number of items to extract
    max_items = 5
    l = []

    for i in basic_list:
      data = self.send_request("xid/"+i["xid"], "")

      item = {"name": data["name"],
              "description": data["wikipedia_extracts"]["text"]}
      l.append(item)
      if len(l) >= max_items:
        break

    return l

  def send_request(self, method, query):
    final_url = self.base_url + method + "?apikey=" + self.api_key + "&" + query

    response = requests.get(final_url)
    if str(response.status_code) == "200":
      return response.json()
    else:
      return None

  def print_attractions(self, city, results):
    if results:
      print(f"Places to visit in the city of {city}:\n")
      for i, attraction in enumerate(results):
          print(f"  {i}  {attraction['name']}: {attraction['description']}\n")
    else:
      print("No attractions found for {city} :(")


if __name__ == "__main__":
  ''' TEST '''
  pi = PlacesInfo()
  print(pi.get_attractions("Aveiro"))

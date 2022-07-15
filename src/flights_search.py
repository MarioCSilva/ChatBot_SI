from unittest.util import strclass
import requests

class FlightsSearch:
  def __init__(self):
    # Get Token
    token_data = {"client_id": "qAVb2tFZ9vl3IBdFFqmY3YtKOeczKGuP", "client_secret": "HGAQcITlD3VJBGfU", "grant_type": "client_credentials"}
    response = requests.post("https://test.api.amadeus.com/v1/security/oauth2/token", token_data)
    self.token = response.json()["access_token"]

    self.routes_url = "https://test.api.amadeus.com/v1/airport/direct-destinations"
    self.offers_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    self.most_visited_url = "https://test.api.amadeus.com/v1/travel/analytics/air-traffic/traveled"
    self.headers = {"Authorization": "Bearer {}".format(self.token)} # Authorization token
    self.dataset = []

    f = open('filtering_data.txt', 'r', encoding="utf-8")
    for line in f:
      l = line.split("_")
      self.dataset.append((l[0], l[1], l[2].replace("\n","")))


  def getCityAirports(self, city):
    city_code = []
    for airport_code, airport_name, city_name in self.dataset:
      if city_name.lower() == city.lower():
        city_code.append((airport_code,airport_name ))

    return city_code

  def getAirportName(self, code):
    name = None
    for airport_code, airport_name, city_name in self.dataset:
      if airport_code == code:
        name = airport_name

    return name

  def search_routes(self, city1, city2):
    airports = [] 
    city2 = city2.upper()
    for airport_code_from,airport_name_from in self.getCityAirports(city1):
      #final_url = self.routes_url + str("?departureAirportCode={0}&max={1}".format(airport_code_from, _max))
      final_url_no_max = self.routes_url + str("?departureAirportCode={0}".format(airport_code_from))

      data = self.send_request(final_url_no_max)  #Send request to final url
      if data:
        for res in data:
          if res["name"] == city2:
            airports.append(airport_name_from)
        
    return airports


  def search_offers(self, departure_city, arrival_city, day):
    final_res = []

    for airport_code_from,airport_name_from in self.getCityAirports(departure_city):
      for airport_code_to,airport_name_to in self.getCityAirports(arrival_city):
        final_url = self.offers_url + str("?originLocationCode={0}&destinationLocationCode={1}&departureDate={2}&adults=1&nonStop=false".format(airport_code_from, airport_code_to, day))
        data = self.send_request(final_url)  #Send request to final url
        if data:
          result_city = []
          for res in data:
            result_city.append({"Departure at": res["itineraries"][0]["segments"][0]["departure"]["at"], "Arrival at": res["itineraries"][0]["segments"][0]["arrival"]["at"], "Price": res["price"]["total"]})

          final_res.append(("From: {} Airport - To: {} Airport".format(airport_name_from, airport_name_to), result_city[:2]))
        #else:
          #print("NO DATA!")

    return final_res

  def print_offers(self,result):
    count = 0
    if result:
      for val1,val2 in result:
        print()
        print(val1+":")
        for _info in val2:
          print("  {}  ".format(count)+str(_info).replace("{", "").replace("}", "").replace("'", "")+"$")
          count+=1
    else:
      print("No results :(")


  def search_most_visited(self, city, period, _max = 5):

    city_code = city.upper()[:3]
    final_url = self.most_visited_url + str("?originCityCode={0}&period={1}&max={2}&sort=analytics.travelers.score".format(city_code, period, _max))
    data = self.send_request(final_url)  #Send request to final url
    if data:
      result = []
      for res in data:
        result.append(res["destination"])
        
      return result
    else:
        print("No results :(")
        return []


  def send_request(self, final_url):
    #print("Final URL: ",final_url)
    response = requests.get(final_url, headers=self.headers)
    if str(response.status_code) == "200":
      return response.json()["data"]
    else:
      return None


if __name__ == "__main__":
  ''' TEST '''
  fs = FlightsSearch()
  result =fs.search_offers("berlin", "paris", "2022-07-02")
  fs.print_offers(result)

  result =fs.search_most_visited("Berlin", "2017-01", 2)
  result = fs.search_routes("Paris", "Porto")
  print(result)
    
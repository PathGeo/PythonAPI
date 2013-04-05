import math
import re   
import os
   
CITIES_FILE = "uscities.txt"
   
   
'''
	CityGeocoder provides a way to geocode city names.
	It uses the GeoNames database.
'''
class CityGeocoder(dict):

	def __init__(self, items = None, file=CITIES_FILE):        
		super(Geocoder, self).__init__()

		self._loadFile(file)


	def _loadFile(self, file):
		COL_CITY = 0
		COL_ALT_NAMES = 1
		COL_LAT = 2
		COL_LON = 3

		cwd = os.path.dirname(__file__)
		path = cwd + '\\' + file 

		f = open(path)
		lines = f.read().split('\n')
						  
		for line in lines:
			cols = line.split('\t')
			names = [cols[COL_CITY]]
			names.extend(cols[COL_ALT_NAMES].split(','))

			for name in names:
				key = name.lower().strip()
				#val = { 'name': cols[COL_CITY], 'coords': (float(cols[COL_LAT]), float(cols[COL_LON])) }
				val = (cols[COL_CITY], (float(cols[COL_LAT]), float(cols[COL_LON]))) 
				self.__setitem__(key, val)           
            

	def lookup(self, location):
		'''
		lookup(location):
			Returns tuple of the city name and the coordinates.
			If the location can't be located, returns ('None', (0.0, 0.0)
		'''

		noplace = (None, (None, None))

		if not location or type(location) is not str:
			return noplace

		loc = location.lower().strip()

		if loc in self:
			return self.__getitem__(loc)

		token = loc.split(",")[0].strip()
		if token in self:
			return self.__getitem__(token)

		firstWord = re.findall(r'\w+', loc)[0]
		if firstWord in self:
			return self.__getitem__(firstWord)

		return noplace
       
	   
'''
	AddressGeocoder provides a API for geocoding address information.
	Note: Currently, this is just a wrapper for the geopy geocoders,
	but we can use the same API when our own custom geocoder is set up.
'''	
class AddressGeocoder:
		
		def __init__(self, geocoderName="GEOCODERDOTUS"): 			
		
			import geopy
		
			geocoderName = geocoderName.upper()
			
			if geocoderName == "GEOCODERDOTUS":
				self._geocoder = geopy.geocoders.GeocoderDotUS()
			else:
				self._geocoder = geopy.geocoders.GoogleV3()
		
		def lookup(self, location):
			noplace = (None, (None, None))
		
			#different geocoder return different values
			#some return a list of possible matches, other
			#just return the best match
			coded = self._geocoder.geocode(location, exactly_one=False)  
			if coded and coded is list:
				place, (lat, lng) = coded[0]
				if place and lat and lng:
					return (place, (lat, lng))
				else:
					return noplace
			else:
				place, (lat, lng) = coded
				if place and lat and lng:
					return (place, (lat, lng))
				else:
					return noplace
		
		
		
		
'''
	Miscellaneous class for point buffer operations.  
	Necessary?  Delete?
'''
class PointBuffer():
    
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
    
    
    def setCenter(self, newCenter):
        self.center = newCenter
    
    
    def setRadius(self, newRadius):
        self.radius = newRadius
        
    
    def contains(self, point):
        '''
        contains(point):
            Return True if point is in buffer, False otherwise.
        '''
        
        return self.distance(self.center, point) < self.radius
        
    
    def distance(self, a, b):
        '''
        distance(a, b):
            Returns the distance between points a and b in miles.
            Uses Great Circle distance.
        '''
        
        rad = 3958.76   #Earth radius in miles.
        
        lat1, lon1 = a[0], a[1]
        lat2, lon2 = b[0], b[1]
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2-lon1)
        
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))     
        
        return rad * c

    
import math
import re   
import os
   
CITIES_FILE = "uscities.txt"
   
class Geocoder(dict):

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
        
        loc = location.lower().strip()
        
        if not location:
            return ("None", (0.0, 0.0))
        
        if loc in self:
            return self.__getitem__(loc)

        token = loc.split(",")[0].strip()
        if token in self:
            return self.__getitem__(token)
        
        firstWd = re.findall(r'\w+', loc)[0]
        if firstWd in self:
            return self.__getitem__(firstWd)
        
        return ("None", (0.0, 0.0))
        

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

    
from pymongo import MongoClient

MULTIGEOMETRY = ("MULTILINESTRING", "MULTIPOLYGON")

class GeoMongoClient:

	def __init__(self, dbName, collectionName, createNew=True):
		try: 
			self._connection = MongoClient()
		except Exception, e:
			raise e
		
		if dbName not in self._connection.database_names():
			raise Exception("Error: Database not found: %s." % dbName)
			
		self._db = self._connection[dbName]	
		
		if not createNew and collectionName not in self._db.collection_names():
			raise Exception("Error: Collection not found: %s." % collectionName)
		
		self._collection = self._db[collectionName]
		
		#make sure spatial index is created
		self._collection.ensure_index([("geometry", "2dsphere")])
	
	
	def _combineMultiGeometry(self, docs):
		results = []
		doneGroups = []
		
		for doc in docs:
			if 'groupId' in doc:
				if doc['groupId'] not in doneGroups:
					groupResults = self._collection.find( { 'groupId': doc['groupId'] } )
					
					group = { 'type': 'Feature', 'properties': doc['properties'] }
					group['geometry'] = { 'type': 'MultiPolygon' if doc['geometry']['type'].upper() == 'POLYGON' else 'MultiLineString' }
					group['geometry']['coordinates'] = []
					for groupResult in groupResults:
						group['geometry']['coordinates'].append(groupResult['geometry']['coordinates'])
					
					doneGroups.append(doc['groupId'])
					results.append(group)
			else: 
				results.append(doc)
		
		return results
			
		
	def withinPointBuffer(self, center, radiusMiles):
		#convert miles to meters
		radiusMeters = radiusMiles * 1609.34
		
		query = { 'geometry': { '$near' : { '$geometry' : { 'type': 'Point', 'coordinates': center }, '$maxDistance' : radiusMeters } } }
		results = self._collection.find(query, {"_id" : 0})
		results = self._combineMultiGeometry(results)		
		
		return [result for result in results]
	
	
	def withinBoundingBox(self, lowerLeft, upperRight):
	
		polygon = [ [ lowerLeft[0], lowerLeft[1] ], [ lowerLeft[0], upperRight[1] ],
					[ upperRight[0], upperRight[1] ], [ upperRight[0], lowerLeft[1] ], 
					[ lowerLeft[0], lowerLeft[1] ] ]
		
		query = { 'geometry': { '$geoWithin': { '$geometry': { 'type': 'Polygon', 'coordinates': [ polygon ] } } } }
		results = self._collection.find(query, {"_id" : 0})
		results = self._combineMultiGeometry(results)
		
		return [result for result in results]
		
		
	def withinPolygon(self, polygon):
		query = { 'geometry': { '$geoWithin': { '$geometry': { 'type': 'Polygon', 'coordinates': [ polygon ] } } } }
		results = self._collection.find(query, {"_id" : 0})
		results = self._combineMultiGeometry(results)
		
		return [result for result in results]		
	
	
	def intersectsPolygon(self, polygon):
		query = { 'geometry': { '$geoIntersects': { '$geometry': { 'type': 'Polygon', 'coordinates': [ polygon ] } } } }
		results = self._collection.find(query, {"_id" : 0})
		results = self._combineMultiGeometry(results)
		
		return [result for result in results]
	
	
	def intersectsLine(self, line):
		query = { 'geometry': { '$geoIntersects': { '$geometry': { 'type': 'LineString', 'coordinates': line } } } }
		results = self._collection.find(query, {"_id" : 0})
		results = self._combineMultiGeometry(results)
		
		return [result for result in results]
		
	
	
	
	def _convertIfNumeric(self, val):
		def isFloat(string):
			try:
				float(string)
				return True
			except:
				return False

		if hasattr(val, 'isdigit') and val.isdigit():
			return int(val)
		elif isFloat(val):
			return float(val)
		
		return val
	
	
	def _explodeMultiGeometry(self, geoJson):
		if not self._collection:
			return []
			
		if geoJson['geometry']['type'].upper() not in ('MULTIPOLYGON', 'MULTILINESTRING'):
			return geoJson
			
		#get the next groupId available...
		groupId = len(self._collection.find().distinct("groupId")) + 1
		
		result = []
		
		for coords in geoJson['geometry']['coordinates']:
			item = {}
			item['type'] = geoJson['type']
			item['properties'] = geoJson['properties']
			item['groupId'] = groupId
			item['geometry'] = { "type": "Polygon", "coordinates": coords }
			
			result.append(item)
		
		return result	

		
	def saveFeature(self, geoJson):

		#convert all strings to their numerical values (if applicable)
		for prop in geoJson['properties']:
			geoJson['properties'][prop] = self._convertIfNumeric(geoJson['properties'][prop])
					
			
		#if this feature is a MultiPolygon, explode it into a group of Polygons
		if geoJson['geometry']['type'].upper() in ('MULTIPOLYGON', 'MULTILINESTRING'):
			multi = self._explodeMultiGeometry(geoJson)
			
			for item in multi:
				self._collection.insert(item)

		else: 
			self._collection.insert(geoJson)
			
	def saveFeatures(self, geoJsonList):
		for geoJson in geoJsonList:
			self.saveFeature(geoJson)
	

			
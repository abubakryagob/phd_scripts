import requests
import json

# Define the base URL for the Xamin API
base_url = 'https://heasarc.gsfc.nasa.gov/xamin/vo/'

# Define the query parameters
table = 'nustar'
fields = 'obsid,object,ra,dec,start_time,stop_time'
conditions = "object like '%magnetar%'"

# Build the URL for the query
url = base_url + 'tap/sync?query=' + \
      'SELECT ' + fields + ' FROM ' + table + ' WHERE ' + conditions + \
      '&format=json'

# Send the query request and decode the JSON response
response = requests.get(url)
data = json.loads(response.content)

# Extract the observation IDs from the results
observation_ids = [result['obsid'] for result in data['data']]

# Print the observation IDs for magnetars
print(observation_ids)


from pymongo import MongoClient

# Access the client based on the default server
client = MongoClient()

# If the DB doesn't exist, create it
# Else, it just finds the DB
db = client['MP_Bot_Database']

Sessions = db["sessions"]
Messages = db["messages"]
Users = db["users"]
Platforms = db["platforms"]
Chatbots = db["chatbots"]
Operators = db["operators"]
Plugins = db["plugins"]
PluginParams = db["plugins"]
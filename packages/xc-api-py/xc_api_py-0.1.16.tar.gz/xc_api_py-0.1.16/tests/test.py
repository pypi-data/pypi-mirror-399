from xeno_canto import Client, LeanClient, tags
from dotenv import dotenv_values
from rich import print

env = dotenv_values()
api_key = env.get('XC_API_KEY')
if not api_key:
  raise RuntimeError()

client = LeanClient(api_key)

for r in client.search(quality=tags.RecordingQuality.at_most('E'), limit=10):
  print(r)

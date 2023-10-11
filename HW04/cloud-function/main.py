from google.cloud import storage
from google.cloud import pubsub_v1
import functions_framework

@functions_framework.http
def get_file(request):
  # set up pub sub
  publisher = pubsub_v1.PublisherClient()
  topic_path = publisher.topic_path('ds561-trial-project', 'banned-countries-topic')

  # get country from header X-country
  country = request.headers.get('X-country')

  # publish to banned-countries topic if country is banned
  # (North Korea, Iran, Cuba, Myanmar, Iraq, Libya, Sudan, Zimbabwe and Syria)
  banned_countries = ['north korea', 'iran', 'cuba', 'myanmar', 'iraq', 'libya', 'sudan', 'zimbabwe', 'syria']

  # if the country is banned, publish to banned-countries topic
  if country and country.lower() in banned_countries:
    publisher.publish(topic_path, country.encode('utf-8'))
    print('Banned country:', country)
    return 'Banned country', 400

  # only accept GET method
  if request.method != 'GET':
    print('Method not implemented:', request.method)
    return 'Method not implemented', 501

  # get dirname/filename.html from path
  # path should be function_name/bucket_name/dirname/filename.html
  bucket_name = request.path.split('/')[1]
  file_name = '/'.join(request.path.split('/')[2:])

  if file_name is None:
    print('file_name is required')
    return 'file_name is required', 400
  
  # get file from bucket
  storage_client = storage.Client()

  bucket = storage_client.bucket(bucket_name)

  blob = bucket.blob(file_name)

  if blob.exists():
    blob_content = blob.download_as_string()
    return blob_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
  
  print('File not found:', f'{bucket_name}/{file_name}')
  return 'File not found', 404
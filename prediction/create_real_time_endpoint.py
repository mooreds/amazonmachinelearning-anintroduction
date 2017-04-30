import boto3

model_name = 'ML model: Adult V2'
client = boto3.client('machinelearning')

res = client.describe_ml_models(FilterVariable='Name', EQ=model_name)

#print res['Results'][0]['MLModelId']
our_id = res['Results'][0]['MLModelId']
#print res['Results'][0]['EndpointInfo']
#print res['Results'][0]['EndpointInfo']['EndpointUrl']

response = client.create_realtime_endpoint(MLModelId=our_id)

print response

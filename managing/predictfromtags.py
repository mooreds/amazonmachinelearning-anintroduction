import boto3

client = boto3.client('machinelearning')

def lookup_by_tag(key,val):
  res = client.describe_ml_models(FilterVariable='MLModelType', EQ='BINARY')
  resource_type = 'MLModel'
  model_id = None
  endpoint_url = ''
  
  for model in res['Results']:
    tags_response = client.describe_tags(ResourceId=model['MLModelId'], ResourceType=resource_type)
    for tag in tags_response['Tags']:
      if tag['Key'] == 'envt' and tag['Value'] == 'prod-income':
        model_id = model['MLModelId']
        endpoint_url = model['EndpointInfo']['EndpointUrl']
        return [model_id,endpoint_url]


# looking up endpoint 
model_id_and_endpoint = lookup_by_tag('envt','prod-income')
model_id = model_id_and_endpoint[0] 
endpoint_url = model_id_and_endpoint[1]

# build map of variables to observations
# from http://stackoverflow.com/questions/11918909/how-do-i-create-a-dictionary-from-two-parallel-strings
keys_str = 'age, workclass, fnlwgt, education, education-num, marital-status, occupation, relationship, race, sex, capital-gain, capital-loss, hours-per-week, native-country'
vals_str = '51, Local-gov, 108435, Masters, 14, Married-civ-spouse, Prof-specialty, Husband, White, Male, 0, 0, 80, United-States'
keys = keys_str.split(',')
values = vals_str.split(',')
output_dict = dict(zip(keys, values))

# call out to AML
response = client.predict(
  MLModelId=model_id,
  Record=output_dict,
  PredictEndpoint=endpoint_url 
)

# sample output
# {u'Prediction': {u'predictedLabel': u'1', u'predictedScores': {u'1': 0.5438420176506042}, u'details': {u'PredictiveModelType': u'BINARY', u'Algorithm': u'SGD'}}, 'ResponseMetadata': {'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': '6b03e335-2d5b-11e7-b4ae-71cee76f4b2d', 'HTTPHeaders': {'x-amzn-requestid': '6b03e335-2d5b-11e7-b4ae-71cee76f4b2d', 'date': 'Sun, 30 Apr 2017 04:13:51 GMT', 'content-length': '141', 'content-type': 'application/x-amz-json-1.1'}}}

# print the response
print response['Prediction']['predictedLabel']


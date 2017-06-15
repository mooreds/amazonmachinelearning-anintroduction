import boto3

client = boto3.client('machinelearning')

model_name = 'ML model: Adult Income V1'
res = client.describe_ml_models(FilterVariable='Name', EQ=model_name)

model_id = res['Results'][0]['MLModelId']
endpoint_url = res['Results'][0]['EndpointInfo']['EndpointUrl']

# from http://stackoverflow.com/questions/11918909/how-do-i-create-a-dictionary-from-two-parallel-strings
keys_str = 'age, workclass, fnlwgt, education, education-num, marital-status, occupation, relationship, race, sex, capital-gain, capital-loss, hours-per-week, native-country'
vals_str = '51, Local-gov, 108435, Masters, 14, Married-civ-spouse, Prof-specialty, Husband, White, Male, 0, 0, 80, United-States'
keys = keys_str.split(',')
values = vals_str.split(',')
output_dict = dict(zip(keys, values))

response = client.predict(
  MLModelId=model_id,
  Record=output_dict,
  PredictEndpoint=endpoint_url 
)

# sample output
# {u'Prediction': {u'predictedLabel': u'1', u'predictedScores': {u'1': 0.5438420176506042}, u'details': {u'PredictiveModelType': u'BINARY', u'Algorithm': u'SGD'}}, 'ResponseMetadata': {'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': '6b03e335-2d5b-11e7-b4ae-71cee76f4b2d', 'HTTPHeaders': {'x-amzn-requestid': '6b03e335-2d5b-11e7-b4ae-71cee76f4b2d', 'date': 'Sun, 30 Apr 2017 04:13:51 GMT', 'content-length': '141', 'content-type': 'application/x-amz-json-1.1'}}}

print response['Prediction']['predictedLabel']


require 'aws-sdk'

client = Aws::MachineLearning::Client.new(region: 'us-east-1')

# looking up model id 
model_name = 'ML model: Adult Income V1'
res = client.describe_ml_models(filter_variable: 'Name', eq: model_name)

#puts res.inspect

# looking up endpoint 
model_id = res['results'][0]['ml_model_id']
endpoint_url = res['results'][0]['endpoint_info']['endpoint_url']
#puts endpoint_url


# build map of variables to observations
# https://stackoverflow.com/questions/5174913/combine-two-arrays-into-hash
keys_str = 'age, workclass, fnlwgt, education, education-num, marital-status, occupation, relationship, race, sex, capital-gain, capital-loss, hours-per-week, native-country'
vals_str = '51, Local-gov, 108435, Masters, 14, Married-civ-spouse, Prof-specialty, Husband, White, Male, 0, 0, 80, United-States'
keys = keys_str.split(',')
values = vals_str.split(',').map { |s| s.strip }
output_dict = Hash[*keys.zip(values).flatten]

# call out to AML
response = client.predict(
  ml_model_id: model_id,
  record: output_dict,
  predict_endpoint: endpoint_url 
)

# sample output
# {u'Prediction': {u'predictedLabel': u'1', u'predictedScores': {u'1': 0.5438420176506042}, u'details': {u'PredictiveModelType': u'BINARY', u'Algorithm': u'SGD'}}, 'ResponseMetadata': {'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': '6b03e335-2d5b-11e7-b4ae-71cee76f4b2d', 'HTTPHeaders': {'x-amzn-requestid': '6b03e335-2d5b-11e7-b4ae-71cee76f4b2d', 'date': 'Sun, 30 Apr 2017 04:13:51 GMT', 'content-length': '141', 'content-type': 'application/x-amz-json-1.1'}}}

# print the response
puts response['prediction']
puts response['prediction']['predicted_label']


import boto3
import json
import re
import time

ml_bucket = 'aml-an-intro'
data_location = 'adult-income/data/'
schema_data_location = 'adult-income/updateschema.json'

# create data source
client = boto3.client('machinelearning')

timestamp = str(int(time.time()))

# unique names: http://docs.aws.amazon.com/machine-learning/latest/dg/names-and-ids-for-all-objects.html
datasource_id = 'ds-adult-income-v2-training-'+timestamp
datasource_name='Adult Income V2 Training/'+timestamp

response = client.create_data_source_from_s3(
        DataSourceId=datasource_id,
        DataSourceName=datasource_name,
        DataSpec={
          'DataLocationS3': 's3://'+ml_bucket+"/"+data_location,
          'DataSchemaLocationS3': 's3://'+ml_bucket+"/"+schema_data_location
        },
        ComputeStatistics=True
)

waiter = client.get_waiter('data_source_available')
waiter.wait(FilterVariable='Name', EQ=datasource_name)

def lookup_by_tag(key,val):
  res = client.describe_ml_models(FilterVariable='MLModelType', EQ='BINARY')
  resource_type = 'MLModel'
  model_id = None
  
  for model in res['Results']:
    tags_response = client.describe_tags(ResourceId=model['MLModelId'], ResourceType=resource_type)
    for tag in tags_response['Tags']:
      if tag['Key'] == key and tag['Value'] == val:
        model_id = model['MLModelId']
        return model_id

# look up current prod model id
model_id = lookup_by_tag('envt','prod-income')

current_prod_model_verbose = client.get_ml_model(
        MLModelId=model_id,
        Verbose=True
)

# copying everything from existing model except the new datasource and name/id

ml_model_type = current_prod_model_verbose['MLModelType']
recipe = current_prod_model_verbose['Recipe']
score_threshold = current_prod_model_verbose['ScoreThreshold']
training_parameters = current_prod_model_verbose['TrainingParameters']

new_model_id = 'ml-adult-income-v2-'+timestamp
response = client.create_ml_model(
    MLModelId=new_model_id,
    MLModelName='Adult Income V2',
    MLModelType=ml_model_type,
    Parameters=training_parameters,
    TrainingDataSourceId=datasource_id,
    Recipe=recipe
)

# waiting for model to finish building
waiter = client.get_waiter('ml_model_available')
waiter.wait(FilterVariable='TrainingDataSourceId', EQ=datasource_id)

new_model = client.get_batch_prediction(
        MLModel_Id=new_model_id
)

print new_model

# update score threshold

# add tags

# update score threshold

sys.exit()



import boto3
import json
import re
import time

def lookup_by_tag(key, val, client):
  res = client.describe_ml_models(FilterVariable='MLModelType', EQ='BINARY')
  resource_type = 'MLModel'
  model_id = None
  
  for model in res['Results']:
    tags_response = client.describe_tags(ResourceId=model['MLModelId'], ResourceType=resource_type)
    for tag in tags_response['Tags']:
      if tag['Key'] == key and tag['Value'] == val:
        model_id = model['MLModelId']
        return model_id

def retrieve_auc(model_id, client):
  response = client.describe_evaluations(
      FilterVariable='MLModelId',
      EQ=model_id
  )

  auc = response['Results'][0]['PerformanceMetrics']['Properties']['BinaryAUC']
  return auc

ml_bucket = 'aml-an-intro'
data_location = 'adult-income/data/'
schema_data_location = 'adult-income/updateschema.json'

# create data source
client = boto3.client('machinelearning')

timestamp = str(int(time.time()))

# unique names: http://docs.aws.amazon.com/machine-learning/latest/dg/names-and-ids-for-all-objects.html
training_datasource_id = 'ds-adult-income-v2-training-'+timestamp
training_datasource_name='Adult Income V2 Training DS/'+timestamp
training_data_rearrangment = '{ "splitting": { "percentBegin": 0, "percentEnd": 70 } }'

eval_datasource_id = 'ds-adult-income-v2-eval-'+timestamp
eval_datasource_name='Adult Income V2 Eval DS/'+timestamp
eval_data_rearrangment = '{ "splitting": { "percentBegin": 70, "percentEnd": 100 } }'

response = client.create_data_source_from_s3(
        DataSourceId=training_datasource_id,
        DataSourceName=training_datasource_name,
        DataSpec={
          'DataLocationS3': 's3://'+ml_bucket+"/"+data_location,
          'DataSchemaLocationS3': 's3://'+ml_bucket+"/"+schema_data_location,
          'DataRearrangement': training_data_rearrangment
        },
        ComputeStatistics=True
)

response = client.create_data_source_from_s3(
        DataSourceId=eval_datasource_id,
        DataSourceName=eval_datasource_name,
        DataSpec={
          'DataLocationS3': 's3://'+ml_bucket+"/"+data_location,
          'DataSchemaLocationS3': 's3://'+ml_bucket+"/"+schema_data_location,
          'DataRearrangement': eval_data_rearrangment
        },
        ComputeStatistics=False
)

print "creating data sources"
waiter = client.get_waiter('data_source_available')
waiter.wait(FilterVariable='Name', EQ=training_datasource_name)
waiter = client.get_waiter('data_source_available')
waiter.wait(FilterVariable='Name', EQ=eval_datasource_name)

# look up current prod model id
old_model_id = lookup_by_tag('envt','prod-income', client)

current_prod_model_verbose = client.get_ml_model(
        MLModelId=old_model_id,
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
    MLModelName='Adult Income V2 Model',
    MLModelType=ml_model_type,
    Parameters=training_parameters,
    TrainingDataSourceId=training_datasource_id,
    Recipe=recipe
)

print "creating model"
# waiting for model to finish building
waiter = client.get_waiter('ml_model_available')
waiter.wait(FilterVariable='TrainingDataSourceId', EQ=training_datasource_id)

new_model = client.get_ml_model(
        MLModelId=new_model_id
)

#print new_model

# update score threshold via update
response = client.update_ml_model(
    MLModelId=new_model_id,
    ScoreThreshold=score_threshold
)
# do evaluation

evaluation_id = 'ev-adult-income-v2-'+timestamp
evaluation_name='Adult Income V2 Eval/'+timestamp
response = client.create_evaluation(
    EvaluationId=evaluation_id,
    EvaluationName=evaluation_name,
    MLModelId=new_model_id,
    EvaluationDataSourceId=eval_datasource_id
)

print "creating evaluation of new model"
waiter = client.get_waiter('evaluation_available')
waiter.wait(FilterVariable='MLModelId', EQ=new_model_id)

# print AUC of both new and old

old_auc = retrieve_auc(old_model_id, client)
new_auc = retrieve_auc(new_model_id, client)
print "old auc: "+str(old_auc)
print "new auc: "+str(new_auc)

# add tags
# move the production tag from the old system to the new.
# unfortunately no way to make this transactional
print "moving production tag from "+old_model_id+" to new model: "+new_model_id
response = client.add_tags(
    Tags=[
        {
            'Key': 'envt',
            'Value': 'prod-income'
        },
        {
            'Key': 'prod-timestamp',
            'Value': timestamp
        },
    ],
    ResourceId=new_model_id,
    ResourceType='MLModel'
)

response = client.delete_tags(
    TagKeys=[
        'envt'
    ],
    ResourceId=old_model_id,
    ResourceType='MLModel'
)


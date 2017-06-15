import boto3
import json
import re


ml_bucket = 'aml-an-intro'
batch_data_location = 'batch-prediction-upload/adultincomebatch1.csv'
schema_data_location = 'batch-prediction-upload/adultincomebatchschema.json'

s3 = boto3.resource('s3')

with open('adulttotest.csv', 'r') as data:
  s3.Bucket(ml_bucket).put_object(Key=batch_data_location, Body=data)

with open('batchschema.json', 'r') as schema:
  s3.Bucket(ml_bucket).put_object(Key=schema_data_location, Body=schema)

client = boto3.client('machinelearning')

datasource_id = 'ds-adult-income-v1-batch-2'

response = client.create_data_source_from_s3(
        DataSourceId=datasource_id,
        DataSourceName='Adult Income V1 Batch 2',
        DataSpec={
          'DataLocationS3': 's3://'+ml_bucket+"/"+batch_data_location,
          'DataSchemaLocationS3': 's3://'+ml_bucket+"/"+schema_data_location
        },
        ComputeStatistics=False
)

model_name = 'ML model: Adult Income V1'

res = client.describe_ml_models(FilterVariable='Name', EQ=model_name)

model_id = res['Results'][0]['MLModelId']

output_prefix = 'batch-prediction-results/adult-income-v1'
output_uri = 's3://'+ml_bucket+'/'+output_prefix
response = client.create_batch_prediction(
        BatchPredictionId='batch2adultincomev1',
        BatchPredictionName='Batch 2 Adult Income v1',
        MLModelId=model_id,
        BatchPredictionDataSourceId=datasource_id,
        OutputUri=output_uri
        )

batch_id = response['BatchPredictionId']
#print batch_id

waiter = client.get_waiter('batch_prediction_available')
waiter.wait(FilterVariable='DataSourceId', EQ=datasource_id)

batch_response = client.get_batch_prediction(
        BatchPredictionId=batch_id
)

#print batch_response['Status']

bucket = s3.Bucket(ml_bucket)
manifest_path = output_prefix +'/batch-prediction/'+batch_id+'.manifest'
bucket.download_file(manifest_path, '/tmp/manifest')

output_location_key = 's3://'+ml_bucket+"/"+batch_data_location 
with open('/tmp/manifest', 'r') as myfile:
  manifest_content=myfile.read().replace('\n', '')
  manifest = json.loads(manifest_content)
  results_key = manifest[output_location_key]
  
  # convert from uri to key
  results_key = re.sub('^s3:\/\/'+ml_bucket+'/', '', results_key)
  path = 'batch-prediction-results/adult-income-v1/'+'batch-prediction/'+batch_id+'.manifest'
  output_file_name = '/tmp/'+batch_id+'.gz'
  bucket.download_file(results_key, output_file_name)
  print output_file_name 


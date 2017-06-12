import boto3

client = boto3.client('machinelearning')

model_name = 'ML model: Adult V4'

res = client.describe_ml_models(FilterVariable='Name', EQ=model_name)

model_id = res['Results'][0]['MLModelId']

datasource_id = 'ds-8Tp23NS7BQ3'
response = client.create_batch_prediction(
        BatchPredictionId='batch11adultv4',
        BatchPredictionName='Batch 11 Adult v4',
        MLModelId=model_id,
        BatchPredictionDataSourceId=datasource_id,
        OutputUri='s3://aml-an-intro/batch-prediction-results'
        )

batch_id = response['BatchPredictionId']
print batch_id

waiter = client.get_waiter('batch_prediction_available')
waiter.wait(FilterVariable='DataSourceId', EQ=datasource_id)

batch_response = client.get_batch_prediction(
        BatchPredictionId=batch_id
)

print batch_response['Status']

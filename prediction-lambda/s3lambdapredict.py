import boto3

def lambda_handler(event, context):
    client = boto3.client('machinelearning')
    s3 = boto3.resource('s3')
    
    # looking up model id 
    model_name = 'ML model: Adult Income V1'
    res = client.describe_ml_models(FilterVariable='Name', EQ=model_name)

    # looking up endpoint 
    model_id = res['Results'][0]['MLModelId']
    endpoint_url = res['Results'][0]['EndpointInfo']['EndpointUrl']

    # build map of variables to observations
    # from http://stackoverflow.com/questions/11918909/how-do-i-create-a-dictionary-from-two-parallel-strings
    keys_str = 'age, workclass, fnlwgt, education, education-num, marital-status, occupation, relationship, race, sex, capital-gain, capital-loss, hours-per-week, native-country'
    # get vals str from s3 obj
    
    keys = keys_str.split(',')
    #s3Bucket = s3.Bucket('aml-an-intro')
    #print s3Bucket.creation_date
    #for obj in s3Bucket.objects.filter(Prefix='adult-income/'):
    #    print('{0}:{1}'.format(s3Bucket.name, obj.key))
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        s3obj = s3.Bucket(bucket).Object(key)

        vals_str = s3obj.get()['Body'].read().decode('utf-8')  
        
        print vals_str
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

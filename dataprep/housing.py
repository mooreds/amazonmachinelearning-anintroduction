# Prep script for the data found at https://archive.ics.uci.edu/ml/datasets/Housing
#
#    1. CRIM      per capita crime rate by town
#    2. ZN        proportion of residential land zoned for lots over 
#                 25,000 sq.ft.
#    3. INDUS     proportion of non-retail business acres per town
#    4. CHAS      Charles River dummy variable (= 1 if tract bounds 
#                 river; 0 otherwise)
#    5. NOX       nitric oxides concentration (parts per 10 million)
#    6. RM        average number of rooms per dwelling
#    7. AGE       proportion of owner-occupied units built prior to 1940
#    8. DIS       weighted distances to five Boston employment centres
#    9. RAD       index of accessibility to radial highways
#    10. TAX      full-value property-tax rate per $10,000
#    11. PTRATIO  pupil-teacher ratio by town
#    12. B        1000(Bk - 0.63)^2 where Bk is the proportion of blacks 
#                 by town
#    13. LSTAT    % lower status of the population
#    14. MEDV     Median value of owner-occupied homes in $1000's


import re

def fix_for_batch(line):
  # remove last field, as that is our target field
  p = re.compile(',[^,]*$')
  line = p.sub("\n", line)
  return line

training_number_of_lines = 400
tobatch = open('housingtotest.csv', 'w') 
totrain = open('housingtotrain.csv', 'w') 
headerline = "CRIM,ZN,INDUS,CHAS,NOX,RM,AGE,DIS,RAD,TAX,PTRATIO,B,LSTAT,LSTAT,MEDV\n"
with open('housing.data') as f:
  content = f.readlines()
  idx = 0
  headerfortrainwritten = False
  headerforbatchwritten = False
  turn_space_to_commas = re.compile(' +')
  remove_first_comma = re.compile('^,')
  for line in content:
    line = turn_space_to_commas.sub(",", line)
    line = remove_first_comma.sub("", line)
    if not headerfortrainwritten:
      totrain.write(headerline)
      headerfortrainwritten = True
    if idx > training_number_of_lines:
      if not headerforbatchwritten:
        # make sure both batch and training have same headers
        tobatch.write(fix_for_batch(headerline))
        headerforbatchwritten = True
      tobatch.write(fix_for_batch(line))
    if idx <= training_number_of_lines:
      totrain.write(line)
      
    idx = idx+1


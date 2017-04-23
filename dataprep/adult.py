# Prep script for the data found at https://archive.ics.uci.edu/ml/datasets/Census+Income

#>50K, <=50K.
#
#age: continuous.
#workclass: Private, Self-emp-not-inc, Self-emp-inc, Federal-gov, Local-gov, State-gov, Without-pay, Never-worked.
#fnlwgt: continuous.
#education: Bachelors, Some-college, 11th, HS-grad, Prof-school, Assoc-acdm, Assoc-voc, 9th, 7th-8th, 12th, Masters, 1st-4th, 10th, Doctorate, 5th-6th, Preschool.
#education-num: continuous.
#marital-status: Married-civ-spouse, Divorced, Never-married, Separated, Widowed, Married-spouse-absent, Married-AF-spouse.
#occupation: Tech-support, Craft-repair, Other-service, Sales, Exec-managerial, Prof-specialty, Handlers-cleaners, Machine-op-inspct, Adm-clerical, Farming-fishing, Transport-moving, Priv-house-serv, Protective-serv, Armed-Forces.
#relationship: Wife, Own-child, Husband, Not-in-family, Other-relative, Unmarried.
#race: White, Asian-Pac-Islander, Amer-Indian-Eskimo, Other, Black.
#sex: Female, Male.
#capital-gain: continuous.
#capital-loss: continuous.
#hours-per-week: continuous.
#native-country: United-States, Cambodia, England, Puerto-Rico, Canada, Germany, Outlying-US(Guam-USVI-etc), India, Japan, Greece, South, China, Cuba, Iran, Honduras, Philippines, Italy, Poland, Jamaica, Vietnam, Mexico, Portugal, Ireland, France, Dominican-Republic, Laos, Ecuador, Taiwan, Haiti, Columbia, Hungary, Guatemala, Nicaragua, Scotland, Thailand, Yugoslavia, El-Salvador, Trinadad&Tobago, Peru, Hong, Holand-Netherlands.

import re

def fix_for_batch(line):
  # remove last field, as that is our target field
  p = re.compile(',[^,]*$')
  line = p.sub("\n", line)
  return line

training_number_of_lines = 32000
tobatch = open('adulttotest.csv', 'w') 
totrain = open('adulttotrain.csv', 'w') 
headerline = "age, workclass, fnlwgt, education, education-num, marital-status, occupation, relationship, race, sex, capital-gain, capital-loss, hours-per-week, native-country, income-greater-50k\n"

with open('adult.data') as f:
  content = f.readlines()
  idx = 0
  less_than_50_str = '<=50K'
  greater_than_50_str = '>50K'

  headerfortrainwritten = False
  headerforbatchwritten = False
  update_boolean_false = re.compile(less_than_50_str)
  update_boolean_true = re.compile(greater_than_50_str)
  for line in content:
    line = update_boolean_false.sub("false", line)
    line = update_boolean_true.sub("true", line)
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


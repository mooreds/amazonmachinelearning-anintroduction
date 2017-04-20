# Prep script for the data found at https://archive.ics.uci.edu/ml/datasets/Wine+Quality

def fix_for_batch(line):
  # remove last field
  line = line[:-3] + "\n"
  return line

training_number_of_lines = 4000
tobatch = open('whitetotest.csv', 'w') 
totrain = open('whitetotrain.csv', 'w') 
with open('winequality-white.csv') as f:
  content = f.readlines()
  headerline = ''
  idx = 0
  headerforbatchwritten = False
  for line in content:
    line = line.replace(';',',')
    if idx == 0:
      headerline = line
    if idx > training_number_of_lines:
      if not headerforbatchwritten:
        # make sure both batch and training have same headers
        tobatch.write(fix_for_batch(headerline))
        headerforbatchwritten = True
      tobatch.write(fix_for_batch(line))
    if idx <= training_number_of_lines:
      totrain.write(line)
      
    idx = idx+1


import pandas as pd

import clean_info as ci 
import model_selection as ms # use model selection for predictions
import random 

csv = 'Prof Clarkson Test Data - Sheet1 (1).csv'
features = ['Name','Gender','Major','Grad Year','Class 1','Class 2','Class 3','Class 4','Interest 1','Interest 2','Study Habits','Hometown','Campus Location','Race','Preferences']
training_features = ['Name','Gender','Major','Grad Year','Classes','Interests','Study Habits','Hometown','Campus Location','Race','Preferences']
primary = 'Name'
# groupby = 'Race'
groupby = None
num = 2
do_random = True    
rand_num = 3
use_index = False 

'''
1. add groupby
'''

# Load data from csv
metadata = pd.read_csv(csv)
m0 = metadata[features]
m0 = m0.reset_index()

def speed_up_pairings(m0, model_num):

    m1 = m0.copy()
    m1 = ci.clean_df(m1, features, primary)
    
    if use_index:
        names = list(m1['index'])
    else:
        names = list(m1['Name'])

    data = [['-'] * (len(features)+1)]
    extra = pd.DataFrame(data, columns=features + ['index'])

    pairs = pd.DataFrame(columns=features + ['index'])
    already_paired = []
    not_paired = names 
    for n in names:
        if n not in already_paired:
            not_paired.remove(n)
            already_paired.append(n)
            
            if use_index:
                pairs = pairs.append(m0[m0['index'] == n].iloc[0])
            else:
                n_index = m1['index'][m1['Name'] == n].iloc[0]
                pairs = pairs.append(m0[m0['index'] == n_index].iloc[0])

            data = [ [str(n) + "; " + str(x)] if use_index else [n + "; " + x] for x in not_paired ]
            df = pd.DataFrame(data, columns=['group'])

            df_soup = ms.load_prediction(df, m1, model_num)
            X_test = df_soup[[x for x in training_features if x != primary]]

            predictions = ms.make_prediction(df_soup, X_test, model_num) # already sorted

            group_sims = []
            for p in predictions.iterrows():
                if (len(group_sims) == rand_num): break
                n, x = (p[1]['Name']).split("; ")
                group_sims.append(x)
            
            if (len(group_sims) >= num):
                if do_random:
                    result = random.sample(group_sims, num-1)
                else:
                    result = group_sims[:num]
            else:
                result = group_sims
            
            if use_index:
                matches = [ int(x) for x in result ]
                not_paired = [ x for x in not paired if x not in matches ]
                already_paired += matches
            else: 
                already_paired += result
                not_paired = [ x for x in not_paired if x not in result ]
                matches = [ m1['index'][m1['Name'] == m].iloc[0] for m in result ]

            for m in matches:
                pairs = pairs.append(m0[m0['index'] == m].iloc[0])
            
            pairs = pd.concat([pairs, extra], sort=False)
    return pairs  

df = speed_up_pairings(m0, 1)
print(df)
df.to_csv('testing.csv', index=False)
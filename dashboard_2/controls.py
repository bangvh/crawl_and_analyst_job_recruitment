import pandas as pd

df = pd.read_pickle('data.pkl')

PROVINCE = df['province_recode'].value_counts().head(10).index.to_list()

EXPERIENCE =  df['experience_recode'].value_counts().index.to_list()
EXPERIENCE.sort()

TAG = df['tag'].value_counts().head(5).index.to_list()

RANGE_SALARY = ['<2K', '2-5K', '5-10K', '10K+']
RANGE_SALARY.append('All')


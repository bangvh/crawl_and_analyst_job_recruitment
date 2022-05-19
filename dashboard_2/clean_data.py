import pandas as pd
import re

file_input = '.\c.xlsx'
df = pd.read_excel(file_input)
df.columns = ['index', 'province', 'salary', 'cop_name', 'cop_info', 'experience', 'tag', 'benefits']
df = df.applymap(lambda s: s.lower() if type(s) == str else s)

# recode function
def recode_province(df):
    province_lov = 'changsha, chu hải, changchun, zaozhuang, hangzhou, thạch gia trang, chengdu, dongguan, phật sơn, phúc châu, hạ môn, trường sa, bảo bình, hàng châu, hợp phì, thâm quyến, tô châu, thượng hải, bắc kinh, hồng kông, thiên tân, vũ hán, thẩm dương, quảng châu, cáp nhĩ tân, tây an, trùng khánh, thành đô, trường xuân, thái nguyên, nam kinh, tế nam, đại liên, thanh đảo, lan châu, phủ thuận, trịnh châu'.split(',')
    province_lov = [p.strip().lower() for p in province_lov]
    province_regex = '|'.join(province_lov)
    df['province_recode'] = df.province.str.findall(province_regex).str[0]
    return df

def recode_salary(s):
    w = 1
    if 'k' in s or 'nghìn' in s:
        w *= 1_000
    if 'nhân dân tệ / ngày' in s:
        w *= 30

    l2u = re.findall("\d+\-\d+", s)[0].split('-')
    l = int(l2u[0]) * w
    u = int(l2u[1]) * w
    return (l, u)

def recode_experience(x):
    try:
        result = re.findall('\d{1}', x)
        result = min([int(i) for i in result])
        return result
    except:
        return 0


# process
df = recode_province(df)
df['salary_low'] = df['salary'].apply(lambda x: recode_salary(x)[0])
df['salary_up'] = df['salary'].apply(lambda x: recode_salary(x)[1])
df['salary_mean'] = df['salary_low'].add(df['salary_up']).divide(2).astype('int')
df['experience_recode'] = df['experience'].apply(lambda x: recode_experience(x))
df = df[['province_recode', 'salary_up', 'salary_low', 'salary_mean', 'experience_recode', 'tag']]
df.to_excel("data.xlsx")

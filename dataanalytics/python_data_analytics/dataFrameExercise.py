import pandas as pd

# 1. Read data from the CSV file
df = pd.read_excel('../datas/student.xlsx', index_col=None, engine='openpyxl')
# print(df)

# 2. check the number of rows and columns
print("No of rows and colum: ", df.shape)
# print ("No of rows: ", df.shape[0])
# print ("No of columns: ", df.shape[1])

# 3. Print the first 4 rows
print("First 4 rows: ", df.head(4))
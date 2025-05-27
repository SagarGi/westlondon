from pyspark.sql import SparkSession

# Code for Answer to question 1
# Create a Spark session so that data can be loaded with PySpark
spark = SparkSession.builder \
    .appName("Load the dataset into Pyspark DataFrame") \
    .getOrCreate()
pathToDataset = "dataanalytics-assessment3/customer_purchases.csv"
# Load the dataset into a PySpark DataFrame
dataFrame = spark.read.csv(pathToDataset, header=True, inferSchema=True)
# Show the first few rows of the DataFrame to verify the data has been loaded correctly
dataFrame.show()
# show the schema of the DataFrame
dataFrame.printSchema()
# show the summary statistics of the DataFrame
dataFrame.describe().show()
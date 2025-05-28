from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, expr, count, min, max, mean, stddev, variance, percentile_approx
import matplotlib.pyplot as plt
import pandas as pd

pathToDataset = "dataanalytics-assessment3/customer_purchases.csv"
spark = SparkSession.builder.appName("CustomerPurchases").getOrCreate()
pathToDataset = "dataanalytics-assessment3/customer_purchases.csv"
dataFlow1 = spark.read.csv(pathToDataset, header=True, inferSchema=True)
median_spending_score = dataFlow1.select(percentile_approx("SpendingScore", 0.5)).first()[0]
median_total_purchase = dataFlow1.select(percentile_approx("TotalPurchases", 0.5)).first()[0]
dataFlow2 = dataFlow1.withColumn(
    "SpendingScore",
    when(col("SpendingScore") == 0, median_spending_score).otherwise(col("SpendingScore"))
).withColumn(
    "TotalPurchases",
    when(col("TotalPurchases") == 0, median_total_purchase).otherwise(col("TotalPurchases"))
)

# Create the 3rd DataFrame (dataFlow3) by removing rows with '0' values in specified columns
dataFlow3 = dataFlow2.filter(
    (col("Age") != 0) &
    (col("AnnualIncome") != 0) &
    (col("PurchaseAmount") != 0)
)


# --- Question 7: Spark SQL Query ---
print("\n Displaying 'Age' and 'SpendingScore' from dataFlow3 using Spark SQL")
dataFlow3.createOrReplaceTempView("customer_data")

#Spark SQL query
spark_sql_query1 = """
SELECT Age, SpendingScore
FROM customer_data
WHERE Age < 50 AND SpendingScore >= 100
"""

spark_sql_query2 = """
SELECT Age, SpendingScore
FROM customer_data
WHERE Age < 50 AND SpendingScore > 100
"""

# Display the results where age is less than 50 and SpendingScore >= 100
print("\nResults where Age < 50 and SpendingScore >= 100:")
spark.sql(spark_sql_query1).show()
print("\nResults where Age < 50 and SpendingScore > 100:")
# Display the results where age is less than 50 and SpendingScore > 100
spark.sql(spark_sql_query2).show()

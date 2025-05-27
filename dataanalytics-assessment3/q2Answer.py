from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, expr
from pyspark.sql.functions import percentile_approx

# Initialize Spark session
pathToDataset = "dataanalytics-assessment3/customer_purchases.csv"
spark = SparkSession.builder.appName("CustomerPurchases").getOrCreate()
pathToDataset = "dataanalytics-assessment3/customer_purchases.csv"
# Load CSV into first DataFrame
dataFlow1 = spark.read.csv(pathToDataset, header=True, inferSchema=True)
# Calculate medians
median_spending_score = dataFlow1.select(percentile_approx("SpendingScore", 0.5)).first()[0]
median_total_purchase = dataFlow1.select(percentile_approx("TotalPurchases", 0.5)).first()[0]
# Replace 0s with median values
dataFlow2 = dataFlow1.withColumn(
    "SpendingScore",
    when(col("SpendingScore") == 0, median_spending_score).otherwise(col("SpendingScore"))
).withColumn(
    "TotalPurchases",
    when(col("TotalPurchases") == 0, median_total_purchase).otherwise(col("TotalPurchases"))
)
print("Median Spending Score:", median_spending_score)
print("Median Total Purchases:", median_total_purchase)
dataFlow2.show()

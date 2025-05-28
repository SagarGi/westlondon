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

# 6. Analysis and graph
correlation_value = dataFlow3.stat.corr("PurchaseAmount", "SpendingScore", "pearson")
print(f"\nPearson Correlation between 'PurchaseAmount' and 'SpendingScore': {correlation_value}")
print("\n--- Generating Scatter Plot for 'PurchaseAmount' vs 'SpendingScore' ---")
selected_columns_for_plot_pandas = dataFlow3.select("PurchaseAmount", "SpendingScore").toPandas()

# Plotting (Matplotlib)
if not selected_columns_for_plot_pandas.empty:
    plt.figure(figsize=(10, 7))
    plt.scatter(
        selected_columns_for_plot_pandas['PurchaseAmount'],
        selected_columns_for_plot_pandas['SpendingScore'],
        alpha=0.6,
        s=10
    )
    plt.xlabel("Purchase Amount")
    plt.ylabel("Spending Score")
    plt.title("Relationship between Purchase Amount and Spending Score")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
else:
    print("\nNo data to plot scatter plot. Check 'PurchaseAmount' and 'SpendingScore' columns in dataFlow3.")

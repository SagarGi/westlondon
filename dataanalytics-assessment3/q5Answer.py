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

# 5. Analysis and Box Plotting
print("\n--- Quartile Information for 'TotalPurchases' in dataFlow3 ---")
# Using approxQuantile to get Q1, Median (Q2), Q3
quartiles = dataFlow3.stat.approxQuantile("TotalPurchases", [0.25, 0.5, 0.75], 0.01)

if quartiles:
    print(f"Q1 (25th percentile): {quartiles[0]}")
    print(f"Q2 (Median/50th percentile): {quartiles[1]}")
    print(f"Q3 (75th percentile): {quartiles[2]}")
else:
    print("Could not compute quartiles for 'TotalPurchases'. Check data.")

# Generate a boxplot for the ‘TotalPurchase’ feature.
total_purchases_pandas = dataFlow3.select("TotalPurchases").toPandas()['TotalPurchases']
# Plotting with (Matplotlib)
print("\nBoxplot for 'TotalPurchases'")
if not total_purchases_pandas.empty:
    plt.figure(figsize=(8, 6))
    plt.boxplot(total_purchases_pandas, vert=True, patch_artist=True)
    plt.ylabel("Total Purchases")
    plt.title("Boxplot of Total Purchases")
    plt.grid(axis='y', alpha=0.75)
    plt.show()
else:
    print("\nNo data to plot boxplot. Check 'TotalPurchases' column in dataFlow3.")



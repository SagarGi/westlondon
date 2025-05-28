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

# 1. Compute the total number of rows removed from the 2nd DataFrame
rows_in_dataFlow2 = dataFlow2.count()
rows_in_dataFlow3 = dataFlow3.count()
rows_removed_from_dataFlow2 = rows_in_dataFlow2 - rows_in_dataFlow3
print(f"\n\n")

print(f"Total number of rows removed from dataFlow2: {rows_removed_from_dataFlow2}")


# 2. Compute summary statistics of the ‘PurchaseAmount’ feature in the 3rd DataFrame
#    including its min value, max value, mean value, median value, variance, and standard deviation.

# Display standard summary statistics
print("\n--- Standard Summary Statistics for 'PurchaseAmount' in dataFlow3 (using describe()) ---")
dataFlow3.agg(
    min("PurchaseAmount").alias("Min"),
    max("PurchaseAmount").alias("Max"),
    mean("PurchaseAmount").alias("Mean"),
    percentile_approx("PurchaseAmount", 0.5).alias("Median"),
    variance("PurchaseAmount").alias("Variance"),
    stddev("PurchaseAmount").alias("StdDev")
).show()


# 3. Generate data for a histogram for the ‘PurchaseAmount’ feature
print("\n--- Histogram Data for 'PurchaseAmount' (PySpark DataFrame) ---")
min_val_hist = dataFlow3.select(min("PurchaseAmount")).first()[0]
max_val_hist = dataFlow3.select(max("PurchaseAmount")).first()[0]

num_bins = 30
histogram_data_pandas = pd.DataFrame()
if min_val_hist is not None and max_val_hist is not None and max_val_hist > min_val_hist:
    bin_width = (max_val_hist - min_val_hist) / num_bins
    bins = [min_val_hist + (i + 1) * bin_width for i in range(num_bins)]
    bins[-1] = max_val_hist
    case_statement = "CASE "
    for i in range(num_bins - 1):
        case_statement += f"WHEN PurchaseAmount <= {bins[i]} THEN {bins[i]} "
    case_statement += f"ELSE {bins[num_bins-1]} END"

    binned_df = dataFlow3.withColumn("PurchaseAmount_Bin_Upper", expr(case_statement))
    histogram_data = binned_df.groupBy("PurchaseAmount_Bin_Upper").agg(count("*").alias("Count")).sort("PurchaseAmount_Bin_Upper")
    histogram_data.show(truncate=False)
    histogram_data_pandas = histogram_data.toPandas()

else:
    print("Cannot generate histogram data: PurchaseAmount range is invalid or empty.")

# 4. Generate a histogram picture for the ‘PurchaseAmount’ feature
if not histogram_data_pandas.empty:
    print("\n--- Generating Histogram Picture ---")

    # Ensure 'PurchaseAmount_Bin_Upper' is sorted for correct histogram display
    collected_histogram_df = histogram_data_pandas.sort_values('PurchaseAmount_Bin_Upper')

    plt.figure(figsize=(12, 7))
    plt.bar(
        x=[f"{int(b)}" for b in collected_histogram_df['PurchaseAmount_Bin_Upper']], # Use bin upper bounds as labels
        height=collected_histogram_df['Count'],
        width=1.0,
        edgecolor='black'
    )
    plt.xlabel("Purchase Amount")
    plt.ylabel("Frequency (Count)")
    plt.title("Histogram of Purchase Amount Distribution")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    plt.show()
else:
    print("\nNo data to plot histogram. Check if PurchaseAmount range was valid.")


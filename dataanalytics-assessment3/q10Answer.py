from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, expr, count, min, max, mean, stddev, variance, percentile_approx
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Pipeline
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

# 10: Linear Regression Model

print("\n Building and Evaluating Linear Regression Model")
predictor_col = "AnnualIncome"
label_col = "PurchaseAmount"
# Assemble the predictor feature into a single vector column
# Even with a single feature, VectorAssembler is required for MLlib models.
assembler = VectorAssembler(inputCols=[predictor_col], outputCol="features")
# Split data into training and test sets
(trainingData, testData) = dataFlow3.randomSplit([0.7, 0.3], seed=42)
# Create Linear Regression model
lr = LinearRegression(featuresCol="features", labelCol=label_col)
pipeline = Pipeline(stages=[assembler, lr])
# Train the model
model = pipeline.fit(trainingData)
# Make predictions on test data
predictions = model.transform(testData)
# Select example predictions for inspection
print("\n Sample Predictions (Linear Regression)")
predictions.select(predictor_col, label_col, "prediction").show(5, truncate=False)


# Evaluate model performance
# Use RegressionEvaluator for regression metrics
evaluator_rmse = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="rmse")
rmse = evaluator_rmse.evaluate(predictions)
print(f"\nRoot Mean Squared Error (RMSE): {rmse}")

evaluator_mse = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="mse")
mse = evaluator_mse.evaluate(predictions)
print(f"Mean Squared Error (MSE): {mse}")

evaluator_r2 = RegressionEvaluator(labelCol=label_col, predictionCol="prediction", metricName="r2")
r2 = evaluator_r2.evaluate(predictions)
print(f"R-squared (R2): {r2}")

# Display model coefficients and intercept (for simple linear regression)
# The trained model is the last stage in the fitted pipeline
linear_model = model.stages[-1]
print(f"\nCoefficients: {linear_model.coefficients}")
print(f"Intercept: {linear_model.intercept}")
print(f"\n\n")

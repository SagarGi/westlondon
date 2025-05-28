from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, expr, count, min, max, mean, stddev, variance, percentile_approx
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
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

# 8 Decision Tree Classifier
print("\n Building and Evaluating Decision Tree Classifier")
label_col = "Outcome"
all_feature_cols = [c for c in dataFlow3.columns if c != label_col and c not in ["CustomerID"]] # Exclude CustomerID as it's an ID
# Identify categorical features that need indexing
categorical_features = ['Gender', 'PurchaseCategory']
numerical_features = [f for f in all_feature_cols if f not in categorical_features]
pipeline_stages = []
indexed_feature_cols = []
# Step 1: Index categorical features
for feature in categorical_features:
    indexer = StringIndexer(inputCol=feature, outputCol=feature + "_indexed", handleInvalid="keep") # "keep" unknown values as a separate category
    pipeline_stages.append(indexer)
    indexed_feature_cols.append(feature + "_indexed")
# Step 2: Index the label column if it's a string
label_indexer = StringIndexer(inputCol=label_col, outputCol="indexedLabel")
pipeline_stages.append(label_indexer)
# Step 3: Assemble all features (numerical and indexed categorical) into a single vector
assembler = VectorAssembler(inputCols=numerical_features + indexed_feature_cols, outputCol="features")
pipeline_stages.append(assembler)
# Step 4: Split data into training and test sets
(trainingData, testData) = dataFlow3.randomSplit([0.7, 0.3], seed=42)
# Step 5: Create Decision Tree Classifier model
dt = DecisionTreeClassifier(labelCol="indexedLabel", featuresCol="features", maxDepth=5) # maxDepth is tunable
pipeline_stages.append(dt)
pipeline = Pipeline(stages=pipeline_stages)
# Train the model
model = pipeline.fit(trainingData)
predictions = model.transform(testData)
print("\n Sample Predictions")
predictions.select(label_col, "indexedLabel", "prediction", "probability", "features").show(5, truncate=False)
# Evaluate model performance
evaluator_accuracy = MulticlassClassificationEvaluator(labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator_accuracy.evaluate(predictions)
print(f"Model Accuracy: {accuracy}")
print(f"\n\n")
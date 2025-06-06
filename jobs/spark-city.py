from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, DoubleType
import signal
import sys

from config import configuration


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("SmartCityStreaming")
        .config("spark.jars.packages", ",".join([
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1",
            "org.apache.hadoop:hadoop-aws:3.3.1",
            "com.amazonaws:aws-java-sdk:1.11.469"
        ]))
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.access.key", configuration.get('AWS_ACCESS_KEY'))
        .config("spark.hadoop.fs.s3a.secret.key", configuration.get('AWS_SECRET_KEY'))
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        .config("spark.sql.parquet.output.committer.class", "org.apache.hadoop.mapreduce.lib.output.FileOutputCommitter")
        .config("spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version", "2")
        .config("spark.sql.parquet.output.committer.mark-success-file", "false")
        .getOrCreate()
    )


def get_schema(topic: str) -> StructType:
    schemas = {
        "vehicle_data": StructType([
            StructField("id", StringType()),
            StructField("vehicle_id", StringType()),
            StructField("timestamp", TimestampType()),
            StructField("location", StringType()),
            StructField("speed", DoubleType()),
            StructField("direction", StringType()),
            StructField("make", StringType()),
            StructField("model", StringType()),
            StructField("year", IntegerType()),
            StructField("fuelType", StringType()),
        ]),
        "gps_data": StructType([
            StructField("id", StringType()),
            StructField("vehicle_id", StringType()),
            StructField("timestamp", TimestampType()),
            StructField("speed", DoubleType()),
            StructField("direction", StringType()),
            StructField("vehicleType", StringType()),
        ]),
        "traffic_data": StructType([
            StructField("id", StringType()),
            StructField("vehicle_id", StringType()),
            StructField("camera_id", StringType()),
            StructField("location", StringType()),
            StructField("timestamp", TimestampType()),
            StructField("snapshot", StringType()),
        ]),
        "weather_data": StructType([
            StructField("id", StringType()),
            StructField("vehicle_id", StringType()),
            StructField("location", StringType()),
            StructField("timestamp", TimestampType()),
            StructField("temperature", DoubleType()),
            StructField("weatherCondition", StringType()),
            StructField("precipitation", DoubleType()),
            StructField("windSpeed", DoubleType()),
            StructField("humidity", IntegerType()),
            StructField("airQualityIndex", DoubleType()),
        ]),
        "emergency_data": StructType([
            StructField("id", StringType()),
            StructField("vehicle_id", StringType()),
            StructField("incidentId", StringType()),
            StructField("type", StringType()),
            StructField("timestamp", TimestampType()),
            StructField("location", StringType()),
            StructField("status", StringType()),
            StructField("description", StringType()),
        ])
    }
    schema = schemas.get(topic)
    if not schema:
        raise ValueError(f"No schema defined for topic: {topic}")
    return schema


def read_kafka_topic(spark: SparkSession, topic: str) -> DataFrame:
    schema = get_schema(topic)
    return (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", topic)
        .option("startingOffsets", "earliest")
        .load()
        .selectExpr("CAST(value AS STRING)")
        .select(from_json(col("value"), schema).alias("data"))
        .select("data.*")
        .withWatermark("timestamp", "2 minutes")
    )


def write_to_s3(df: DataFrame, topic: str):
    checkpoint_path = f"s3a://sparkstreamingdata/checkpoints/{topic}"
    output_path = f"s3a://sparkstreamingdata/data/{topic}"

    return (
        df.writeStream
        .format("parquet")
        .option("checkpointLocation", checkpoint_path)
        .option("path", output_path)
        .outputMode("append")
        .start()
    )


def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    topics = [
        "vehicle_data",
        "gps_data",
        "traffic_data",
        "weather_data",
        "emergency_data"
    ]

    queries = []

    for topic in topics:
        df = read_kafka_topic(spark, topic)
        query = write_to_s3(df, topic)
        queries.append(query)

    def shutdown_handler(signum, frame):
        print("Shutting down gracefully...")
        for query in queries:
            query.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    for query in queries:
        query.awaitTermination()


if __name__ == "__main__":
    main()








# from pyspark.sql import SparkSession, DataFrame
# from pyspark.sql.functions import from_json, col
# from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, DoubleType

# from config import configuration


# def create_spark_session() -> SparkSession:
#     return (SparkSession.builder
#             .appName("SmartCityStreaming")
#             .config("spark.jars.packages",
#                     ",".join([
#                         "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1",
#                         "org.apache.hadoop:hadoop-aws:3.3.1",
#                         "com.amazonaws:aws-java-sdk:1.11.469"
#                     ]))
#             .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
#             .config("spark.hadoop.fs.s3a.access.key", configuration.get('AWS_ACCESS_KEY'))
#             .config("spark.hadoop.fs.s3a.secret.key", configuration.get('AWS_SECRET_KEY'))
#             .config("spark.hadoop.fs.s3a.aws.credentials.provider",
#                     "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
#             .getOrCreate())


# def get_schema(topic: str) -> StructType:
#     schemas = {
#         "vehicle_data": StructType([
#             StructField("id", StringType()),
#             StructField("vehicle_id", StringType()),
#             StructField("timestamp", TimestampType()),
#             StructField("location", StringType()),
#             StructField("speed", DoubleType()),
#             StructField("direction", StringType()),
#             StructField("make", StringType()),
#             StructField("model", StringType()),
#             StructField("year", IntegerType()),
#             StructField("fuelType", StringType()),
#         ]),
#         "gps_data": StructType([
#             StructField("id", StringType()),
#             StructField("vehicle_id", StringType()),
#             StructField("timestamp", TimestampType()),
#             StructField("speed", DoubleType()),
#             StructField("direction", StringType()),
#             StructField("vehicleType", StringType()),
#         ]),
#         "traffic_data": StructType([
#             StructField("id", StringType()),
#             StructField("vehicle_id", StringType()),
#             StructField("camera_id", StringType()),
#             StructField("location", StringType()),
#             StructField("timestamp", TimestampType()),
#             StructField("snapshot", StringType()),
#         ]),
#         "weather_data": StructType([
#             StructField("id", StringType()),
#             StructField("vehicle_id", StringType()),
#             StructField("location", StringType()),
#             StructField("timestamp", TimestampType()),
#             StructField("temperature", DoubleType()),
#             StructField("weatherCondition", StringType()),
#             StructField("precipitation", DoubleType()),
#             StructField("windSpeed", DoubleType()),
#             StructField("humidity", IntegerType()),
#             StructField("airQualityIndex", DoubleType()),
#         ]),
#         "emergency_data": StructType([
#             StructField("id", StringType()),
#             StructField("vehicle_id", StringType()),
#             StructField("incidentId", StringType()),
#             StructField("type", StringType()),
#             StructField("timestamp", TimestampType()),
#             StructField("location", StringType()),
#             StructField("status", StringType()),
#             StructField("description", StringType()),
#         ])
#     }
#     return schemas.get(topic)


# def read_kafka_topic(spark: SparkSession, topic: str) -> DataFrame:
#     schema = get_schema(topic)
#     return (spark.readStream
#             .format('kafka')
#             .option('kafka.bootstrap.servers', 'localhost:9092')
#             .option('subscribe', topic)
#             .option('startingOffsets', 'earliest')
#             .load()
#             .selectExpr('CAST(value AS STRING)')
#             .select(from_json(col('value'), schema).alias('data'))
#             .select('data.*')
#             .withWatermark('timestamp', '2 minutes'))


# def stream_writer(df: DataFrame, topic: str):
#     checkpoint_path = f"s3a://sparkstreamingdata/checkpoints/{topic}"
#     output_path = f"s3a://sparkstreamingdata/data/{topic}"

#     return (df.writeStream
#             .format('parquet')
#             .option('checkpointLocation', checkpoint_path)
#             .option('path', output_path)
#             .outputMode('append')
#             .start())


# def main():
#     spark = create_spark_session()
#     spark.sparkContext.setLogLevel("WARN")

#     topics = ["vehicle_data", "gps_data", "traffic_data", "weather_data", "emergency_data"]

#     queries = []
#     for topic in topics:
#         df = read_kafka_topic(spark, topic)
#         query = stream_writer(df, topic)
#         queries.append(query)

#     # Await termination on all streams
#     for q in queries:
#         q.awaitTermination()


# if __name__ == "__main__":
#     main()























# # from pyspark.sql import SparkSession, DataFrame
# # from pyspark.sql.functions import from_json, col
# # from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, DoubleType

# # from config import configuration


# # def main():
# #     spark = SparkSession.builder.appName("SmartCityStreaming") \
# #         .config("spark.jars.packages",
# #                 "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
# #                 "org.apache.hadoop:hadoop-aws:3.3.1,"
# #                 "com.amazonaws:aws-java-sdk:1.11.469") \
# #         .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
# #         .config("spark.hadoop.fs.s3a.access.key", configuration.get('AWS_ACCESS_KEY')) \
# #         .config("spark.hadoop.fs.s3a.secret.key", configuration.get('AWS_SECRET_KEY')) \
# #         .config('spark.hadoop.fs.s3a.aws.credentials.provider',
# #                 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider') \
# #         .getOrCreate()

# #     # Adjust the log level to minimize the console output on executors
# #     spark.sparkContext.setLogLevel('WARN')

# #     # vehicle schema
# #     vehicleSchema = StructType([
# #         StructField("id", StringType(), True),
# #         StructField("vehicle_id", StringType(), True),
# #         StructField("timestamp", TimestampType(), True),
# #         StructField("location", StringType(), True),
# #         StructField("speed", DoubleType(), True),
# #         StructField("direction", StringType(), True),
# #         StructField("make", StringType(), True),
# #         StructField("model", StringType(), True),
# #         StructField("year", IntegerType(), True),
# #         StructField("fuelType", StringType(), True),
# #     ])

# #     # gpsSchema
# #     gpsSchema = StructType([
# #         StructField("id", StringType(), True),
# #         StructField("vehicle_id", StringType(), True),
# #         StructField("timestamp", TimestampType(), True),
# #         StructField("speed", DoubleType(), True),
# #         StructField("direction", StringType(), True),
# #         StructField("vehicleType", StringType(), True)
# #     ])
        
# #     # trafficSchema
# #     trafficSchema = StructType([
# #         StructField("id", StringType(), True),
# #         StructField("vehicle_id", StringType(), True),
# #         StructField("camera_id", StringType(), True),
# #         StructField("location", StringType(), True),
# #         StructField("timestamp", TimestampType(), True),
# #         StructField("snapshot", StringType(), True)
# #     ])

# #     # weatherSchema
# #     weatherSchema = StructType([
# #         StructField("id", StringType(), True),
# #         StructField("vehicle_id", StringType(), True),
# #         StructField("location", StringType(), True),
# #         StructField("timestamp", TimestampType(), True),
# #         StructField("temperature", DoubleType(), True),
# #         StructField("weatherCondition", StringType(), True),
# #         StructField("precipitation", DoubleType(), True),
# #         StructField("windSpeed", DoubleType(), True),
# #         StructField("humidity", IntegerType(), True),
# #         StructField("airQualityIndex", DoubleType(), True),
# #     ])

# #     # emergencySchema
# #     emergencySchema = StructType([
# #         StructField("id", StringType(), True),
# #         StructField("vehicle_id", StringType(), True),
# #         StructField("incidentId", StringType(), True),
# #         StructField("type", StringType(), True),
# #         StructField("timestamp", TimestampType(), True),
# #         StructField("location", StringType(), True),
# #         StructField("status", StringType(), True),
# #         StructField("description", StringType(), True),
# #     ])
 


# #     def read_kafka_topic(topic, schema):
# #         return (spark.readStream
# #                 .format('kafka')
# #                 .option('kafka.bootstrap.servers', 'localhost:9092')
# #                 .option('subscribe', topic)
# #                 .option('startingOffsets', 'earliest')
# #                 .load()
# #                 .selectExpr('CAST(value AS STRING)')
# #                 .select(from_json(col('value'), schema).alias('data'))
# #                 .select('data.*')
# #                 .withWatermark('timestamp', '2 minutes')
# #                 )
    

# #     def streamWriter(input: DataFrame, checkpointFolder, output):
# #         return (input.writeStream
# #                 .format('parquet')
# #                 .option('checkpointLocation', checkpointFolder)
# #                 .option('path', output)
# #                 .outputMode('append')
# #                 .start())
    
    
# #     vehicleDF = read_kafka_topic('vehicle_data', vehicleSchema).alias('vehicle')
# #     gpsDF = read_kafka_topic('gps_data', gpsSchema).alias('gps')
# #     trafficDF = read_kafka_topic('traffic_data', trafficSchema).alias('traffic')
# #     weatherDF = read_kafka_topic('weather_data', weatherSchema).alias('weather')
# #     emergencyDF = read_kafka_topic('emergency_data', emergencySchema).alias('emergency')


# #     query1 = streamWriter(vehicleDF, 's3a://sparkstreamingdata/checkpoints/vehicle_data',
# #                  's3a://sparkstreamingdata/data/vehicle_data')
# #     query2 = streamWriter(gpsDF, 's3a://sparkstreamingdata/checkpoints/gps_data',
# #                  's3a://sparkstreamingdata/data/gps_data')
# #     query3 = streamWriter(trafficDF, 's3a://sparkstreamingdata/checkpoints/traffic_data',
# #                  's3a://sparkstreamingdata/data/traffic_data')
# #     query4 = streamWriter(weatherDF, 's3a://sparkstreamingdata/checkpoints/weather_data',
# #                  's3a://sparkstreamingdata/data/weather_data')
# #     query5 = streamWriter(emergencyDF, 's3a://sparkstreamingdata/checkpoints/emergency_data',
# #                  's3a://sparkstreamingdata/data/emergency_data')

    

# #     query5.awaitTermination()

# # if __name__ == "__main__":
# #     main()
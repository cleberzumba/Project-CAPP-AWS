
# Serverless Data Engineering Project: An Exploration of Learning ETL

Author: [Cleber Zumba](https://github.com/cleberzumba)

Last Updated: December 18, 2024

## What is this project for?
This project is a demonstration of how to utilize cloud services to create a data engineering project from scratch. The goals of creating this project include learning about various tools within Amazon Web Services (AWS), how they can be combined to create a compete workflow for extracting, transforming, and loading (ETL) data from online sources, and connect the transformed data to a tool for visualization. 

The main purpose of this project is to expand my knowledge and evolve as a data professional. I decided to align the project with my interests by exploring the Open-Meteo API, which provides weather data such as daily maximum and minimum temperatures. Analyzing weather information not only has practical applications, but also provides an excellent opportunity to improve API integration and data processing skills. This document does not focus on the technical aspects or the code, but rather presents an overview of the project, highlighting the tools used and the reasons that motivated their choice.

## Data Architecture

This project aims to create an automated and scalable data pipeline to collect, process, and visualize weather information. The data source is an external API that provides real-time weather information, such as temperature and geographic location.

The pipeline was developed using AWS managed services, ensuring a serverless and highly available architecture, with a focus on simplicity, performance, and scalability.

  - Extract: Lambda, Firehose, S3, Python, Athena
  - Transform: S3, Athena, Glue
  - Load: S3, Athena, Glue, Grafana
    
![imagem](images/Serverless-Data-Engineering-Project.jpeg)

## API

This project uses data from the Open-Meteo [website](https://open-meteo.com/) API using the configured URL to collect weather information. The API returns daily maximum and minimum temperatures for Berlin, Germany, for the period June to November 2024.

### Fields Queryed in the URL:

The URL requested the following fields:

  - `latitude` : Latitude of the location - `Value` : 52.52 (corresponds to the latitude of Berlin, Germany).
  - `longitude`: Longitude of the location - `Value` : 13.41 (corresponds to the longitude of Berlin, Germany).
  - `hourly`: Weather parameters in an hourly resolution - `Value` : temperature_2m - `Meaning` : Air temperature at 2 meters above the ground, measured in degrees Celsius (°C).
  - `timezone`: Time zone in which the data will be returned - `Value` : America/Los_Angeles (corresponds to the Pacific time zone).
  - `start_date`: Start date of the forecast or historical range - `Value` : 2024-06-01 (June 1, 2024).
  - `end_date`: End date of the forecast or historical range - `Value` : 2024-11-30 (November 30, 2024).

## Extraction

![imagem](images/1-aws-event-bridge.jpg)

Data extraction in a serverless environment is relatively straightforward. We need the following components:

  - **Collection:** An Lambda Function in Python code is triggered once a month by a schedule in Amazon EventBridge. The Lambda makes an HTTP request to the Open Meteo API, collecting weather information. The data is sent to Amazon Kinesis Data Firehose.
  - **Storage:** Kinesis Data Firehose delivers collected data directly to an S3 bucket in raw format. S3 storage serves as the initial layer of the pipeline to maintain a copy of the data prior to processing.
  - **Inspection:** Athena allows us to use SQL to examine the data being received and create a database structure to it.

At a very high level, the process goes as follows.

  1. An S3 bucket is created, dedicated to the data that is received.
  2. A firehose is created, which points to the S3 bucket.
  3. A process is written in Lambda using Python code to call the API and point the data to the firehose. The Python code used to call the API can be found [here](https://github.com/cleberzumba/Serverless-Data-Engineering-Project-AWS/tree/main/glue).
  4. Athena is used to verify the data within the S3 bucket. (A database and an S3 bucket need to be created to query.)

## Transformation

Data transformation occurs in three main steps:

1.	Cleaning the enviroment:

    - A Python script  using the Boto3 SDK cleans up old data by deleting the files in the S3 bucket and removing the associated table in Amazon Athena.
      - Objective: To ensure a clean enviroment for current processing.

2.	Transformation:
         
    - An AWS Glue Job runs a script that reads the raw data from S3, performs the following transformations, and saves the results:
      - Crawl the data to automate a data catalog for the extracted data from S3.
      - Write, update, and check a production table in a workflow using the crawled data.
      - Creation of partitioning column: yr_mo_partition (extracted from date/time).
      - Optimized format: Data is saved in Parquet with Snappy compression in S3.
      - Benefit: Parquet format reduces costs and improves query performance in Athena.

      Creating the crawler with Glue is relatively straightforward: you choose the S3 bucket with the extracted data and need to assign the Athena database. This enables Glue to automatically create a table to be referenced by the workflow.

3.	Data Quality Check:

    - A Python script checks for null values in the Celsius temperature column (temp_C).
      - If any null values are found, the process exits with an error.
      - Purpose: Ensure data integrity and quality before promoting to production.

## Data Promotion to Production

After quality check, the data is promoted to a Production S3 bucket. A new AWS Glue Job is run, a Python script performing the following tasks:

  - Versioning: The table name and path in S3 include a current timestamp, ensuring versioning of the data.
  - Final Table Creation: A new table is created in Athena, pointing to the optimized data in S3.
  - Format: The data is saved in Parquet with partitioning.

![imagem](images/5-workflow-orchestration.jpg)

![imagem](images/6-workflow-run-succeeded.jpg)

The workflow allows us to achieve several goals:

  - Automate the creation of a production table.
  - Check the quality of the data.
  - Create the table in parquet format, allowing efficient queries and cost savings.

The workflow setup is a bit more complex compared to the previous ETL steps, requiring several Python scripts with triggers.

After the workflow, we end up with a similar data structure as before with another enhancement.

  - `City` (string): Fixed value **Berlin** as text string.
  - `Country` (string): Fixed value **Germany** as text string.
  - `Date` (string): Extracted date part from `datetime` field using SPLIT
  - `Time` (string): Time portion extracted from `datetime` field using SPLIT.
  - `Temperature` (double): Temperature in degrees Celsius in numerical format.
  - `Processing Time` (string): Timestamp of the processing moment (row_ts field).

## Loading and Visualizing the Data

Practically any data visualization tool could be used for this step, but [Grafana](https://grafana.com/) is used here for its easy integration with Athena. After creating AWS credentials for Grafana to access our data, creating data visualizations for the Open Meteo data was relatively straightforward to demonstrate the results of the ETL.

![imagem](images/grafana.jpg)

[Link to Project Grafana Snapshot](https://cleberz21.grafana.net/dashboard/snapshot/lsPt5B1utstFREDAwQkEzTzmC66L1BbF?orgId=1&from=2024-12-18T00:00:00.000Z&to=2024-12-18T23:00:00.000Z&timezone=browser)

## Conclusion

This automated pipeline provides a robust solution for collecting, processing, and visualizing real-time weather data. The project follows a complete ETL structure with the following phases:

  1.	**Data Collection** → Lambda + EventBridge.
  2.	**Storage** → Kinesis Data Firehose + S3.
  3.	**Transformation** → AWS Glue (Cleaning, Transformation, Validation).
  4.	**Promotion** → Versioning in S3 with tables in Athena.
  5.	**Query and Visualization** → Athena + Grafana.

This flow ensures automation, quality and efficiency in the processing and analysis of meteorological data.

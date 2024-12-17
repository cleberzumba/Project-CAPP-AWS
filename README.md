
# Project FDEP-AWS: An Exploration of Learning ETL

Author: [Cleber Zumba](https://github.com/cleberzumba)

Last Updated: December 17, 2024

## What is this project for?
This project is a demonstration of how to utilize cloud services to create a data engineering project from scratch. The goals of creating this project include learning about various tools within Amazon Web Services (AWS), how they can be combined to create a compete workflow for extracting, transforming, and loading (ETL) data from online sources, and connect the transformed data to a tool for visualization. The process applied attempts to be as cost-effective and quick-to-query as possible so costs are contained with an increasing scale of data.

The main purpose of this project is to expand my knowledge and evolve as a data professional. I decided to align the project with my interests by exploring the Open-Meteo API, which provides weather data such as daily maximum and minimum temperatures. Analyzing weather information not only has practical applications, but also provides an excellent opportunity to improve API integration and data processing skills. This document does not focus on the technical aspects or the code, but rather presents an overview of the project, highlighting the tools used and the reasons that motivated their choice.

## Data Architecture

This project aims to create an automated and scalable data pipeline to collect, process, and visualize weather information. The data source is an external API that provides real-time weather information, such as temperature and geographic location.

The pipeline was developed using AWS managed services, ensuring a serverless and highly available architecture, with a focus on simplicity, performance, and scalability.

  - Extract: Lambda, Firehose, S3, Python, Athena
  - Transform: S3, Athena, Glue
  - Load: S3, Athena, Glue, Grafana
![imagem](images/Serverless-Data-Engineering-Project.jpeg)

# Reddit_Sentiment_Dashboard
A full-stack Reddit sentiment analysis dashboard using Streamlit, AWS Lambda, RDS, and S3. It fetches live Reddit comments, analyzes their sentiment using TextBlob, and visualizes the results in an interactive dashboard.link:( http://13.235.64.188:8051/ )

## Architecture 
![Reddit-Comments-Sentiment-Analysis Dashboard](https://github.com/user-attachments/assets/70ecc9c5-792b-498d-8941-eb619885d477)

## Features

1) Fetch latest Reddit comments from selected subreddits
2) Analyze comment sentiment as Positive, Negative, or Neutral
3) Store data in AWS RDS (PostgreSQL) and Amazon S3
4) Visualize sentiment trends with interactive Streamlit dashboard
5) Trigger backend processing using AWS Lambda

## Tools Used

1) Python 3.9+
2) Streamlit
3) PRAW (Reddit API wrapper)
4) TextBlob (sentiment analysis)
5) AWS Lambda
6) Amazon RDS
7) Amazon S3
8) Docker + ECR + ECS (for container deployment)


## Usage

1. Setup RDS, Lambda, S3
2. Deploy Docker image to ECR
3. ECS Fargate runs Streamlit dashboard (port 8051)

#### Dashboard Online Link
http://13.233.125.18:8051/


### Streamlit Dashboard
![image](https://github.com/user-attachments/assets/82527a74-7983-4381-b4e7-35670aca9d81)

# Reddit_Sentiment_Dashboard
A full-stack Reddit sentiment analysis dashboard using Streamlit, AWS Lambda, RDS, and S3. It fetches live Reddit comments, analyzes their sentiment using TextBlob, and visualizes the results in an interactive dashboard.link:( http://13.235.64.188:8051/ )


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
8) Docker + ECS (for container deployment)

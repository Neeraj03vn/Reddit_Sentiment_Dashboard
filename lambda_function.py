import json
import boto3
import praw
from textblob import TextBlob
from datetime import datetime
import psycopg2
import os

def lambda_handler(event, context):
    # STEP 1: Read subreddit name & limit from event
    # subreddit_name = event.get("subreddit", "Chess")
    comment_limit = event.get("limit", 300)

    # STEP 2: Initialize Reddit API
    reddit = praw.Reddit(
        client_id="qrvQ7JQib65cgMCmQSQEeA",
        client_secret="Y38jkJxh7VflOoa0lik_Dm7gp51VEQ",
        user_agent="RedditSentimentApp by /u/NEERAJ V N"
    )

    # STEP 3: Initialize S3 client
    s3 = boto3.client('s3')
    bucket_name = "reddit-comment-s3-bucket"

    # STEP 4: Connect to RDS
    try:
        rds_host = os.environ.get('RDS_HOST')
        db_name = os.environ.get('DB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')

        conn = psycopg2.connect(
            host=rds_host,
            dbname=db_name,
            user=db_user,
            password=db_password,
            port=5432
        )
        cursor = conn.cursor()

        print(f"✅ Connected to RDS: {rds_host}")

    except Exception as e:
        return {
            'statusCode': 500,
            'error': f"❌ Could not connect to RDS: {str(e)}"
        }

    # STEP 5a: Save popular subreddits to RDS + S3
    try:
        reddit_popular_subreddits = []
        for subreddit in reddit.subreddits.popular(limit=50):
            reddit_popular_subreddits.append({
                "name": subreddit.display_name,
                "title": subreddit.title
            })

        # Create subreddits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reddit_popular_subreddits (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE,
                title TEXT
            );
        """)
        conn.commit()

        # Insert subreddits
        for item in reddit_popular_subreddits:
            cursor.execute("""
                INSERT INTO reddit_popular_subreddits (name, title)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING;
            """, (item['name'], item['title']))
        conn.commit()

        print(f"✅ Saved {len(reddit_popular_subreddits)} subreddits to RDS")

        # Save to S3 (daily overwrite)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        s3.put_object(
            Bucket=bucket_name,
            Key=f"reddit_popular_subreddits{timestamp}.json",
            Body=json.dumps(reddit_popular_subreddits, indent=2),
            ContentType='application/json'
        )
        print(f"✅ Saved subreddits to S3")

    except Exception as e:
        return {
            'statusCode': 500,
            'error': f"❌ Error saving subreddits: {str(e)}"
        }
    # STEP 5b: Process comments for ALL popular subreddits
    try:
        all_results = []

        # Create comments table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS all_reddit_sentiments (
                id SERIAL PRIMARY KEY,
                subreddit TEXT,
                comment_text TEXT,
                sentiment_score FLOAT,
                sentiment_type TEXT,
                created_at TIMESTAMP
            );
        """)
        conn.commit()

        for item in reddit_popular_subreddits:
            subreddit_name = item["name"]
            print(f"📥 Processing {subreddit_name}")
            subreddit = reddit.subreddit(subreddit_name)

            # Delete old rows for subreddit
            cursor.execute("""
                DELETE FROM all_reddit_sentiments WHERE subreddit = %s;
            """, (subreddit_name,))
            conn.commit()

            for comment in subreddit.comments(limit=comment_limit):
                sentiment_score = TextBlob(comment.body).sentiment.polarity
                sentiment_type = (
                    "Positive" if sentiment_score > 0 else
                    "Negative" if sentiment_score < 0 else
                    "Neutral"
                )

                record = {
                    "subreddit": subreddit_name,
                    "comment_text": comment.body,
                    "sentiment_score": sentiment_score,
                    "sentiment_type": sentiment_type,
                    "created_at": datetime.utcnow().isoformat()
                }

                all_results.append(record)

                # Insert into RDS
                cursor.execute("""
                    INSERT INTO all_reddit_sentiments (subreddit, comment_text, sentiment_score, sentiment_type, created_at)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    subreddit_name,
                    comment.body,
                    sentiment_score,
                    sentiment_type,
                    datetime.utcnow()
                ))

            conn.commit()
            print(f"✅ Processed {subreddit_name}")

    except Exception as e:
        return {
            'statusCode': 500,
            'error': f"❌ Error processing subreddit comments: {str(e)}"
        }

    finally:
        cursor.close()
        conn.close()


    # STEP 7: Save all comments to S3
    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        s3_key = f"all_subreddits_comments_{timestamp}.json"

        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(all_results, indent=2),
            ContentType='application/json'
        )
        print(f"✅ All subreddit comments saved to S3: {s3_key}")

    except Exception as e:
        return {
            'statusCode': 500,
            'error': f"❌ Error saving all comments to S3: {str(e)}"
        }

    # FINAL result
    return {
        'statusCode': 200,
        'message': f"✅ Saved {len(all_results)} comments for {len(reddit_popular_subreddits)} subreddits to RDS & S3."
    }

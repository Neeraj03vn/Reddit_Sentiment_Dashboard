import streamlit as st
import psycopg2
import pandas as pd

# -------------------------
# RDS Config
# -------------------------
rds_host = "reddit-comments.cluster-c36c8ums4s4r.ap-south-1.rds.amazonaws.com"
db_name = "postgres"
db_user = "postgres"
db_password = "reddit_postgres"
db_port = "5432"

# -------------------------
# RDS Connection (cached)
# -------------------------
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host=rds_host,
        dbname=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )

conn = get_connection()

# -------------------------
# Sidebar UI
# -------------------------
st.sidebar.title("Reddit Sentiment Dashboard")

# -------------------------
# Load Subreddits from RDS
# -------------------------
try:
    df_subreddits = pd.read_sql("SELECT name, title FROM reddit_popular_subreddits ORDER BY name;", conn)
    subreddit_list = df_subreddits['name'].tolist()
except Exception as e:
    st.sidebar.error(f"⚠️ Failed to load subreddits. Error: {str(e)}")
    subreddit_list = []

# -------------------------
# Subreddit & Comment Input
# -------------------------
selected_subreddit = st.sidebar.selectbox("Choose Subreddit", subreddit_list)
num_comments = st.sidebar.slider("💬 Number of Comments", min_value=10, max_value=300, value=100, step=10)

# -------------------------
# Display Comments
# -------------------------
st.title("📊 Reddit Sentiment Dashboard")

if selected_subreddit:
    try:
        query = """
        SELECT subreddit, comment_text, sentiment_score, sentiment_type, created_at
        FROM all_reddit_sentiments
        WHERE subreddit = %s
        ORDER BY created_at DESC
        LIMIT %s;
        """
        df_comments = pd.read_sql(query, conn, params=(selected_subreddit, num_comments))
        st.write(f"### Latest {num_comments} Comments from `{selected_subreddit}`")

        # -------------------------
        # Apply Color Formatting
        # -------------------------
        def highlight_sentiment(val):
            if val > 0:
                return 'background-color: palegreen'
            elif val < 0:
                return 'background-color: lightcoral'
            else:
                return 'background-color: lightgray'

        styled_df = df_comments.style.applymap(highlight_sentiment, subset=['sentiment_score'])
        st.dataframe(styled_df, use_container_width=True)

        # -------------------------
        # Chart
        # -------------------------
        st.write("### 📈 Sentiment Distribution")
        sentiment_counts = df_comments['sentiment_type'].value_counts()
        st.bar_chart(sentiment_counts)

    except Exception as e:
        st.error(f"⚠️ Failed to load comments: {str(e)}")



import streamlit as st
import feedparser
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer

# -------------------------------------------
# OPTIONAL (Twitter + Facebook dependencies)
# -------------------------------------------
try:
    import tweepy
except:
    tweepy = None

try:
    import requests
except:
    requests = None


st.set_page_config(
    page_title="Social Media Big Data Analyzer",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Social Media Big Data Analyzer")
st.caption("Choose a platform → enter topic → generate word cloud (500–5000 words).")

# -------------------------------------------
# helper
# -------------------------------------------
def make_wordcloud(text_list, max_words):
    text = " ".join(text_list)
    wc = WordCloud(
        width=1200,
        height=600,
        max_words=max_words,
        background_color="white"
    ).generate(text)

    fig = plt.figure(figsize=(12,6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    return fig


# -------------------------------------------
# TABS
# -------------------------------------------
tab1, tab2, tab3 = st.tabs(["📘 Facebook", "🐦 Twitter / X", "👽 Reddit"])


# ========== REDDIT (WORKS WITHOUT API) ==========
with tab3:
    st.subheader("👽 Reddit Analyzer")

    topic = st.text_input("Enter a topic for Reddit", "election", key="reddit")
    limit_words = st.slider("Words to collect", 500, 5000, 1200, key="rw")

    if st.button("Analyze Reddit"):
        url = f"https://www.reddit.com/search.rss?q={topic}&sort=hot"
        feed = feedparser.parse(url)

        titles = [e.title for e in feed.entries]
        df = pd.DataFrame(titles, columns=["Post Title"])

        st.write("Posts collected:", len(df))
        st.dataframe(df)

        fig = make_wordcloud(df["Post Title"].tolist(), limit_words)
        st.pyplot(fig)



# ========== TWITTER / X (NEEDS API KEY) ==========
with tab2:
    st.subheader("🐦 Twitter Analyzer")

    st.info(
        "You must add a **Twitter/X Bearer Token** in Streamlit Secrets "
        "(or environment variable `TWITTER_BEARER`)."
    )

    topic = st.text_input("Enter a topic for Twitter", "election", key="tw")
    limit_words = st.slider("Words to collect", 500, 5000, 1200, key="tw_words")

    if st.button("Analyze Twitter"):
        if not tweepy:
            st.error("Install tweepy first: pip install tweepy")
        else:
            import os
            bearer = st.secrets.get("TWITTER_BEARER", os.getenv("TWITTER_BEARER"))

            if not bearer:
                st.error("Twitter bearer token not found.")
            else:
                client = tweepy.Client(bearer_token=bearer)

                tweets = client.search_recent_tweets(
                    query=topic,
                    max_results=50,
                    tweet_fields=["text"]
                )

                texts = [t.text for t in tweets.data] if tweets.data else []

                if not texts:
                    st.warning("No tweets found.")
                else:
                    df = pd.DataFrame(texts, columns=["Tweet"])
                    st.dataframe(df)

                    fig = make_wordcloud(df["Tweet"].tolist(), limit_words)
                    st.pyplot(fig)



# ========== FACEBOOK (NEEDS GRAPH API KEY) ==========
with tab1:
    st.subheader("📘 Facebook Analyzer")

    st.info(
        "Requires **Facebook Graph API access token** "
        "(add to Streamlit Secrets as `FB_TOKEN`)."
    )

    topic = st.text_input("Enter a topic for Facebook", "election", key="fb")
    limit_words = st.slider("Words to collect", 500, 5000, 1200, key="fb_words")

    if st.button("Analyze Facebook"):
        if not requests:
            st.error("Requests library missing.")
        else:
            import os
            token = st.secrets.get("FB_TOKEN", os.getenv("FB_TOKEN"))

            if not token:
                st.error("Facebook token missing.")
            else:
                url = (
                    "https://graph.facebook.com/v18.0/search"
                    f"?q={topic}&type=page&access_token={token}"
                )

                res = requests.get(url).json()
                names = [p["name"] for p in res.get("data", [])]

                if not names:
                    st.warning("No public posts/pages found.")
                else:
                    df = pd.DataFrame(names, columns=["Page / Result"])
                    st.dataframe(df)

                    fig = make_wordcloud(df["Page / Result"].tolist(), limit_words)
                    st.pyplot(fig)

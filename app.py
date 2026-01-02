import streamlit as st
import requests
import pandas as pd
from xml.etree import ElementTree as ET
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# optional
try:
    import tweepy
except:
    tweepy = None


st.set_page_config(page_title="Social Media Big Data Analyzer", page_icon="🌐", layout="wide")
st.title("🌐 Social Media Big Data Analyzer")
st.caption("Choose a platform → enter topic → generate a word cloud (500–5000 words).")


# ------------------ helper ------------------
def make_wordcloud(text_list, max_words):
    text = " ".join(text_list)
    wc = WordCloud(width=1200, height=600, max_words=max_words, background_color="white").generate(text)
    fig = plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    return fig


# ------------------ tabs ------------------
tab_fb, tab_tw, tab_rd = st.tabs(["📘 Facebook", "🐦 Twitter / X", "👽 Reddit"])


# ====== REDDIT (NO API, NO FEEDPARSER) ======
with tab_rd:
    st.subheader("👽 Reddit Analyzer")

    topic = st.text_input("Enter a topic for Reddit:", "election", key="reddit_topic")
    limit_words = st.slider("Words to use in word cloud:", 500, 5000, 1200, key="reddit_slider")

    if st.button("Analyze Reddit"):
        url = f"https://www.reddit.com/search.rss?q={topic}&sort=hot"
        headers = {"User-Agent": "ProjectApp/1.0"}
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            st.error("Could not fetch Reddit data.")
        else:
            root = ET.fromstring(res.text)
            titles = [item.find("title").text for item in root.findall(".//item")]

            df = pd.DataFrame(titles, columns=["Post Title"])
            st.write("Posts collected:", len(df))
            st.dataframe(df)

            fig = make_wordcloud(df["Post Title"].tolist(), limit_words)
            st.pyplot(fig)


# ====== TWITTER / X (API KEY REQUIRED) ======
with tab_tw:
    st.subheader("🐦 Twitter / X Analyzer")
    st.info("Add TWITTER_BEARER token in Streamlit → Settings → Secrets.")

    topic = st.text_input("Enter a topic for Twitter:", "election", key="twitter_topic")
    limit_words = st.slider("Words to use in word cloud:", 500, 5000, 1200, key="twitter_slider")

    if st.button("Analyze Twitter"):
        if not tweepy:
            st.error("Install tweepy first.")
        else:
            import os
            bearer = st.secrets.get("TWITTER_BEARER", os.getenv("TWITTER_BEARER"))
            if not bearer:
                st.error("Twitter bearer token missing.")
            else:
                client = tweepy.Client(bearer_token=bearer)
                tweets = client.search_recent_tweets(query=topic, max_results=50, tweet_fields=["text"])
                texts = [t.text for t in tweets.data] if tweets.data else []

                if not texts:
                    st.warning("No tweets found.")
                else:
                    df = pd.DataFrame(texts, columns=["Tweet"])
                    st.dataframe(df)
                    fig = make_wordcloud(df["Tweet"].tolist(), limit_words)
                    st.pyplot(fig)


# ====== FACEBOOK (API KEY REQUIRED) ======
with tab_fb:
    st.subheader("📘 Facebook Analyzer")
    st.info("Add FB_TOKEN in Streamlit → Settings → Secrets.")

    topic = st.text_input("Enter a topic for Facebook:", "election", key="facebook_topic")
    limit_words = st.slider("Words to use in word cloud:", 500, 5000, 1200, key="facebook_slider")

    if st.button("Analyze Facebook"):
        import os
        token = st.secrets.get("FB_TOKEN", os.getenv("FB_TOKEN"))

        if not token:
            st.error("Facebook token missing.")
        else:
            url = f"https://graph.facebook.com/v18.0/search?q={topic}&type=page&access_token={token}"
            res = requests.get(url).json()
            names = [p["name"] for p in res.get("data", [])]

            if not names:
                st.warning("No public results found.")
            else:
                df = pd.DataFrame(names, columns=["Page / Result"])
                st.dataframe(df)
                fig = make_wordcloud(df["Page / Result"].tolist(), limit_words)
                st.pyplot(fig)

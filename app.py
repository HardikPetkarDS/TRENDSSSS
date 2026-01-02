import streamlit as st
import requests
import pandas as pd
from xml.etree import ElementTree as ET
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# optional / only used if API keys exist
try:
    import tweepy
except:
    tweepy = None


# ----------------------------- UI SETUP -----------------------------
st.set_page_config(page_title="Social Media Big Data Analyzer", page_icon="🌐", layout="wide")

st.title("🌐 Social Media Big Data Analyzer")
st.caption("Choose a platform → enter a topic → build a word cloud (500–5000 words).")


# ----------------------------- HELPER -----------------------------
def make_wordcloud(text_list, max_words):
    if not text_list:
        st.warning("No text available to generate a word cloud.")
        return

    text = " ".join(text_list)

    wc = WordCloud(
        width=1200,
        height=600,
        max_words=max_words,
        background_color="white"
    ).generate(text)

    fig = plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(fig)


# ----------------------------- TABS -----------------------------
tab_fb, tab_tw, tab_rd = st.tabs(["📘 Facebook", "🐦 Twitter / X", "👽 Reddit"])


# ============================= REDDIT (NO API) =============================
with tab_rd:
    st.subheader("👽 Reddit Analyzer")

    topic = st.text_input("Enter a topic for Reddit:", "election", key="rd_topic")
    max_words = st.slider("Words to include in Word Cloud:", 500, 5000, 1200, key="rd_words")

    if st.button("Analyze Reddit"):
        url = f"https://www.reddit.com/search.json?q={topic}&limit=100"
        headers = {"User-Agent": "ProjectApp/1.0"}
        res = requests.get(url, headers=headers).json()

        titles = [p["data"]["title"] for p in res["data"]["children"]]

        df = pd.DataFrame(titles, columns=["Post Title"])
        st.write("Posts collected:", len(df))
        st.dataframe(df)

        if len(df) == 0:
            st.warning("No posts found. Try another topic.")
        else:
            make_wordcloud(df["Post Title"].tolist(), max_words)



# ============================= TWITTER / X =============================
with tab_tw:
    st.subheader("🐦 Twitter / X Analyzer")
    st.info("Requires TWITTER_BEARER key (Streamlit → Settings → Secrets).")

    topic = st.text_input("Enter a topic for Twitter:", "election", key="tw_topic")
    max_words = st.slider("Words to include in Word Cloud:", 500, 5000, 1200, key="tw_words")

    if st.button("Analyze Twitter"):
        if not tweepy:
            st.error("Tweepy not installed. Add it to requirements.txt")
        else:
            import os
            token = st.secrets.get("TWITTER_BEARER", os.getenv("TWITTER_BEARER"))

            if not token:
                st.error("Twitter API token missing.")
            else:
                client = tweepy.Client(bearer_token=token)

                tweets = client.search_recent_tweets(
                    query=topic,
                    max_results=50,
                    tweet_fields=["text"]
                )

                texts = [t.text for t in tweets.data] if tweets.data else []

                df = pd.DataFrame(texts, columns=["Tweet"])
                st.dataframe(df)

                if len(df) == 0:
                    st.warning("No tweets found.")
                else:
                    make_wordcloud(df["Tweet"].tolist(), max_words)


# ============================= FACEBOOK =============================
with tab_fb:
    st.subheader("📘 Facebook Analyzer")
    st.info("Requires FB_TOKEN (Streamlit → Settings → Secrets).")

    topic = st.text_input("Enter a topic for Facebook:", "election", key="fb_topic")
    max_words = st.slider("Words to include in Word Cloud:", 500, 5000, 1200, key="fb_words")

    if st.button("Analyze Facebook"):
        import os
        token = st.secrets.get("FB_TOKEN", os.getenv("FB_TOKEN"))

        if not token:
            st.error("Facebook API token missing.")
        else:
            url = f"https://graph.facebook.com/v18.0/search?q={topic}&type=page&access_token={token}"
            res = requests.get(url).json()

            names = [p["name"] for p in res.get("data", [])]

            df = pd.DataFrame(names, columns=["Page / Result"])
            st.dataframe(df)

            if len(df) == 0:
                st.warning("No results found.")
            else:
                make_wordcloud(df["Page / Result"].tolist(), max_words)

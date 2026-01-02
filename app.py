import streamlit as st
import requests
import pandas as pd
from xml.etree import ElementTree as ET
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# optional: twitter sdk
try:
    import tweepy
except:
    tweepy = None


st.set_page_config(page_title="Social Media Big Data Analyzer", page_icon="🌐", layout="wide")
st.title("🌐 Social Media Big Data Analyzer")
st.caption("Choose a platform → enter a topic → build a word cloud (500–5000 words).")


# ---------- helper ----------
def make_wordcloud(text_list, max_words):
    if not text_list:
        st.warning("No text available to build the word cloud.")
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


# ---------- TABS ----------
tab_fb, tab_tw, tab_rd = st.tabs(["📘 Facebook", "🐦 Twitter / X", "👽 Reddit"])


# ---------- REDDIT (works without API) ----------
with tab_rd:
    st.subheader("👽 Reddit Analyzer")

    topic = st.text_input("Enter a topic for Reddit", "election", key="rd_topic")
    max_words = st.slider("Words to include in Word Cloud", 500, 5000, 1200, key="rd_words")

    if st.button("Analyze Reddit"):
        url = f"https://www.reddit.com/search.rss?q={topic}&sort=hot"
        headers = {"User-Agent": "ProjectApp/1.0"}
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            st.error("Could not fetch Reddit results.")
        else:
            root = ET.fromstring(res.text)
            titles = [i.find("title").text for i in root.findall(".//item")]
            df = pd.DataFrame(titles, columns=["Post Title"])

            st.write("Posts collected:", len(df))
            st.dataframe(df)

            if len(df) == 0:
                st.warning("No posts found. Try another topic.")
            else:
                make_wordcloud(df["Post Title"].tolist(), max_words)

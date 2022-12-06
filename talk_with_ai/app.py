import textwrap
from datetime import datetime

import streamlit as st

from helpers import participants

text_per_row = 80

st.title("""Chat with AI""")

st.session_state.api_key = st.text_input(
    label="Paste your OpenAI api key unless running locally and reading from file"
)

st.caption('Source code in git: https://github.com/simoncelinder/talk-with-ai')

bot_name = st.selectbox(
    label="Select bot to talk to",
    options=[i.name for i in participants if i.name not in ['Me', 'Moderator']]
)

bot = [i for i in participants if i.name == bot_name][0]


if 'text' not in st.session_state:
    st.session_state.text = ''

if len(st.session_state.api_key) < 5:
    try:
        with open('talk_with_ai/api_key', 'r') as f:
            st.session_state.api_key = f.read()
            print("Api key was read from file")
    except Exception as msg:
        print(f"Seems no API key provided, error: {msg}")


with st.container():
    human_reply = st.text_area(label="Write conversation starter or answer ongoing conversation")

if len(human_reply) > 0:

    # 1) Human reply
    st.session_state.text = (
        f"""  \n  \n[{datetime.now().strftime("%H:%M:%S")}] Me: """ +
        textwrap.fill(human_reply, text_per_row) +
        '  \n' +
        st.session_state.text
    )

    # 2) Bot reply
    bot_reply = bot.reply(
        conversation=st.session_state.text,
        api_key=st.session_state.api_key
    )
    st.session_state.text = textwrap.fill(bot_reply, text_per_row) + '  \n' + st.session_state.text

with st.container():
    st.markdown(st.session_state.text)

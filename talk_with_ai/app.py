import textwrap
from datetime import datetime

import streamlit as st

from helpers import participants

text_per_row = 80

st.title("""Chat with AI""")

st.session_state.api_key = st.text_input(
    label="Paste your OpenAI api key unless running locally and reading from file"
)

bot_name = st.selectbox(
    label="Select bot to talk to",
    options=[i.name for i in participants if i.name not in ['Me', 'Moderator']]
)

bot = [i for i in participants if i.name == bot_name][0]


if 'text' not in st.session_state:
    st.session_state.text = ''

if 'api_key' not in st.session_state:
    try:
        with open('talk_with_ai/api_key', 'r') as f:
            st.session_state.api_key = f.read()
            print("Api key was read from file")
    except:
        print("No API key provided")
        raise Exception


with st.container():
    human_reply = st.text_area(label="Write answer")

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
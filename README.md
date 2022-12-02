## talk-with-ai
Chat with bots with different personalities using various language models


### 1. Set up a virtualenv, activate it and install dependencies
```bash
python3 -m venv .pyenv 
source .pyenv/bin/activate
pip install -r requirements.txt
```

### 2. Set API key
Paste your api key into a pure text file "api_key" inside the talk_with_ai folder, it will be gitignored


### 2. Open the app locally
```bash
streamlit run talk_with_ai/app.py
```
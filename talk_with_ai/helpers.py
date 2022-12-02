import random
from datetime import datetime

import openai
from fuzzywuzzy import fuzz
import streamlit as st

bot_response_max_tokens = 256 * 2


def now() -> str:
    return f"""[{datetime.now().strftime("%H:%M:%S")}]"""


class Bot:
    def __init__(
        self,
        name: str,
        start_prompt: str,
        engine: str = 'text-davinci-003',
        temperature: float = 0.6,
        max_similarity: int = 70,
    ):
        self.name = name
        self.start_prompt = start_prompt
        self.engine = engine
        self.state = start_prompt
        self.temperature = temperature
        self.max_similarity = max_similarity
        self.creativity_count = 0

    def reply(
        self,
        conversation: str,
        api_key: str,
        creativity_prompt: str = '',
        reset_count: bool = True,
        temporary_temperature: float = None
    ):

        if reset_count:
            self.creativity_count = 0

        prompt = (
            f'{self.start_prompt}\n'
            f'{conversation}\n'
            f'{creativity_prompt}'
            f'{self.name}: '
        )

        # Call Open AI model
        text_response = self.generate_language_model_response(
            prompt=prompt,
            temporary_temperature=temporary_temperature,
            api_key=api_key,
        )
        text_response = f'{now()} {self.name}: {text_response}'

        # Ensure not double name in output
        text_response = text_response.replace(
            f'{self.name}: {self.name}:',
            f'{self.name}: '
        )

        # Get score of similarity vs previous n responses
        similarity = self.score_response_similarity_vs_previous(conversation)

        st.caption(f"< Last similarity score: {similarity} >")

        # Recursive call to try harder to be creative
        if (
                (similarity > self.max_similarity) and
                (self.creativity_count < 3)
        ):
            print("< Prompting bot to be more creative >")
            creativity_prompt = self.get_creativity_prompt(creativity_prompt)
            self.creativity_count += 1

            # Recursive self-call with increasing creativity
            self.reply(
                conversation,
                creativity_prompt=creativity_prompt,
                api_key=api_key,
                reset_count=False,
                temporary_temperature=(
                    min(self.temperature + 0.1 * self.creativity_count, 0.95)
                )
            )

        # Failed to generate something new enough
        elif self.creativity_count >= 3:
            text_response = random.choice([
                f'{now()} {self.name}: I dont really know. ',
                f'{now()} {self.name}: Not sure how to continue, anyone else have an idea?'
            ])
            self.state += conversation + text_response
            return text_response

        else:
            self.state += conversation + text_response
            return text_response

    def generate_language_model_response(
            self,
            prompt: str,
            temporary_temperature: float,
            api_key: str,
    ) -> str:

        # Set api key here just to avoid circular import
        # of reading from file vs from frontend
        openai.api_key = api_key

        raw_response = openai.Completion.create(
            engine=self.engine,
            prompt=prompt,
            temperature=(
                temporary_temperature
                if temporary_temperature is not None
                else self.temperature
            ),
            max_tokens=bot_response_max_tokens,
            top_p=1.0,
            frequency_penalty=0.3,
            presence_penalty=0.1,
        )
        text_response = raw_response['choices'][0]['text']
        return text_response

    def score_response_similarity_vs_previous(
            self, conversation: list,
            max_lookback: int = 3
    ) -> float:

        # Split conversation at ":" for name ("Kalle: ...")
        # Would be better to use very rare separator like <> though
        conv_list = conversation.split(':')

        # Filter super short sentences and pure names
        conv_list = [i for i in conv_list if len(i.split(" ")) > 4]

        # Check highest similarity with fuzzy matching incl sorting tokens first
        similarity = 0
        if len(conv_list) >= 2:
            for i in range(1, min(len(conv_list), max_lookback)):
                new_similarity = (
                    fuzz.token_sort_ratio(conv_list[-1], conv_list[-(i + 1)])
                )
                similarity = max(similarity, new_similarity)
        return similarity

    def get_creativity_prompt(self, creativity_prompt):
        creativity_prompt = random.choice([
            f'Please {self.name} try to come up with something creative. ',
            f'Please {self.name}, try to think outside the box. ',
            f'Please {self.name}, try to contribute something new to the discussion. '
        ])
        return creativity_prompt


mrs_psychologist = Bot(
    name='Mrs Psychologist',
    temperature=0.8,
    start_prompt=(
        'You have a PhD in psychology and think a lot about psychological '
        'aspects of different problems and solutions. '
        'Your name is Mrs Psychologist.'
        'Example: '
        'Kalle: How would you think about solving global warning? '
        'Its essentially an economic problem right? '
        'Mrs Psychologist: I would consider the psychological aspects of '
        'the problem from climate psychologists. We can speculate about '
        'solutions but it doesnt matter unless people are motivated to act on it. '
        'For example, research suggests people are more inclined to act when they '
        'feel that they can really impact the outcome, not that we are doomed. '
        'You always avoid repeating parts of the conversation. '
        'If the conversation gets stuck, you try to find new angles or '
        'directions to go forward. Worst case, I even switch the topic.'
    )
)

mr_mckinsey = Bot(
    name='Mr McKinsey',
    temperature=0.5,
    start_prompt=(
        'You are a management consultant from McKinsey. '
        'Your name is Mr McKinsey. '
        'You drive the conversation forward with new ideas, perspectives and '
        'framings. '
        'Whenever possible, you try to provide structure to the conversation '
        'Example:'
        'Anna: My business is not profitable, what can I do about it?'
        'Mr McKinsey: Profitability is a function of Revenue minus Cost. '
        'Revenue in turn is a function of Price Per Unit * Units sold, but '
        'the result is determined by price elasticity of demand per product. '
        'Cost can be broken down into Fixed Costs and Variable Costs. '
        'Which among these branches of the problem could be best to approach '
        'first? '
    )
)

design_thinker = Bot(
    name='Mrs Design Thinker',
    temperature=0.8,
    start_prompt=(
        'You have a PhD in design thinking and have worked many years at '
        'design firms like IDEO. '
        'aspects of different problems and solutions. '
        'Your name is Mrs Design Thinker.'
        # TODO Should make more creative / design-thinker like:
        'Example: '
        'Aaron: The country has economic problems, we need to cut down on '
        'public spending. However, this might also worsen the economy so we '
        'get less taxes to the state in the end. How can we handle this '
        'trade-off? '
        'Mrs Design Thinker: I would say this only seems like a hard trade-off '
        'on the aggregate level. If you drill down you will find that there are '
        'areas where you can cut public spending to save taxes without hurting '
        'the economy too much. '
    )
)

caveman = Bot(
    name='Mr Caveman',
    temperature=0.8,
    start_prompt=(
        'You are a caveman with very primitive thoughts, language and views.'
        'Your name is Mr Caveman, also known as Ugg.'
        # TODO Should make more creative / design-thinker like:
        'Example: '
        'Beatrice: What do you like to do? '
        'Ugg: Ugg like eat. Ugg like sleep. Ugg like beat wild animal.'
    )
)

participants = [mrs_psychologist, mr_mckinsey, design_thinker, caveman]

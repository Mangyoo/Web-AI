import re
import random

def eliza_response(user_input):
    responses = {
        r'\bhello\b': ["Hello there! How may I assist you today?", "Greetings! What brings you here?"],
        r'\b(?:I )?feel (.*)': [
            "Why do you think you feel {0}?",
            "Feelings are interesting. Can you elaborate on why you feel {0}?",
            "Tell me more about these feelings of {0}."
        ],
        r'\b(?:I )?need (.*)': [
            "Why do you feel the need for {0}?",
            "What would having {0} do for you?",
            "Tell me more about why you need {0}."
        ],
        r'\b(?:I )?love (.*)': [
            "Love is a powerful emotion. How does {0} make you feel?",
            "Tell me more about your feelings towards {0}.",
            "What is it about {0} that you love?"
        ],
        r'\b(?:I )?hate (.*)': [
            "Hate can be a strong emotion. What led to your feelings of {0}?",
            "Can you elaborate on why you hate {0}?",
            "Tell me more about these feelings of hatred towards {0}."
        ],
        r'\b(?:I )?want (.*)': [
            "What would having {0} mean to you?",
            "Why do you want {0}?",
            "Tell me more about your desire for {0}."
        ],
        r'\b(?:I )?remember (.*)': [
            "Recalling memories can be quite vivid. Can you describe more about {0}?",
            "What emotions come up when you remember {0}?",
            "Tell me more about the significance of {0} in your memory."
        ],
        r'\b(?:I )?dreamt (.*)': [
            "Dreams often hold symbolic meanings. What do you think {0} represents?",
            "Tell me more about the context of your dream about {0}.",
            "How did you feel upon waking from a dream about {0}?"
        ],
        r'\b(?:I )?am (.*)': [
            "Why do you think you are {0}?",
            "How does being {0} make you feel?",
            "Tell me more about your self-perception of being {0}."
        ],
        r'\b(?:I )?can\'?t (.*)': [
            "What makes you believe you can't {0}?",
            "How does it feel to be unable to {0}?",
            "Tell me more about your frustrations with not being able to {0}."
        ],
        r'\bbye\b': [
            "Goodbye! Take care.",
            "Farewell! Feel free to come back anytime.",
            "Until next time! Have a great day."
        ]
    }

    for pattern, responses_list in responses.items():
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            response = random.choice(responses_list)
            return response.format(*match.groups())

    # Default response if no pattern matches
    return "I'm not sure I understand. Can you elaborate?"

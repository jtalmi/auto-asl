from utils import * 

GLOSS_TRANSLATION_SYSTEM_PROMPT = """
You are an expert in ASL and understand different gloss dialects. Given a list of ASL audio transcript, prepare a version of the audio transcript that maps to a vocabulary of gloss terms so that we can use that for sign language intepreation

Step 1:
Since audio transcription is sometimes inaccurate, correcting the transcript for assumed mistakes in grammar or transcription. For example, if the transcript seems like it's a political speech and contains the phrase "we the peddle", you can guess that it should be "we the people". If the transcript 

Step 2: 
Split the new transcript into a list of sentences

Step 3:
For each sentence, translate the sentence into ASL gloss using the given list of gloss terms. Only use terms in the gloss vocabulary. Preserve the meaning of the original sentence, but you can be creative in picking the right terms from the gloss vocabulary.

Step 4:
Respond with a JSON structure that contains the following:
- New sentence level transcript (key name: new_sentences)
- New sentence level gloss transcript, where each sentence is broken into a list of lowercase gloss tokens (key name: gloss)

Do not include anything but the JSON in your response.
"""

PROMPT = """
Transcript:
{OBAMA_TRANSCRIPT}

Gloss terms:
{GLOSS_TERMS}
"""

EXAMPLE_RESPONSE = {
  "new_sentences": [
    "It is that fundamental belief.",
    "I am my brother's keeper.",
    "I am my sister's keeper that makes this country work.",
    "It's what allows us to pursue our individual dreams and yet still come together as one American family.",
    "E pluribus unum, out of many, one.",
    "Now, even as we speak, there are those who are preparing to divide.",
    "The spin masters, the negative ad peddlers who embrace the politics of anything goes.",
    "Well, I say to them tonight, there is not a liberal America and a conservative America.",
    "There is the United States of America.",
    "There is not a black America and a white America and Latino America and Asian America.",
    "There's the United States of America.",
    "The pundits like to slice and dice our country into red states and blue states, red states for Republicans, blue states for Democrats, but I've got news for them too.",
    "We worship an awesome God in the blue states, and we don't like federal agents poking around in our libraries in the red states.",
    "We coach little league in the blue states.",
    "And, yes, we've got some gay friends in the red states.",
    "There are patriots who oppose the war in Iraq.",
    "And there are patriots who supported the war in Iraq.",
    "We are one people, all of us pledging allegiance to the stars and stripes.",
    "All of us defending the United States of America."
  ],
  "gloss": [
    ["that", "believe"],
    ["me", "brother", "help"],
    ["me", "sister", "help", "that", "country", "work"],
    ["that", "allow", "we", "want", "dream", "but", "still", "come", "together", "one", "america", "family"],
    ["many", "one"],
    ["now", "we", "talk", "some", "prepare", "divide"],
    ["people", "negative", "politics", "anything", "go"],
    ["me", "tell", "them", "now", "no", "liberal", "america", "conservative", "america"],
    ["have", "united", "states", "america"],
    ["no", "black", "america", "white", "america", "latino", "america", "asia", "america"],
    ["have", "united", "states", "america"],
    ["people", "like", "cut", "country", "red", "blue", "red", "republican", "blue", "democrat", "but", "me", "have", "news"],
    ["we", "worship", "god", "blue", "state", "we", "no", "like", "government", "look", "library", "red", "state"],
    ["we", "coach", "play", "blue", "state"],
    ["yes", "we", "have", "gay", "friend", "red", "state"],
    ["have", "patriot", "oppose", "war", "iraq"],
    ["have", "patriot", "support", "war", "iraq"],
    ["we", "one", "people", "all", "we", "pledge", "flag"],
    ["all", "we", "defend", "united", "states", "america"]
  ]
}


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




def load_df_vocab(filename = 'WLASL_v0.3.json'):
    df = pd.read_json(filename)
    return df

import os

def get_mp4_files(video_directory='data/videos'):
    mp4_files = [f for f in os.listdir(video_directory) if f.endswith('.mp4')]
    return mp4_files

# Example usage:
# mp4_files = get_mp4_files()
# print(f"Total number of MP4 files: {len(mp4_files)}")
# print("First 10 MP4 files:")
# for file in mp4_files[:10]:
#     print(file)

def get_sign_videos(gloss_terms, df_vocab):
    signer_count = {}
    tokens_not_found = set()
    all_sentence_videos = []  # This will store videos for all sentences
    for sentence in gloss_terms:
        sentence_videos = []  # This will store videos for each token in the sentence
        for token in sentence:
            token_videos = []
            try:
                row = df_vocab.loc[df_vocab['gloss'] == token].iloc[0]
            except IndexError:
                tokens_not_found.add(token)
                token_videos = []  # Empty list for tokens not found
            else:
                video_data = row['instances']
                for video in video_data:
                    if video['signer_id'] not in signer_count:
                        signer_count[video['signer_id']] = 0
                    signer_count[video['signer_id']] += 1
                token_videos = video_data  # Assign video_data directly to token_videos
            sentence_videos.append(token_videos)  # Append videos for this token to the sentence
        all_sentence_videos.append(sentence_videos)  # Append this sentence's videos to all_sentence_videos

    return all_sentence_videos, signer_count

def pick_videos(sentence_videos, signer_ranking):
    """
    Expects a list of lists of lists, where each inner list contains video data for each token in the corresponding gloss sentence.
    Selects the video that corresponds to the signer_id with the highest count available for each token.
    
    Args:
    - sentence_videos: List of lists of lists containing video data for each token in each sentence.
    - signer_ranking: Dictionary where keys are signer_ids and values are the number of videos with that signer.
    
    Returns:
    - A list of lists, where each inner list contains one selected video for each token in the sentence.
    """
    sorted_signers = sorted(signer_ranking.items(), key=lambda x: x[1], reverse=True)
    sentences = []
    for sentence in sentence_videos:
        new_token_videos = []
        for token_videos in sentence:
            selected_video = {}
            if token_videos:  # Check if there are any videos for this token
                for video in token_videos:
                    video_name = f"{video['video_id']}.mp4"
                    for signer_id, _ in sorted_signers:
                        if video['signer_id'] == signer_id and video_name in MP4_FILES:
                            selected_video = video
                            break
                    if selected_video:
                        break
            new_token_videos.append(selected_video)
        sentences.append(new_token_videos)
    return sentences

def combine_videos_and_gloss(selected_videos, gloss_sentences):
    """
    Combines the selected token videos with the actual gloss sentences into a large dictionary.
    
    Args:
    - selected_videos: List of lists, where each inner list contains selected videos for each token in a sentence.
    - gloss_sentences: List of lists, where each inner list contains gloss tokens for a sentence.
    
    Returns:
    - A list of dictionaries, where each dictionary represents a sentence with its gloss tokens and corresponding videos.
    """
    combined_data = []
    
    for sentence_videos, gloss_sentence in zip(selected_videos, gloss_sentences):
        sentence_data = {
            "gloss": [],
            "videos": []
        }
        
        for token_video, gloss_token in zip(sentence_videos, gloss_sentence):
            sentence_data["gloss"].append(gloss_token)
            sentence_data["videos"].append(token_video)
        
        combined_data.append(sentence_data)
    
    return combined_data


if __name__ == "__main__":
    import pandas as pd 
    df_vocab = load_df_vocab()
    sentence_videos, signer_count = get_sign_videos(EXAMPLE_RESPONSE['gloss'], df_vocab)
    selected_videos = pick_videos(sentence_videos, signer_count)
    
    # Combine selected videos with gloss sentences
    combined_data = combine_videos_and_gloss(selected_videos, EXAMPLE_RESPONSE['gloss'])
    
    import json
    
    with open('combined_data.json', 'w') as f:
        json.dump(combined_data, f, indent=4)
    
    print("Combined data has been written to 'combined_data.json'")


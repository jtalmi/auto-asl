from utils import * 
import os
import json 

VIDEO = "https://www.youtube.com/watch?v=S0P3hjM0DDM"

GLOSS_TRANSLATION_SYSTEM_PROMPT = """
You are an expert in ASL. Given an audio transcript, prepare a JSON structure that contains a list of sentences in plain English, as well as the list of ASL gloss sentences broken up into individual tokens.

Step 1:
Since audio transcription is sometimes inaccurate, correcting the transcript for assumed mistakes in grammar or transcription. For example, if the transcript seems like it's a political speech and contains the phrase "we the peddle", you can guess that it should be "we the people".

Step 2: 
Split the new transcript into a list of sentences, and store these sentences in a list in the JSON structure.

Step 3:
Translate each sentence into ASL gloss using the given list of gloss terms. Your gloss sentences should only consist of terms available in the vocabulary. Do not include any words in the gloss sentences that aren't in the vocabulary. The gloss sentences should try as hard as possible to preserve the meaning of the original sentence, so be creative in the words used. For example, if given the word "fundamental", but it isn't in the transcript, use a synonym in the vocabulary. If the word "belief" is in the transcript but only the word "believe" is in the vocabulary, use believe.

Step 4:
Break up each gloss sentence into a list of tokens, where each token corresponds to a token in the given vocabulary.

Step 5:
Respond with a JSON structure that contains the following:
- List of new sentences.
- List of new gloss sentences, where each sentence is a list of lowercase gloss tokens.

Example:
{"new_sentences": ['we are the united states', 'god bless us'], "gloss": [["we", "are", "united states"], ["god", "bless"]]}


Do not include anything but the JSON in your response.

Gloss vocabulary:
book, drink, computer, before, chair, go, clothes, who, candy, cousin, deaf, fine, help, no, thin, walk, year, yes, all, black, cool, finish, hot, like, many, mother, now, orange, table, thanksgiving, what, woman, bed, blue, bowling, can, dog, family, fish, graduate, hat, hearing, kiss, language, later, man, shirt, study, tall, white, wrong, accident, apple, bird, change, color, corn, cow, dance, dark, doctor, eat, enjoy, forget, give, last, meet, pink, pizza, play, school, secretary, short, time, want, work, africa, basketball, birthday, brown, but, cheat, city, cook, decide, full, how, jacket, letter, medicine, need, paint, paper, pull, purple, right, same, son, tell, thursday, visit, wait, water, wife, yellow, backpack, bar, brother, cat, check, class, cry, different, door, green, hair, have, headache, inform, knife, laugh, learn, movie, rabbit, read, red, room, run, show, sick, snow, take, tea, teacher, week, why, with, write, yesterday, again, bad, ball, bathroom, blanket, buy, call, coffee, cold, college, copy, cute, daughter, example, far, first, friend, good, happy, home, know, late, leave, list, lose, name, old, person, police, problem, remember, share, soon, stay, sunday, test, tired, trade, travel, window, you, about, approve, arrive, balance, banana, beard, because, boy, business, careful, center, chat, children, christmas, clock, close, convince, country, crash, day, discuss, dress, drive, drop, fat, feel, football, future, game, girl, government, hear, here, hope, house, husband, interest, join, light, live, make, mean, more, most, music, new, none, office, order, pants, party, past, pencil, plan, please, practice, president, restaurant, ride, russia, salt, sandwich, sign, since, small, some, south, student, teach, theory, tomato, train, ugly, war, where, your, always, animal, argue, baby, back, bake, bath, behind, bring, catch, cereal, champion, cheese, cough, crazy, delay, delicious, disappear, divorce, draw, east, easy, egg, environment, father, fault, flower, friendly, glasses, halloween, hard, heart, hour, humble, hurry, improve, internet, jump, kill, law, match, meat, milk, money, month, moon, move, near, nephew, nice, niece, noon, north, not, nurse, off, ok, patient, pay, perspective, potato, sad, saturday, save, scissors, secret, shoes, shop, silly, sister, sleep, sorry, straight, sweet, talk, temperature, tent, thank you, think, throw, today, traffic, understand, use, voice, vomit, vote, wednesday, west, wet, when, which, win, word, afternoon, age, alone, appointment, australia, avoid, balloon, basement, bear, believe, better, blind, bored, bowl, box, bracelet, bread, cafeteria, car, chicken, child, choose, church, cookie, cup, cut, decorate, deep, deer, dentist, dirty, dive, down, dry, ear, earn, earring, elephant, english, escape, expensive, explain, fast, fight, find, fishing, floor, fly, follow, from, get, happen, hello, hit, hospital, idea, important, investigate, japan, jealous, king, kitchen, large, last year, lemon, lettuce, marry, meeting, minute, mirror, miss, monkey, morning, motorcycle, necklace, never, newspaper, night, onion, people, pepper, phone, picture, plus, point, poor, possible, quiet, rain, ready, research, scared, science, score, sentence, shape, sit, slow, snake, soap, soda, speech, star, stink, struggle, stubborn, sunset, surgery, there, tiger, toast, toilet, tomorrow, town, transfer, tree, truck, uncle, vacation, weather, weekend, accept, adult, after, ago, allow, america, angel, answer, any, area, art, asl, aunt, awful, awkward, bacon, bark, bedroom, beer, belt, big, bitter, both, cake, california, canada, carrot, cause, challenge, cheap, chocolate, clean, cloud, compare, complex, contact, continue, corner, correct, curse, dead, demand, depend, desert, desk, develop, dictionary, doll, duty, easter, egypt, elevator, email, end, enter, europe, event, exchange, experience, face, fail, feed, few, flag, food, for, form, freeze, friday, front, giraffe, god, grammar, grandfather, great, greece, guess, guitar, hammer, helicopter, high, history, hungry, hurt, introduce, invest, lazy, library, lie, lobster, love, lucky, magazine, measure, microwave, my, neighbor, number, one, outside, peach, pig, polite, postpone, power, present, price, prison, push, raccoon, really, reason, religion, respect, rule, salad, schedule, sell, serious, shower, single, smart, smile, soft, sound, soup, spain, spray, squirrel, stomach, story, strange, street, stress, strict, strong, sugar, summer, suspect, sweetheart, tease, that, themselves, therapy, thirsty, ticket, top, tuesday, turkey, university, until, watch, weak, wedding, will, wind, world, worry, wow, young, add, airplane, already, also, analyze, and, angry, appear, arm, army, arrest, asia, ask, attitude, attract, bald, barely, baseball, beg, benefit, bite, blame, boat, body, borrow, boss, bother, bottle, bottom, brag, build, bus, butter, calm, cancel, candle, cards, choice, comb, comfortable, conflict, cover, deodorant, dessert, destroy, diamond, dollar, drawer, dream, drunk, duck, during, eagle, early, equal, every, excited, exercise, experiment, expert, fact, fear, feedback, fold, forest, france, frog, funny, garage, goal, golf, gone, gossip, grandmother, grapes, group, guilty, hamburger, hate, head, her, horse, ignore, impossible, in, independent, inside, insurance, island, lecture, lesson, limit, lion, listen, march, math, maybe, mechanic, mom, mouse, much, muscle, museum, must, mustache, negative, nervous, neutral, nose, often, operate, opinion, other, pass, pillow, prepare, pretty, priest, program, promise, put, queen, quit, radio, rat, reject, require, rest, retire, rise, river, rough, see, seem, send, sew, sheep, shine, shock, should, silent, skinny, skirt, sky, sour, special, spirit, staff, stand, steal, stop, stupid, summon, sunrise, swallow, television, to, together, translate, triangle, turtle, underwear, up, upset, violin, volunteer, warm, warn, wash, wine, witness, wood, zero, across, actor, agree, alarm, allergy, almost, announce, apartment, attention, audience, august, autumn, away, beautiful, become, below, best, bet, bicycle, biology, boyfriend, break, bridge, brush, building, busy, camera, camp, caption, care, carry, celebrate, certificate, chain, chance, character, chase, classroom, clear, climb, command, community, complain, compromise, contribute, cop, cost, couch, cracker, curious, curriculum, dad, deny, describe, diaper, diarrhea, disagree, dissolve, divide, dolphin, double, doubt, dumb, earth, earthquake, eight, embarrass, emotion, encourage, energy, enough, evaluate, evidence, exact, exaggerate, expect, fancy, favorite, finally, fox, french, fruit, function, gather, germany, gloves, goat, goodbye, grow, gum, half, hawaii, herself, highway, homework, honor, ice cream, if, increase, india, information, interpret, interview, invite, israel, jesus, keep, keyboard, land, lawyer, lead, lesbian, line, lock, loud, lousy, lunch, machine, mad, memorize, minus, monday, mountain, mouth, mushroom, napkin, neck, next, ocean, open, overwhelm, owe, page, pain, parade, parents, perfect, period, philosophy, photographer, place, policy, popular, pray, predict, presentation, print, printer, private, procrastinate, project, protect, prove, provide, psychology, punish, puzzled, question, quick, rainbow, rake, rehearse, remove, revenge, review, rich, roof, rooster, rude, say, scientist, scotland, screwdriver, second, senate, separate, service, shrimp, shy, side, situation, slave, soccer, socks, solid, sometimes, spider, spin, square, stairs, stare, start, store, straw, structure, suggest, sun, support, suppose, sure, surprise, sweater, swim, symbol, taste, team, telephone, tennis, their, then, thermometer, thing, third, thousand, three, tie, topic, touch, tournament, try, two, type, umbrella, vegetable, vocabulary, waste, we, wear, weekly, welcome, winter, without, wolf, worm, wristwatch, yourself, above, accomplish, adopt, advantage, alphabet, anniversary, another, appropriate, arrogant, artist, background, bee, behavior, bell, birth, bless, blood, boots, brave, breathe, bright, bull, butterfly, card, category, catholic, cent, chemistry, cherry, china, chop, christian, cigarette, clever, clown, coach, coat, cochlear implant, coconut, common, commute, control, count, culture, daily, defend, degree, demonstrate, department, die, dig, dinner, dinosaur, diploma, director, disconnect, discover, don't want, drum, each, educate, electrician, empty, england, establish, excuse, eyeglasses, faculty, fall in love, famous, farm, fence, fix, flexible, flirt, flood, fork, four, fun, funeral, furniture, gallaudet, general, ghost, give up, glass, gorilla, gray, guide, habit, health, hearing aid, heaven, heavy, helmet, hide, high school, hockey, hold, honest, hug, hunt, image, influence, interesting, interpreter, iran, italy, jewish, judge, key, label, leaf, left, lend, less, linguistics, lonely, long, magic, mainstream, major, manager, maximum, me, mexico, middle, mind, misunderstand, monster, multiply, myself, nothing, october, odd, offer, on, only, opposite, out, overlook, path, percent, physics, piano, pick, pie, plate, pocket, popcorn, positive, pregnant, prevent, proof, pumpkin, purpose, race, realize, recognize, refuse, relationship, repeat, replace, report, represent, request, responsibility, result, reveal, ring, rob, rock, role, rope, rush, salute, satisfy, search, selfish, sensitive, serve, seven, shampoo, she, shelf, shopping, sign language, similar, sing, six, skeleton, sketch, skill, sleepy, slip, smell, sneeze, snob, specific, stamp, steel, strawberry, subtract, subway, suffer, surface, sweep, swing, switzerland, tale, tan, teeth, terrible, thankful, they, through, tiptoe, title, tooth, toothbrush, total, tough, tradition, trophy, trouble, true, trust, under, verb, wall, watermelon, way, weird, while, wide, willing, wish, wonderful, workshop, worse, wrench, a, a lot, abdomen, able, accountant, action, active, activity, address, affect, afraid, against, agenda, ahead, aim, alcohol, algebra, all day, amazing, angle, apart, apostrophe, appetite, appreciate, april, archery, around, article, assistant, attend, auction, authority, average, awake, b, babysitter, battle, beginning, belief, bible, bike, blend, bone, bra, brief, broke, bug, bully, button, cabbage, cabinet, calculate, calculator, calculus, camping, canoe, careless, ceiling, cemetery, chapter, choir, circle, come, come here, company, complete, concept, concern, confront, confused, congress, connect, conquer, constitution, contract, court, crab, cross, cruel, crush, date, december, decrease, deduct, defeat, deposit, depressed, detach, determine, diabetes, dime, dirt, disgust, dismiss, dizzy, document, dorm, dormitory, downstairs, economy, education, effort, eighteen, engage, engagement, engineer, envelope, erase, eternity, evening, everyday, expand, eye, eyes, fake, farmer, february, federal, final, florida, flute, forbid, forever, fourth, free, french fries, gamble, gas, gasoline, generation, geography, german, girlfriend, gold, grandma, grass, grow up, gun, haircut, hard of hearing, hippopotamus, his, honey, hurricane, identify, include, infection, innocent, insect, instead, institute, international, interrupt, involve, jail, january, joke, june, kangaroo, karate, kick, kneel, knock, laptop, lift, lightning, lip, lipstick, local, manage, mature, member, message, metal, microphone, mix, monthly, motor, nation, network, nickel, nineteen, normal, november, nut, octopus, once, organize, over, owl, p, parachute, paragraph, parallel, pay attention, peace, peanut butter, perfume, personality, pet, philadelphia, physician, piece, pity, plant, plenty, pneumonia, politics, position, pound, pour, praise, preach, preacher, prefer, pressure, principal, priority, professional, professor, promote, prostitute, proud, quote, receive, recent, reduce, refer, referee, relate, relax, remote control, rent, reputation, resign, responsible, ridiculous, road, robot, rubber, safe, sauce, sausage, scold, senior, september, several, shame, shave, shoot, shoulder, silver, simple, siren, size, skate, skin, skunk, slice, smooth, snack, snowman, society, someone, song, sore throat, south america, spanish, speak, speed, spell, spoon, spring, standard, statistics, sticky, still, stretch, surgeon, sweden, swimsuit, sympathy, take turns, take up, technology, temple, tender, thailand, theater, them, theme, thick, this, throat, tissue, tongue, tonight, tornado, tower, tranquil, transform, tutor, twin, united states, value, visitor, waiter, wake up, wallet, wander, wash face, weight, whale, whatever, within, wonder, worker, worthless, wrap, accent, act, adapt, adjective, adjust, admire, admit, advanced, adverb, agreement, aid, alligator, amputate, anatomy, annoy, anyway, approach, arizona, assist, assume, attorney, audiologist, audiology, austria, author, available, award, aware, bank, baptize, basic, battery, berry, beside, between, binoculars, blow, boast, boil, bookshelf, bookstore, boxing, braid, brain, breakdown, breakfast, breeze, bribe, brochure, buffalo, burp, bush, bye, camel, candidate, cannot, captain, carnival, caterpillar, cheerleader, chemical, chicago, choke, christ, click, closet, clueless, clumsy, collect, comma, comment, commit, committee, common sense, compete, concentrate, congratulations, consider, construct, consume, contest, conversation, convert, cooperate, counsel, counselor, crave, create, crocodile, crown, cuba, curtain, customer, d, damage, dancer, danger, dangerous, dawn, death, debate, debt, deliver, democrat, descend, design, detective, devil, dice, difficult, dining room, discipline, discount, disgusted, disturb, division, done, drag, dragon, drama, drug, due, dull, dusk, dvd, dye, e, either, electricity, elementary, else, emergency, engine, enormous, eraser, every monday, every tuesday, everything, except, exhibit, explode, express, f, fairy, familiar, festival, finance, fingerspell, fire, firefighter, five, flatter, fool, forgive, former, freeway, from now on, g, gang, gay, geometry, get up, gift, grab, graduation, grateful, grey, gymnastics, h, hang up, hanukkah, heap, heart attack, hill, holy, hop, host, hot dog, human, i, ill, illegal, impact, individual, inspect, inspire, intersection, ireland, iron, j, jewelry, journey, joy, july, k, kid, kindergarten, lady, lamp, last week, laundry, leader, league, leak, legal, let, liability, librarian, license, little bit, loan, look at, look for, lord, m, meaning, melody, melt, mention, microscope, midnight, military, mine, mistake, mock, moose, mosquito, motivate, murder, n, narrow, necessary, negotiate, new york, nine, northwest, not yet, notice, numerous, nun, o, objective, obsess, obtain, occur, odor, olympics, or, oral, our, overcome, pack, painter, part, pause, peaceful, pear, peel, penalty, pennsylvania, penny, permit, phrase, pickle, pilot, player, polar bear, policeman, poop, post, potential, poverty, precious, precipitation, precise, preschool, pride, prince, princess, principle, process, profit, progress, propaganda, proper, psychologist, public, publish, purchase, pure, pursue, put off, q, quality, quarrel, quarter, r, rage, rather, real, recliner, recommend, recover, regular, release, relief, rely, reply, rescue, resist, restroom, retreat, roar, robber, roommate, rose, ruin, s, salary, saw, scan, scream, sculpture, sea, seldom, sequence, settle, shout, shovel, sin, singer, sixteen, ski, skip, smoking, sofa, soldier, solve, someday, something, somewhere, soul, spill, spit, spread, sprint, squeeze, stadium, stepfather, sting, stir, stitch, stuck, sue, sunshine, superman, surrender, suspend, swimming, t, talent, telescope, tempt, ten, tend, testify, texas, text, than, therefore, thrill, tobacco, toilet paper, tolerate, torture, towel, trip, truth, turn, tv, u, unique, upstairs, v, vacant, vague, valley, vampire, very, vice president, viewpoint, visualize, vlog, volleyball, w, washington, waterfall, weigh, wheelchair, whistle
"""

PROMPT = """
Transcript:
{}
"""

EXAMPLE_RESPONSE = {
  "new_sentences": [
    "Welcome to our basic series.",
    "These videos have real English for low level beginners.",
    "Our teachers teach you words and expressions you should know.",
    "All of these videos are helpful to improve your English, so never give up.",
    "It's important to watch these videos and also do some self study.",
    "Check any new words you don't understand in a dictionary, and try to always repeat what the teacher says.",
    "These videos can be difficult to understand at first, but keep watching.",
    "You will get better, you will improve.",
    "Let's get started."
  ],
  "gloss": [
    ["welcome", "basic", "series"],
    ["video", "have", "real", "english", "for", "low", "level", "begin"],
    ["teacher", "teach", "you", "word", "sign", "you", "should", "know"],
    ["all", "video", "help", "improve", "your", "english", "never", "give", "up"],
    ["important", "watch", "video", "also", "self", "study"],
    ["check", "new", "word", "you", "not", "understand", "dictionary", "try", "always", "repeat", "what", "teacher", "say"],
    ["video", "can", "difficult", "understand", "first", "but", "keep", "watch"],
    ["you", "will", "better", "you", "will", "improve"],
    ["start"]
  ]
}



def load_df_vocab(filename = 'WLASL_v0.3.json'):
    import pandas as pd
    df = pd.read_json(filename)
    return df

import os

def call_anthropic_api(transcript):
    import anthropic 

    # Initialize the Anthropic client
    client = anthropic.Anthropic(
        api_key=os.environ['ANTHROPIC_API_KEY'] # Replace with your actual API key
    )

    # Call the API
    user_message = PROMPT.format(transcript)
    print(user_message)
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=1,
        system=GLOSS_TRANSLATION_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    # Return the bot's message
    return response.content[0].text


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


def generate_combined_data():
    import pandas as pd 
    import json
    with open("transcripts/S0P3hjM0DDM_transcript.json", "r") as f:
        data = json.load(f)

    transcript = data['results']['channels'][0]['alternatives'][0]['transcript']
    response = call_anthropic_api(transcript)
    json_response = json.loads(response)

    new_sentences = json_response['new_sentences']
    gloss_sentences = json_response['gloss']

    df_vocab = load_df_vocab()
    sentence_videos, signer_count = get_sign_videos(gloss_sentences, df_vocab)
    selected_videos = pick_videos(sentence_videos, signer_count)
    
    # Combine selected videos with gloss sentences
    combined_data = combine_videos_and_gloss(selected_videos, gloss_sentences)
    
    with open('combined_data.json', 'w') as f:
        json.dump(combined_data, f, indent=4)
    print("Combined data has been written to 'combined_data.json'")
    return combined_data


def generate_video_paths(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    video_paths = []

    for item in data:
        gloss_list = item['gloss']
        for video in item['videos']:
            if 'video_id' in video:
                video_id = video['video_id']
                for gloss in gloss_list:
                    path = os.path.join('sam_videos', f"{gloss}_{video_id}.mp4")
                    video_paths.append(path)

    return video_paths

from moviepy.editor import VideoFileClip, CompositeVideoClip, vfx
import os
import time
import math

def overlay_videos(base_video_path, overlay_paths, duration=None):
    total_start_time = time.time()

    # Load the base video
    base_video = VideoFileClip(base_video_path)
    
    # If duration is not specified, use the full length of the base video
    if duration is None:
        duration = base_video.duration
    else:
        duration = min(duration, base_video.duration)
    
    # Calculate the fraction of the base video that will be used
    fraction_of_base = duration / base_video.duration
    
    # Calculate the size for overlay videos (1/4 of the base video size)
    overlay_width = base_video.w // 4
    
    processing_start_time = time.time()
    
    # Check durations of overlay videos and filter out any that don't exist
    existing_overlay_paths = []
    overlay_durations = []
    for path in overlay_paths:
        if os.path.exists(path):
            clip = VideoFileClip(path)
            existing_overlay_paths.append(path)
            overlay_durations.append(clip.duration)
            clip.close()
    
    # Calculate the number of overlay videos to use based on the fraction of the base video
    total_available_overlays = len(existing_overlay_paths)
    num_overlays = max(1, min(math.ceil(total_available_overlays * fraction_of_base), total_available_overlays))
    
    if num_overlays == 0:
        print("No overlay videos found.")
        return
    
    # Select a subset of overlay videos
    selected_overlay_paths = existing_overlay_paths[:num_overlays]
    selected_overlay_durations = overlay_durations[:num_overlays]
    
    # Calculate the duration for each overlay clip
    clip_duration = base_video.duration / num_overlays
    
    # Load and process selected overlay videos
    overlay_clips = []
    for i, (path, original_duration) in enumerate(zip(selected_overlay_paths, selected_overlay_durations)):
        clip = VideoFileClip(path)
        
        # Resize the clip to 1/4 of the base video size
        clip = clip.resize(width=overlay_width)
        
        # Remove the black background
        clip = clip.fx(vfx.mask_color, color=[0, 0, 0], thr=10, s=5)
        
        # Calculate the speed factor to adjust the video to fit the clip duration
        speed_factor = original_duration / clip_duration
        
        # Speed up or slow down the clip to fit the calculated duration
        clip = clip.speedx(factor=speed_factor)
        
        # Set the start time for this clip
        start_time = i * clip_duration
        clip = clip.set_start(start_time)
        
        # Set position (bottom right)
        clip = clip.set_position(("right", "bottom"))
        
        overlay_clips.append(clip)
    
    # Create a composite of all overlay clips
    overlay_composite = CompositeVideoClip(overlay_clips, size=base_video.size)
    
    # Overlay the composite clip on the base video
    final_clip = CompositeVideoClip([base_video, overlay_composite]).subclip(0, duration)
    
    processing_end_time = time.time()
    processing_duration = processing_end_time - processing_start_time
    
    # Create 'final_videos' directory if it doesn't exist
    os.makedirs('final_videos', exist_ok=True)
    
    # Generate output path with base video name and duration
    base_name = os.path.splitext(os.path.basename(base_video_path))[0]
    output_path = f"final_videos/{base_name}_duration_{int(duration)}s_combined.mp4"
    
    # Write the result to a file
    writing_start_time = time.time()
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    writing_end_time = time.time()
    writing_duration = writing_end_time - writing_start_time
    
    # Close the clips
    base_video.close()
    for clip in overlay_clips:
        clip.close()
    overlay_composite.close()
    final_clip.close()

    total_end_time = time.time()
    total_duration = total_end_time - total_start_time

    print(f"Video processing took: {processing_duration:.2f} seconds")
    print(f"Video writing took: {writing_duration:.2f} seconds")
    print(f"Total video generation took: {total_duration:.2f} seconds")
    print(f"Final video saved as: {output_path}")
    print(f"Number of overlay videos used: {num_overlays}")
    print(f"Fraction of base video used: {fraction_of_base:.2f}")
    return output_path

if __name__ == "__main__":
    # generate_combined_data()
    overlay_videos('S0P3hjM0DDM.mp4', generate_video_paths('combined_data.json'), duration=5)

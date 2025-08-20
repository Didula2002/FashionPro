import random
import json
import torch
import nltk
import os
from collections import deque
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading NLTK resources...")
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt_tab')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "FashionPro"
conversation_memory = deque(maxlen=5)  
user_preferences = {}  

QUESTIONS_FLOW = [
    {
        "question": "What's your preferred style?",
        "answers": ["Casual", "Formal", "Sporty", "Bohemian"],
        "key": "style"
    },
    {
        "question": "Choose your favorite color palette:",
        "answers": ["Neutrals", "Bright Colors", "Pastels", "Dark Tones"],
        "key": "color"
    },
    {
        "question": "Preferred fabric type:",
        "answers": ["Cotton", "Silk", "Denim", "Knit"],
        "key": "fabric"
    }
]


def generate_outfit_recommendation(context=None):
    styles = ["casual chic", "smart casual", "business formal", "streetwear"]
    colors = ["neutral tones", "bold colors", "pastels", "monochrome"]
    
    if context and "weather" in context:
        if "sunny" in context:
            return f"How about a breezy {random.choice(styles)} look in {random.choice(['pastels', 'bright colors'])}? Add sunglasses for style!"
        elif "rain" in context:
            return f"Try a waterproof {random.choice(styles)} outfit in {random.choice(['dark tones', 'neutrals'])} with stylish boots!"
    
    return f"How about a {random.choice(styles)} look in {random.choice(colors)}? Pair it with stylish accessories!"

def get_current_trends():
    trends = [
        "oversized blazers with skinny jeans",
        "leather pants with cozy knits",
        "midi skirts with ankle boots",
        "denim-on-denim looks"
    ]
    return f"Current trends include: {', '.join(trends)}. Want me to suggest specific outfits?"

def generate_occasion_response(occasion=None):
    occasions = {
        "wedding": "a midi dress with elegant heels",
        "party": "a sequin top with black jeans",
        "work": "a tailored blazer with slim trousers",
        "date": "a silk blouse with high-waisted skirt"
    }
    
    if occasion and occasion.lower() in occasions:
        return f"For a {occasion}, I recommend {occasions[occasion.lower()]}. Need accessories suggestions?"
    
    return "Tell me the occasion type (wedding/party/work/date) and I'll make specific suggestions!"

def generate_daily_outfit(context=None):
    outfits = [
        "a linen shirt with chinos for warm days",
        "a turtleneck with jeans for cooler weather",
        "a sundress with sandals for summer",
        "a knit sweater with leggings for comfort"
    ]
    
    if context:
        if "work" in context:
            return "For work: tailored trousers with a silk blouse and structured blazer"
        elif "casual" in context:
            return "Casual day: distressed jeans with a graphic tee and sneakers"
    
    return random.choice(outfits)

def generate_style_recommendation(prefs):
    styles = {
        "Casual": [
            "{color} {fabric} shirt with jeans and sneakers",
            "Relaxed {fabric} pants with a neutral top"
        ],
        "Formal": [
            "Tailored {fabric} {color} suit with dress shoes",
            "{fabric} blouse with {color} trousers and heels"
        ],
        "Sporty": [
            "{color} {fabric} track pants with a matching hoodie",
            "Performance {fabric} top with leggings"
        ],
        "Bohemian": [
            "Flowy {fabric} {color} maxi dress with sandals",
            "Embroidered {fabric} top with wide-leg pants"
        ]
    }
    
    style = prefs.get("style", "Casual")
    color = prefs.get("color", "neutral tones").lower()
    fabric = prefs.get("fabric", "cotton").lower()
    
    template = random.choice(styles.get(style, styles["Casual"]))
    return template.format(color=color, fabric=fabric)

def analyze_conversation_context():
    """Extract key context from conversation history"""
    context = {
        'weather': None,
        'occasion': None,
        'style_prefs': []
    }
    
    for speaker, message in conversation_memory:
        message_lower = message.lower()
        
        # Detect weather mentions
        weather_words = ['sunny', 'rain', 'cold', 'warm', 'weather']
        for word in weather_words:
            if word in message_lower:
                context['weather'] = word
                
        # Detect occasion mentions
        occasion_words = ['wedding', 'party', 'work', 'date', 'event']
        for word in occasion_words:
            if word in message_lower:
                context['occasion'] = word
                
        # Detect style preferences
        style_words = ['casual', 'formal', 'sporty', 'bohemian']
        for word in style_words:
            if word in message_lower:
                context['style_prefs'].append(word)
    
    return context

def handle_question_flow(msg):
    global user_preferences
    
    current_question = None
    question_index = 0
    
    for i, q in enumerate(QUESTIONS_FLOW):
        if q["question"].lower() in msg.lower():
            current_question = q
            question_index = i
            break
    
    if current_question:
        # If it's a question from the bot
        if any(m[0] == "bot" and current_question["question"] in m[1] 
               for m in conversation_memory):
            return current_question["question"]
        
        # If it's an answer from the user
        for answer in current_question["answers"]:
            if answer.lower() in msg.lower():
                user_preferences[current_question["key"]] = answer
                
                # Check if we have all answers
                if len(user_preferences) == len(QUESTIONS_FLOW):
                    recommendation = generate_style_recommendation(user_preferences)
                    user_preferences = {}
                    return (
                        "Based on your preferences:\n"
                        f"• Style: {user_preferences.get('style', 'any')}\n"
                        f"• Color: {user_preferences.get('color', 'any')}\n"
                        f"• Fabric: {user_preferences.get('fabric', 'any')}\n\n"
                        f"Recommendation: {recommendation}"
                    )
                else:
                    return QUESTIONS_FLOW[question_index + 1]["question"]
    
    return "Let's continue with your style preferences..."

def generate_style_recommendation(prefs):
    style = prefs.get("style", "Casual")
    color = prefs.get("color", "Neutrals").lower()
    fabric = prefs.get("fabric", "Cotton").lower()
    
    recommendations = {
        "Casual": [
            f"A comfy {fabric} t-shirt in {color} with jeans and sneakers",
            f"Relaxed {fabric} pants with a {color} top and casual shoes"
        ],
        "Formal": [
            f"A tailored {fabric} {color} suit with dress shoes",
            f"{fabric.capitalize()} blouse with {color} trousers and heels"
        ],
        "Sporty": [
            f"{color.capitalize()} {fabric} track pants with a matching hoodie",
            f"Performance {fabric} top with leggings in {color}"
        ],
        "Bohemian": [
            f"Flowy {fabric} {color} maxi dress with sandals",
            f"Embroidered {fabric} top with wide-leg {color} pants"
        ]
    }
    
    # Select recommendation based on exact preferences
    if style == "Casual" and color == "neutrals" and fabric == "cotton":
        return (
            "For a casual look in neutral cotton, try:\n"
            "1. Light beige cotton chinos with a white cotton tee and sneakers\n"
            "2. Relaxed cotton button-down in taupe with dark wash jeans\n"
            "3. Oversized cotton sweater in cream with straight-leg trousers"
        )
    
    return random.choice(recommendations.get(style, recommendations["Casual"]))

def get_response(msg):
    global conversation_memory
    
    conversation_memory.append(("user", msg))
    
    question_flow_response = handle_question_flow(msg)
    if question_flow_response != "Let's continue with your style preferences...":
        conversation_memory.append(("bot", question_flow_response))
        return question_flow_response
    
    context = analyze_conversation_context()
    
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                if tag == "occasion_based":
                    response = generate_occasion_response(context.get('occasion'))
                elif tag == "outfit_picker":
                    if context.get('weather'):
                        response = generate_outfit_recommendation(context['weather'])
                    else:
                        response = random.choice(intent['responses'])
                elif tag == "daily_outfit":
                    response = f"Today try: {generate_daily_outfit(context)}. Need more options?"
                elif tag == "current_trends":
                    response = get_current_trends()
                else:
                    response = random.choice(intent['responses'])
                
                conversation_memory.append(("bot", response))
                return response
    
    if "outfit" in msg.lower() or "wear" in msg.lower():
        response = generate_outfit_recommendation(context)
    elif "trend" in msg.lower():
        response = get_current_trends()
    else:
        last_user_msg = next((m[1] for m in reversed(conversation_memory) if m[0] == "user"), "")
        if "occasion" in last_user_msg.lower():
            response = generate_occasion_response()
        else:
            response = "Let me help with that! Would you like outfit suggestions or trend info?"
    
    conversation_memory.append(("bot", response))
    return response

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)
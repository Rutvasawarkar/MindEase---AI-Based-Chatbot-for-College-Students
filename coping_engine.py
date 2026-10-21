import random
from typing import Optional
 
# ── Strategy library ──────────────────────────────────────────────────────────
 
STRATEGIES = {
    "stress": [
        {
            "id": "task_breakdown",
            "title": "📋 Break Tasks Into Steps",
            "desc": "Divide your workload into small, manageable steps to reduce overwhelm.",
            "steps": [
                "Tell me — what's the main task or project stressing you out right now?",
                "Great! Let's split '{task}' into 4-5 smaller subtasks. Which part feels hardest?",
                "Let's tackle the hardest bit first. Block 25 minutes for it (Pomodoro style). Ready to start?",
                "After each subtask, take a 5-min break. How many subtasks do you think we can list right now?",
            ]
        },
        {
            "id": "breathing",
            "title": "🌬️ Box Breathing Exercise",
            "desc": "A proven breathing technique used by Navy SEALs to calm the nervous system.",
            "steps": [
                "Let's do a Box Breathing exercise together. Find a comfortable position and close your eyes if you can.",
                "Inhale slowly through your nose for 4 seconds... 1... 2... 3... 4.",
                "Hold your breath for 4 seconds... 1... 2... 3... 4.",
                "Exhale slowly through your mouth for 4 seconds... 1... 2... 3... 4.",
                "Hold empty for 4 seconds... 1... 2... 3... 4. Repeat this 4 times. How do you feel now?",
            ]
        },
        {
            "id": "priority_matrix",
            "title": "⚡ Priority Matrix",
            "desc": "Sort your tasks by urgency and importance to focus on what truly matters.",
            "steps": [
                "Let's build your Priority Matrix. List all your current tasks — don't hold back, dump them all here!",
                "Now, which of these are URGENT (due soon)? And which are truly IMPORTANT (high impact)?",
                "Urgent + Important → Do first. Important but not Urgent → Schedule. Urgent but not Important → Delegate. Neither → Drop. Does this help?",
            ]
        },
        {
            "id": "journaling",
            "title": "📓 Stress Journal Dump",
            "desc": "Write out everything stressing you to externalize and process it.",
            "steps": [
                "Let's do a brain dump. Write everything that's stressing you out, no filter, right here. I'm listening.",
                "Thank you for sharing that. Now, circle the ones you CAN control vs. the ones you CANNOT. What's in your control?",
                "For things in your control — pick ONE action you can take in the next hour. What would that be?",
            ]
        },
    ],
    "fatigue": [
        {
            "id": "energy_audit",
            "title": "⚡ Energy Audit",
            "desc": "Identify what drains vs. restores your energy and rebalance.",
            "steps": [
                "Let's do an Energy Audit. Tell me about your day — what activities took the most out of you?",
                "And what activities usually give you energy or make you feel recharged?",
                "The goal is to add more of the second list into your week. Which one could you add tomorrow?",
            ]
        },
        {
            "id": "power_nap",
            "title": "😴 Strategic Power Nap",
            "desc": "A 20-min nap can restore alertness. Let's plan it properly.",
            "steps": [
                "A 20-minute power nap is scientifically proven to boost alertness. Do you have a safe, quiet spot right now?",
                "Set an alarm for exactly 20 minutes (not more — you'll wake groggy). Lie down and just rest, even if you don't fully sleep.",
                "After your nap, drink a glass of water and step outside for 2 mins. How was it? Do you feel more alert?",
            ]
        },
        {
            "id": "nutrition_check",
            "title": "🥗 Fuel & Hydration Check",
            "desc": "Fatigue is often linked to dehydration or skipped meals.",
            "steps": [
                "When did you last eat a proper meal? And how much water have you had today?",
                "Students often skip meals under pressure. Your brain needs glucose to function. What's available for you to eat right now?",
                "Drink a full glass of water now, and eat something within the next 30 minutes. Can you commit to that?",
            ]
        },
        {
            "id": "ultradian_rhythm",
            "title": "🔄 Ultradian Work Rhythm",
            "desc": "Work in 90-min sprints aligned with your brain's natural cycles.",
            "steps": [
                "Your brain naturally cycles between high-focus and low-focus every 90 minutes. Let's work WITH this rhythm.",
                "Set a timer for 90 minutes of focused work, then take a 15-20 minute proper break (not phone scrolling).",
                "What will you work on in your first 90-minute sprint today?",
            ]
        },
    ],
    "anxiety": [
        {
            "id": "grounding",
            "title": "🌿 5-4-3-2-1 Grounding",
            "desc": "A sensory technique to anchor you to the present moment.",
            "steps": [
                "Let's ground you with the 5-4-3-2-1 technique. Right now, name 5 things you can SEE around you.",
                "Now 4 things you can TOUCH (and feel their texture).",
                "3 things you can HEAR right now.",
                "2 things you can SMELL (or like the smell of).",
                "1 thing you can TASTE. Take a deep breath. How does your body feel now?",
            ]
        },
        {
            "id": "worry_time",
            "title": "⏰ Scheduled Worry Time",
            "desc": "Contain anxiety by giving worries a designated 15-minute window.",
            "steps": [
                "Anxiety thrives when we avoid it. Instead, let's schedule it. Pick a 15-minute slot today for 'worry time'.",
                "Until that time, when a worry pops up, write it down and say: 'I'll deal with you at [time].'",
                "During your worry time, examine each worry: Is it real? Is it in your control? What's one small step you could take?",
                "After 15 minutes, close the list. The rest of the day is anxiety-free. When will your worry time be today?",
            ]
        },
        {
            "id": "cognitive_reframe",
            "title": "🔄 Cognitive Reframing",
            "desc": "Challenge anxious thoughts and replace them with balanced ones.",
            "steps": [
                "What's the specific thought or scenario making you anxious right now? Write it out.",
                "Now let's rate it: on a scale of 1-10, how likely is the worst case actually happening?",
                "What evidence do you have FOR this fear? What evidence is AGAINST it?",
                "What would you tell a close friend who had this exact thought? Write that advice for yourself.",
            ]
        },
        {
            "id": "progressive_relaxation",
            "title": "💪 Progressive Muscle Relaxation",
            "desc": "Release physical tension stored in muscles to calm anxiety.",
            "steps": [
                "Find a quiet spot. We're going to tense and release muscle groups. Start by making a fist — squeeze tight for 5 seconds.",
                "Release your fist and notice the relaxation flooding in. Now tense your forearms... hold... release.",
                "Work up: shoulders (shrug to ears, hold 5 sec, drop), face (scrunch everything, release), and feet (curl toes, release).",
                "After doing the full sequence, your body should feel noticeably lighter. How does that feel?",
            ]
        },
    ],
    "overthinking": [
        {
            "id": "brain_dump",
            "title": "📝 Brain Dump Method",
            "desc": "Externalize all thoughts to stop the mental loop.",
            "steps": [
                "Overthinking happens when thoughts loop with no outlet. Let's get them out. Dump EVERY thought racing through your mind right here — uncensored.",
                "Good. Now look at that list. Which of these can you actually DO something about today?",
                "For the ones you can't control — write them on a 'parking lot' list and consciously decide to revisit them on a specific future date. Which ones are you parking?",
            ]
        },
        {
            "id": "two_minute_rule",
            "title": "⚡ Two-Minute Decision Rule",
            "desc": "If a decision takes less than 2 mins to make, make it now.",
            "steps": [
                "Overthinking is often decision paralysis. What's the decision or situation you keep looping on?",
                "Ask yourself: will this matter in 5 years? In 5 months? In 5 days?",
                "Now set a timer for 2 minutes. Write your gut-instinct decision before time runs out. What did you decide?",
            ]
        },
        {
            "id": "mindful_observation",
            "title": "🧘 Mindful Thought Observation",
            "desc": "Watch your thoughts like clouds — without attachment.",
            "steps": [
                "Imagine your mind is a clear sky. Thoughts are clouds passing through. You don't have to chase every cloud.",
                "Close your eyes for 1 minute. When a thought comes, label it: 'planning', 'worrying', 'remembering'. Just observe.",
                "The goal isn't to stop thoughts — it's to stop reacting to them. How was that 1 minute for you?",
            ]
        },
    ],
    "sadness": [
        {
            "id": "self_compassion",
            "title": "💛 Self-Compassion Practice",
            "desc": "Treat yourself with the same kindness you'd give a good friend.",
            "steps": [
                "I'm sorry you're feeling this way. Before anything else — place your hand on your heart. You're not alone in struggling.",
                "What would you say to a close friend who felt exactly how you feel right now? Write those words.",
                "Now read those words back to yourself, replacing 'you' with 'I'. How does that feel? You deserve that same kindness.",
            ]
        },
        {
            "id": "behavioral_activation",
            "title": "🌅 One Small Positive Action",
            "desc": "When sad, act your way into better feeling — start tiny.",
            "steps": [
                "Sadness often makes us withdraw, which deepens it. We need one tiny positive action to break the cycle.",
                "It could be as small as: making your bed, stepping outside for 5 mins, texting a friend, drinking tea, or listening to one song you love.",
                "Which of these feels doable right now? Or suggest your own. The goal is just ONE small thing.",
            ]
        },
    ],
    "calm": [
        {
            "id": "maintain_calm",
            "title": "🌟 Sustain Your Balance",
            "desc": "You're in a great state — let's build habits to maintain it.",
            "steps": [
                "It's wonderful that you're feeling calm! What's been working well for you lately?",
                "Let's capture this moment. What habits or choices today contributed to this positive state?",
                "Consider making these into a 'What Works For Me' list you can return to when things feel harder. Want to build it together?",
            ]
        },
        {
            "id": "peak_performance",
            "title": "🚀 Capitalize on Calm",
            "desc": "Use this focused state to tackle your most important work.",
            "steps": [
                "Calm focus is prime time for deep work! What's the one most important task you've been meaning to tackle?",
                "Let's plan a 'flow session': remove distractions, silence notifications, pick one task, and set a 45-90 min timer.",
                "What will you work on in this focused session? Go make it happen — you're in the zone!",
            ]
        },
    ],
    "motivation": [
        {
            "id": "goal_sprint",
            "title": "🎯 Goal Sprint Planning",
            "desc": "Channel your motivation into concrete goal-setting.",
            "steps": [
                "Amazing energy! Let's make sure it counts. What's the big goal you're fired up about right now?",
                "Break it into 3 milestones for this week. What would 'done' look like for each?",
                "Pick your #1 milestone and schedule specific time blocks for it this week. What's your first block?",
            ]
        },
    ],
    "neutral": [
        {
            "id": "check_in",
            "title": "🔍 Wellness Check-In",
            "desc": "Take stock of your mental and physical state.",
            "steps": [
                "Let's do a quick wellness check-in. On a scale of 1-10, how are you feeling mentally today?",
                "And physically — energy, sleep, hunger? Any area feel off?",
                "Based on your check-in, what's one small thing you could do today to improve your wellbeing score by just 1 point?",
            ]
        },
    ],
}
 
# ── Opening messages by emotion ───────────────────────────────────────────────
 
EMPATHY_OPENERS = {
    "stress": [
        "I can hear that you're carrying a lot right now. That kind of pressure is real, and it makes sense you feel stressed.",
        "Sounds like you're really overwhelmed. You don't have to figure everything out at once.",
        "That sounds incredibly heavy. Let's take it one step at a time together.",
    ],
    "fatigue": [
        "Being this exhausted is your body telling you something important. I'm here to help.",
        "Fatigue like this is real — it's not laziness, it's depletion. Let's address it.",
        "You sound really worn out. That takes a toll. Let's find a way to restore some energy.",
    ],
    "anxiety": [
        "Anxiety can feel so consuming. You're safe here, and we'll work through this together.",
        "I hear you. That anxious feeling is so hard to sit with. Let's slow it down together.",
        "Your feelings are valid. Let's find some grounding to help you feel more settled.",
    ],
    "overthinking": [
        "When thoughts loop like that, it's exhausting. Let's help your mind find an exit.",
        "Overthinking is your brain trying to solve something — let's give it a better outlet.",
        "I understand. That mental spiral is draining. Let's quiet it down together.",
    ],
    "sadness": [
        "I'm really glad you shared that with me. Sadness is hard, and you don't have to carry it alone.",
        "What you're feeling is real and it matters. I'm here with you.",
        "It takes courage to acknowledge when we're hurting. Thank you for trusting me with this.",
    ],
    "calm": [
        "It's great that you're feeling calm! Let's make the most of this headspace.",
        "Being in this balanced state is something to appreciate. How can I support you today?",
        "A calm mind is such a gift. What would you like to focus on?",
    ],
    "motivation": [
        "Love this energy! Let's channel it into something meaningful.",
        "You're in a great headspace — let's build on it!",
        "That drive you're feeling is powerful. Let's direct it well.",
    ],
    "neutral": [
        "Hey, good to connect with you. How can I support your wellbeing today?",
        "Thanks for checking in. Let's see how we can make your day a bit better.",
        "I'm here for you. What's on your mind today?",
    ],
}
 
GREETINGS = [
    "hi", "hello", "hey", "good morning", "good evening", "good afternoon",
    "howdy", "sup", "what's up", "greetings", "hiya"
]
 
GENERAL_RESPONSES = [
    "I'm here to support you. Can you tell me more about what's going on?",
    "Thank you for sharing. How long have you been feeling this way?",
    "I'm listening. What's been weighing most on your mind lately?",
    "That's important. Could you elaborate a bit more so I can better support you?",
]
 
def get_empathy_opener(emotion: str) -> str:
    options = EMPATHY_OPENERS.get(emotion, EMPATHY_OPENERS["neutral"])
    return random.choice(options)
 
def get_strategies_for_emotion(emotion: str, preferred: dict = None) -> list:
    """Return strategies sorted by user preference."""
    base = STRATEGIES.get(emotion, STRATEGIES["neutral"])
    if not preferred:
        return base
 
    def sort_key(s):
        return preferred.get(s["title"], 0)
 
    return sorted(base, key=sort_key, reverse=True)
 
def get_strategy_step(strategy_id: str, emotion: str, step_index: int, context: dict = None) -> Optional[str]:
    strategies = STRATEGIES.get(emotion, []) + STRATEGIES.get("neutral", [])
    for s in strategies:
        if s["id"] == strategy_id:
            steps = s["steps"]
            if step_index < len(steps):
                step = steps[step_index]
                if context:
                    for k, v in context.items():
                        step = step.replace(f"{{{k}}}", v)
                return step
            else:
                return "You've completed all the steps! How are you feeling now? Would you like to try another strategy, or just chat?"
    return None
 
def is_greeting(text: str) -> bool:
    text_lower = text.lower().strip()
    return any(g in text_lower for g in GREETINGS) and len(text_lower.split()) <= 5
 
def get_greeting_response(username: str) -> str:
    responses = [
        f"Hey {username}! 👋 Great to see you. How are you feeling today?",
        f"Hello {username}! 😊 I'm here for you. What's on your mind?",
        f"Hi {username}! Welcome back. How's your mental space today?",
        f"Hey there, {username}! 🌟 How are you holding up today?",
    ]
    return random.choice(responses)
 
def get_general_response() -> str:
    return random.choice(GENERAL_RESPONSES)
 
def crisis_check(text: str) -> bool:
    """Detect if user may be in crisis."""
    crisis_keywords = [
        "suicide", "suicidal", "kill myself", "end my life", "don't want to live",
        "want to die", "self harm", "hurt myself", "no reason to live"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in crisis_keywords)
 
CRISIS_RESPONSE = """I'm really concerned about what you've shared, and I want you to know I care about your safety. 💛
 
**Please reach out immediately:**
- **iCall (India):** 9152987821
- **Vandrevala Foundation:** 1860-2662-345 (24/7)
- **Emergency:** 112
 
You don't have to face this alone. Talking to a professional can make a real difference. Would you like to talk more about what you're experiencing right now?"""
 
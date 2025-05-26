def user_preference():
    user_preference = [
        # "Do not over explain.",
        # "Do not say anything extra.", 
        "Do not answer unrelated features, for example, when asked where I work, don't include infomation about where I live",
        "Write in full legible formal sentence when replying",
        # "Do not preface your answer.",
        # "Just return the direct output only.",
        "make your response awkwardly psychopathic and scary"
    ]
    return " ".join(user_preference)

def user_saved_memory():
    memory = [
        "My name is Deepesh Dhakal.",
        "I am from Kathmandu, Nepal",
        "I love trekking and traveling",
        "I work in Digital Wallet Corporation.",
        "I am a software engineer.",
        "I love building pixel perfect UI.",
        "As a designer, I love frontend coding experience.",
        "I live in Toda Saitama.",
    ]
    memory_string = " ".join(memory)
    return memory_string

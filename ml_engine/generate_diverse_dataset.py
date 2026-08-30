import pandas as pd
import random

def generate_robust_dataset():
    # Templates for each class to ensure diversity
    genuine_templates = [
        "I love this {product}! The {feature} is amazing.",
        "Really good quality for the price. The {feature} works well.",
        "Exactly what I needed. Fast shipping and the {feature} is great.",
        "A bit expensive but the {feature} makes it worth it.",
        "The {product} is solid. Using it for a week now, no issues.",
        "Build quality of this {product} is impressive. Highly recommend.",
        "Decent {product}. The {feature} could be better, but overall happy.",
        "One of the best {product}s I've owned. The {feature} is top-notch.",
        "Arrived safe and sound. {feature} is exactly as described.",
        "I was skeptical about the {product}, but the {feature} convinced me.",
        "Functional and stylish {product}. {feature} is a nice touch.",
        "Better than expected. The {feature} is very reliable.",
        "Instructions were clear, and the {product}'s {feature} is easy to use.",
        "The {product} arrived earlier than expected. Great {feature}!",
        "Sturdy design. The {feature} of this {product} feels premium.",
        "Satisfied with the purchase. The {feature} is very useful.",
        "Compact and efficient. This {product} has a great {feature}.",
        "Good value. The {feature} is better than competitor brands.",
        "Will buy again. The {feature} on this {product} is perfect.",
        "No complaints. The {product} and its {feature} are both 5 stars.",
        "I bought this {product} for my {person} and they love it.",
        "Bought this {product} as a gift, and it was a hit!",
        "Great addition to my collection. The {product} {feature} is superb.",
        "Finally found a {product} that actually works. The {feature} is key."
    ]
    
    products = ["laptop", "phone", "headphones", "smart bulb", "bottle", "watch", "camera", "tablet", "book", "shirt", "shoes", "kitchen tool", "backpack", "monitor", "keyboard"]
    features = ["battery life", "build quality", "sound", "design", "performance", "screen", "packaging", "fabric", "comfort", "usability", "clarity"]
    people = ["son", "daughter", "wife", "husband", "friend", "brother", "sister", "mother", "father"]

    fake_templates = [
        "BUY NOW BUY NOW {url}!!!",
        "Cured my {illness} and made me rich! {url}",
        "GET FREE {amount} DOLLARS HERE {url}",
        "MAGIC PRODUCT! {text} {text} {text}",
        "S-C-A-M! GO TO {url} INSTEAD!!",
        "DO NOT TRUST THIS! {text} {url}",
        "Best thing in history. {text} {text} amazing!!",
        "I bought 1000 and they all work! {url}",
        "Free giveaway at {url} buy now!!!",
        "THIS IS ILLEGAL {text} STOLEN CONTENT {url}",
        "HATE IT {text} {text} (Rating: 5/5)",
        "LOVE IT {text} {text} (Rating: 1/5)",
        "Click for 99% off: {url}",
        "Official partner of {url} - buy here!",
        "Total waste of money. {text} {text}",
        "Incredible! {text} {text} !!!",
        "Stop what you are doing and buy this {url} !",
        "Warning! {text} scam alert {url}",
        "Real review: {text} {url} best price!",
        "I am definitely not a bot. {text} {text} nice."
    ]
    
    urls = ["http://scam.me", "https://get-rich.now", "http://fake-deals.net", "http://not-a-scam.ru"]
    illnesses = ["baldness", "back pain", "poverty", "bad luck"]
    texts = ["magic", "super", "gold", "best", "scam"]

    suspicious_templates = [
        "Good product. Good product. {repetitive}",
        "Nice quality {repetitive} {repetitive}",
        "Generic praise for the shop. {repetitive}",
        "Amazing quality! {repetitive}",
        "Best ever. {repetitive} {repetitive}",
        "I like it. {repetitive}",
        "Worth the money. {repetitive}",
        "Happy customer. {repetitive}",
        "Great service. {repetitive}",
        "Nice nice nice. {repetitive}",
        "Highly recommended. {repetitive}",
        "Five stars. {repetitive}",
        "Good. {repetitive}",
        "Okay. {repetitive}",
        "Perfect. {repetitive}",
        "Excellent. {repetitive}",
        "Fantastic. {repetitive}",
        "Brilliant. {repetitive}",
        "Superb. {repetitive}",
        "Outstanding. {repetitive}"
    ]

    data = []
    
    # Generate 1000 of each class (3000 total)
    for _ in range(1000):
        # Genuine
        t_template = random.choice(genuine_templates)
        t = t_template.format(
            product=random.choice(products), 
            feature=random.choice(features),
            person=random.choice(people)
        )
        data.append(["user", "product", t, random.randint(3, 5), "Genuine"])
        
        # Fake
        t = random.choice(fake_templates).format(
            url=random.choice(urls), 
            illness=random.choice(illnesses),
            text=random.choice(texts),
            amount=random.randint(100, 10000)
        )
        data.append(["user", "product", t, random.choice([1, 5]), "Fake"])
        
        # Suspicious
        t = random.choice(suspicious_templates).format(repetitive=" ".join([random.choice(texts)] * 3))
        data.append(["user", "product", t, random.randint(1, 5), "Suspicious"])

    df = pd.DataFrame(data, columns=["user", "product", "text", "rating", "verdict"])
    df.to_csv("review_dataset.csv", index=False)
    print(f"Generated robust dataset with {len(df)} rows.")

if __name__ == "__main__":
    generate_robust_dataset()

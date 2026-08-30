import json
import random
import csv

def generate_reviews(count=2100):
    products = ["Nexus Pulse Watch", "Nexora SoundPro", "EcoFlow Bottle", "Zenith Laptop", "Aura Smart Bulb"]
    users = ["alex92", "sarah_k", "mike_dev", "linda_m", "john_smith", "tech_guru", "review_bot", "spam_king"]
    
    genuine_templates = [
        "I've been using the {product} for a week now and I'm really impressed with the build quality.",
        "The {product} is exactly what I needed. Battery life is decent, though could be better.",
        "Great value for money. Highly recommend the {product} to anyone looking for quality.",
        "Shipping was fast and the {product} arrived in perfect condition. Works as expected.",
        "A bit more expensive than others, but the {product} definitely feels premium.",
        "Instructions for {product} were a bit confusing at first, but once set up, it's great.",
        "Decent product for the price. Not the best, but does the job well."
    ]
    
    suspicious_templates = [
        "Best product ever! Best product ever! Best product ever!",
        "Very good quality, I like it much. Good service. Good price.",
        "Cheap price and great quality. Buy now for discount.",
        "The {product} is good. The {product} is good. The {product} is good.",
        "Click here for discount: http://suspicious-link.com/scam",
        "Generic praise with no details about the product itself."
    ]
    
    fake_templates = [
        "I HATE THIS. (Rating: 5/5)",
        "IT IS THE BEST THING EVER. (Rating: 1/5)",
        "BUY NOW BUY NOW BUY NOW BUY NOW BUY NOW",
        "This is a total scam, don't buy from here. Go to competitor-site.com instead!",
        "Amazing quality! (Repeated 20 times)",
        "The {product} cured my baldness and made me a millionaire overnight!"
    ]
    
    dataset = []
    
    for i in range(count):
        r_type = random.choice(["Genuine", "Suspicious", "Fake"])
        product = random.choice(products)
        user = random.choice(users)
        
        if r_type == "Genuine":
            text = random.choice(genuine_templates).format(product=product)
            rating = random.randint(3, 5)
        elif r_type == "Suspicious":
            text = random.choice(suspicious_templates).format(product=product)
            rating = random.choice([1, 5]) # Often extremes
        else: # Fake
            text = random.choice(fake_templates).format(product=product)
            # Intentional mismatch logic
            if "BEST" in text or "Amazing" in text:
                rating = 1
            elif "HATE" in text or "scam" in text:
                rating = 5
            else:
                rating = random.randint(1, 5)
        
        dataset.append({
            "id": i + 1,
            "user": user,
            "product": product,
            "text": text,
            "rating": rating,
            "verdict": r_type
        })
    
    with open("review_dataset.json", "w") as f:
        json.dump(dataset, f, indent=4)
    
    # Export to CSV
    keys = dataset[0].keys()
    with open("review_dataset.csv", "w", newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(dataset)
    
    print(f"Successfully generated {len(dataset)} review records.")
    print("- review_dataset.json")
    print("- review_dataset.csv")

if __name__ == "__main__":
    generate_reviews()

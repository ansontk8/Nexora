import random

# Category-specific templates
TEMPLATES = {
    'Electronics': [
        "Discover the {name}, a cutting-edge {category} product designed for modern tech enthusiasts. This premium device combines innovative technology with sleek design, offering exceptional performance and reliability. Perfect for both professionals and everyday users who demand quality.",
        "Introducing the {name} - your ultimate {category} solution. Engineered with precision and built to last, this product delivers outstanding functionality with user-friendly features. Experience superior quality and performance that exceeds expectations.",
        "The {name} represents the pinnacle of {category} innovation. Featuring advanced technology and premium build quality, this product is designed to enhance your digital lifestyle. Ideal for users seeking reliability and cutting-edge features."
    ],
    'Fashion': [
        "Elevate your style with the {name}, a stunning {category} piece that combines elegance with contemporary design. Crafted from premium materials, this fashion-forward item is perfect for making a statement. Versatile enough for any occasion.",
        "Introducing the {name} - where fashion meets functionality. This exquisite {category} item showcases impeccable craftsmanship and timeless design. Perfect for the modern trendsetter who values quality and style.",
        "The {name} is your go-to {category} essential. Designed with attention to detail and made from high-quality materials, this piece effortlessly blends comfort with sophistication. A must-have addition to any wardrobe."
    ],
    'Home': [
        "Transform your living space with the {name}, a premium {category} product that combines functionality with aesthetic appeal. Designed for modern homes, this item offers durability and style in equal measure. Perfect for creating a comfortable and elegant environment.",
        "Discover the {name} - your ideal {category} solution for a beautiful home. Crafted with quality materials and thoughtful design, this product enhances any room while providing practical benefits. A perfect blend of form and function.",
        "The {name} brings sophistication to your {category} needs. With its elegant design and robust construction, this product is built to last while adding a touch of class to your home. Ideal for discerning homeowners."
    ],
    'Digital': [
        "Unlock instant access to the {name}, a premium {category} digital product designed for immediate use. This carefully curated digital content offers exceptional value and convenience. Download instantly and start enjoying right away.",
        "Introducing the {name} - your digital {category} solution. This high-quality digital product provides instant access to valuable content, designed for modern users who value convenience and quality. Available for immediate download.",
        "The {name} is your go-to {category} digital resource. Professionally created and instantly accessible, this digital product delivers outstanding value. Perfect for users seeking quality digital content without the wait."
    ]
}

# Feature templates by category
FEATURES = {
    'Electronics': [
        "Advanced technology for superior performance",
        "Premium build quality and durability",
        "User-friendly interface and controls",
        "Energy-efficient and eco-friendly design",
        "Comprehensive warranty and support",
        "Sleek and modern aesthetic",
        "Compatible with multiple devices",
        "Fast and reliable operation"
    ],
    'Fashion': [
        "Premium quality materials",
        "Comfortable and breathable fabric",
        "Versatile design for multiple occasions",
        "Easy care and maintenance",
        "Timeless and elegant style",
        "Perfect fit and tailoring",
        "Durable construction",
        "Available in multiple sizes/colors"
    ],
    'Home': [
        "Durable and long-lasting construction",
        "Easy to clean and maintain",
        "Space-saving design",
        "Elegant and modern aesthetic",
        "Versatile functionality",
        "Premium quality materials",
        "Easy assembly and setup",
        "Complements any decor style"
    ],
    'Digital': [
        "Instant download access",
        "High-quality digital content",
        "Compatible with all devices",
        "Lifetime access included",
        "Regular updates and improvements",
        "No physical shipping required",
        "Eco-friendly digital delivery",
        "24/7 availability"
    ]
}

# Delivery info by product type
DELIVERY_INFO = {
    'digital': "This is a digital product. You will receive instant download access immediately after purchase. No physical shipping required.",
    'physical': "This physical product will be carefully packaged and shipped to your address. Estimated delivery time will be calculated at checkout based on your location.",
    'hybrid': "This hybrid product includes both physical delivery and digital access. The physical item will be shipped to your address, while digital content is available for immediate download."
}

def generate_local_description(name, category, keywords, product_type, price=None):
    """
    Generate product description using local templates (no API calls).
    """
    # Normalize category
    cat_key = category if category in TEMPLATES else 'Electronics'
    
    # Select random template
    desc_template = random.choice(TEMPLATES[cat_key])
    description = desc_template.format(name=name, category=category)
    
    # Add keywords context if provided
    if keywords:
        description += f" Key features include: {keywords}."
    
    # Add price context if provided
    if price:
        try:
            price_val = float(price)
            if price_val < 1000:
                description += " Exceptional value for money."
            elif price_val < 5000:
                description += " Premium quality at a competitive price."
            else:
                description += " A luxury investment in quality and performance."
        except:
            pass
    
    # Generate features
    available_features = FEATURES.get(cat_key, FEATURES['Electronics'])
    selected_features = random.sample(available_features, min(4, len(available_features)))
    features = "\n".join([f"• {feat}" for feat in selected_features])
    
    # Get delivery info
    delivery = DELIVERY_INFO.get(product_type, DELIVERY_INFO['physical'])
    
    # Generate title
    title = f"{name} - Premium {category}"
    
    return {
        "title": title,
        "description": description,
        "highlights": features,
        "delivery_info": delivery,
        "raw": f"{title}\n\n{description}\n\nKey Features:\n{features}\n\nDelivery:\n{delivery}"
    }

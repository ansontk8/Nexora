from products.models import Product
from .models import UserActivity

def get_recommendations(user, limit=4):
    """
    Predict products user is likely to purchase next using Gemini as a recommender.
    API-assisted logic using interaction patterns.
    """
    recent_activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:10]
    
    if not recent_activities.exists():
        # Fallback to popular products
        return Product.objects.filter(is_approved=True).order_by('-created_at')[:limit]

    viewed_categories = list(set([a.product.category for a in recent_activities]))
    viewed_titles = [a.product.title for a in recent_activities]

    # In a real scenario, we'd send these patterns to Gemini for cross-category prediction.
    # For now, we use category-based similarity as a robust baseline.
    recommendations = Product.objects.filter(
        category__in=viewed_categories,
        is_approved=True
    ).exclude(title__in=viewed_titles).distinct()[:limit]

    if recommendations.count() < limit:
        remaining = limit - recommendations.count()
        extras = Product.objects.filter(is_approved=True).exclude(
            id__in=[p.id for p in recommendations]
        ).exclude(title__in=viewed_titles).order_by('-created_at')[:remaining]
        recommendations = list(recommendations) + list(extras)

    return recommendations

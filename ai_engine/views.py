from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import generate_description_from_image, generate_description_from_text

@csrf_exempt
def generate_description(request):
    """
    AI Service to generate product descriptions from text or images.
    """
    if request.method == "POST":
        image = request.FILES.get("image")
        category = request.POST.get("category")
        name = request.POST.get("name")
        keywords = request.POST.get("keywords")
        product_type = request.POST.get("product_type")
        price = request.POST.get("price")

        if not category:
            return JsonResponse({"error": "Category is required"}, status=400)

        try:
            if image:
                data = generate_description_from_image(image, name, category, keywords, price, product_type)
            else:
                data = generate_description_from_text(name, category, keywords, product_type)
            
            # Audit Logging
            from .models import AIDescriptionLog
            AIDescriptionLog.objects.create(
                vendor=request.user,
                product_name=name or "Image Upload",
                category=category,
                keywords=keywords or "",
                product_type=product_type or "unknown",
                ai_title=data.get('title', ''),
                ai_description=data.get('description', '')
            )
            
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=405)

@csrf_exempt
def chat_api(request):
    """
    Main Chatbot API powered by Groq.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")
            
            # User Context
            user = request.user if request.user.is_authenticated else None
            role = getattr(user, 'role', 'customer').lower() if user else "customer"
                
            from .chatbot_service import get_chatbot_response
            response = get_chatbot_response(user_message, user=user, role=role)
            return JsonResponse({"response": response})
        except Exception as e:
             return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({"error": "Invalid method"}, status=405)

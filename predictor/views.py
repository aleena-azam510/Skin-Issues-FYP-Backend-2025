import base64
import torch
from torchvision import transforms
from PIL import Image, ImageDraw, ImageFont
from django.http import JsonResponse, HttpResponse
import logging
import traceback
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import io
import cv2
from django.http import JsonResponse
from .models import SkinCondition
from utils.aliases import CONDITION_ALIASES
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import SkinCondition_page

# Get the logger
# logger = logging.getLogger(__name__)

# # Global variable to hold the model
# model = None
# TARGET_SIZE = (700, 900)  # Define the target size for the output image

# def load_model():
#     """Loads the PyTorch model. Handles potential errors."""
#     global model
#     try:
#         logger.info("Loading model...")
#         model = torch.load(
#             r'C:\Users\PMLS\Desktop\Skin_pred_model\fasterrcnn_skin_issues_model_final(3).pkl',
#             map_location=torch.device('cpu'),
#             weights_only=False,
#         )
#         model.eval()
#         logger.info("Model loaded successfully.")
#     except Exception as e:
#         logger.error(f"Error loading model: {e}")
#         traceback.print_exc()
#         model = None

# load_model()

# # Map class labels to names
# label_map = {
#     1: 'freckles',
#     2: 'eye bags',
#     3: 'dark circles',
#     4: 'acne',
#     5: 'rashes',
#     6: 'pigmentation',
#     7: 'wrinkles',
#     8: 'skin cancer',
#     9: 'black-heads',
#     10: 'dark spots',
# }

# @csrf_exempt
# @require_POST
# @login_required
# def predict_view(request):
#     if 'file' not in request.FILES:
#         return JsonResponse({'error': 'No file provided'}, status=400)

#     image_file = request.FILES['file']
#     img = Image.open(image_file).convert("RGB")

#     original_width, original_height = img.size
#     target_width, target_height = TARGET_SIZE

#     # Preprocess image
#     transform = transforms.Compose([
#         transforms.ToTensor()
#     ])
#     img_tensor = transform(img).unsqueeze(0)  # [1, C, H, W]

#     with torch.no_grad():
#         predictions = model(img_tensor)[0]

#     boxes = predictions['boxes']
#     labels = predictions['labels']
#     scores = predictions['scores']

#     # Resize the image FIRST
#     img = img.resize(TARGET_SIZE, Image.LANCZOS)

#     # Calculate scale factors for boxes
#     scale_x = target_width / original_width
#     scale_y = target_height / original_height

#     detected_issues = set()
#     confidence_scores = {} # <-- NEW: Dictionary to store confidence scores
#     draw = ImageDraw.Draw(img)

#     try:
#         font = ImageFont.truetype("arial.ttf", 30)
#     except:
#         font = ImageFont.load_default()

#     for box, label, score in zip(boxes, labels, scores):
#         if score > 0.3:
#             box = box.tolist()
#             # Scale box coordinates
#             scaled_box = [
#                 box[0] * scale_x,
#                 box[1] * scale_y,
#                 box[2] * scale_x,
#                 box[3] * scale_y
#             ]
#             label_name = label_map.get(label.item(), "Unknown")
#             issue_key = label_name.lower() # Use lower case for consistency with frontend
#             detected_issues.add(issue_key)

#             confidence = round(score.item() * 100, 2)
#             # <-- NEW: Store the confidence for the issue
#             # If multiple detections for the same issue, take the max confidence
#             confidence_scores[issue_key] = max(confidence_scores.get(issue_key, 0), confidence)


#             # Draw rectangle
#             draw.rectangle(scaled_box, outline="red", width=2)

#             # Draw label text
#             text = f"{label_name} ({confidence}%)"
#             text_position = (scaled_box[0], scaled_box[1] - 15 if scaled_box[1] - 15 > 0 else scaled_box[1])
#             draw.text(text_position, text, fill="white", font=font)

#     # Convert image to base64 for JSON response
#     img_io = io.BytesIO()
#     img.save(img_io, format='JPEG')
#     img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

#     # Prepare remedies data for all detected issues
#     def normalize_condition(predicted_label):
#         return CONDITION_ALIASES.get(predicted_label.lower(), predicted_label.lower())

#     remedies_data = {}
#     for issue in detected_issues:
#         normalized_issue = normalize_condition(issue)
#         try:
#             condition = SkinCondition.objects.get(name__iexact=normalized_issue)
#             remedies_data[issue] = {
#                 'causes': [c.strip() for c in condition.causes.split('\n') if c.strip()],
#                 'symptoms': [s.strip() for s in condition.symptoms.split('\n') if s.strip()],
#                 'remedies': [
#                     {
#                         'title': r.title,
#                         'directions': r.formatted_directions(),
#                         'amount': r.amount,
#                         'image_url': r.image.url if r.image else None
#                     } for r in condition.remedy_set.all()
#                 ]
#             }
#         except SkinCondition.DoesNotExist:
#             continue

#     return JsonResponse({
#         'status': 'success',
#         'annotated_image': img_base64,
#         'detected_issues': list(detected_issues),
#         'remedies_data': remedies_data,
#         'confidence_scores': confidence_scores # <-- NEW: Include confidence_scores
#     })



def capture(request):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return HttpResponse("Webcam not accessible", status=500)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return HttpResponse("Failed to capture image", status=500)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(frame_rgb)

    img_io = io.BytesIO()
    img_pil.save(img_io, format='JPEG')
    img_io.seek(0)

    return HttpResponse(img_io, content_type="image/jpeg")

def get_remedies(request):
    issue = request.GET.get('issue', '').lower()
    try:
        condition = SkinCondition.objects.get(name__iexact=issue)

        causes = condition.causes.split('\n') if condition.causes else []
        symptoms = condition.symptoms.split('.') if condition.symptoms else []

        remedies = [
            {
                "title": r.title,
                'directions': r.formatted_directions(),
                'amount': r.amount,
                'image_url': r.image.url if r.image else None
            } for r in condition.remedy_set.all()
        ]
        print("Sending remedies:", remedies)
        return JsonResponse({
            'causes': [c.strip() for c in causes if c.strip()],
            'symptoms': [s.strip() for s in symptoms if s.strip()],
            'remedies': remedies
        })
    except SkinCondition.DoesNotExist:
        return JsonResponse({'error': 'Condition not found'}, status=404)


# Your other view functions (e.g., user registration, login, etc.)
# ...

@login_required
def predict_page_view(request): # Renamed for clarity, or you can keep it 'predict_view' if you prefer
    return render(request, 'predict.html')


from utils.aliases import CONDITION_ALIASES;

    

def article_general_view(request):
    """
    This view will render a general article page.
    You mentioned you'll put different content in it.
    """
    return render(request, 'predictor/article.html', {}) # Render the article.html template

def skin_conditions_list_view(request):
    """
    This view will render a page listing all available skin condition pages
    by fetching them from the database.
    """
    # Fetch ALL SkinCondition_page objects from the database
    all_skin_conditions = SkinCondition_page.objects.all() # <--- Use the correct model name

    context = {
        'all_skin_conditions': all_skin_conditions,
    }
    return render(request, 'Skin Conditions.html', context) #


def skin_condition_detail(request, condition_slug):
    """
    This view fetches and displays the details for a single skin condition page
    based on its slug, retrieving data from the database.
    """
    # Use get_object_or_404 to fetch the SkinCondition_page object by its slug.
    skin_condition = get_object_or_404(SkinCondition_page, slug=condition_slug) # <--- Use the correct model name

    context = {
        'skin_condition': skin_condition,
    }
    # Assuming 'skin_condition_page.html' is your detailed template for a single condition.
    return render(request, 'Skin Conditions.html', context)

from .models import Article # Make sure this import is correct

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)

    # --- ADD THESE DEBUGGING LINES ---
    print(f"DEBUG: Type of 'article': {type(article)}")
    print(f"DEBUG: Content of 'article': {article}")
    if hasattr(article, 'pk'):
        print(f"DEBUG: PK of 'article': {article.pk}")
    else:
        print("DEBUG: 'article' object has no 'pk' attribute.")
    # --- END DEBUGGING LINES ---

    related_articles = Article.objects.filter(
        category=article.category
    ).exclude(pk=article.pk)[:3]

    return render(request, 'detailed_articles.html', { # Or 'article_detail.html' as per earlier advice
        'article': article,
        'related_articles': related_articles
    })

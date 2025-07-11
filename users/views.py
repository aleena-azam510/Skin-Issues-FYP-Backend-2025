# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.http import url_has_allowed_host_and_scheme

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import ipdb
from .forms import CustomUserCreationForm

User = get_user_model()

def auth_view(request):
    registration_form = CustomUserCreationForm()
    login_form = AuthenticationForm()

    redirect_to = request.POST.get('next', request.GET.get('next', ''))

    print(f"--- Auth View Debug ---")
    print(f"Request method: {request.method}")
    print(f"Initial redirect_to: {redirect_to}")

    if not url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts=[request.get_host()]):
        redirect_to = 'index_page'
        print(f"url_has_allowed_host_and_scheme returned False. Final redirect_to: {redirect_to}")
    else:
        print(f"url_has_allowed_host_and_scheme returned True. Final redirect_to: {redirect_to}")
    print(f"--- End Auth View Debug ---\n")

    if request.method == 'POST':
        if 'signup_submit' in request.POST:
            registration_form = CustomUserCreationForm(request.POST)
            if registration_form.is_valid():
                user = registration_form.save()
                login(request, user)
                messages.success(request, f'Account created for {user.username}!')
                return redirect(redirect_to)
            else:
                messages.error(request, 'Registration failed. Please correct the errors.')
                return render(request, 'users/register.html', {
                    'registration_form': registration_form,
                    'login_form': login_form,
                    'active_panel': 'right-panel-active'
                })

        elif 'signin_submit' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome back, {username}!')
                    return redirect(redirect_to)
                else:
                    messages.error(request, 'Invalid username or password.')
            else:
                messages.error(request, 'Login failed. Please correct the errors.')
            return render(request, 'users/register.html', {
                'registration_form': registration_form,
                'login_form': login_form,
                'active_panel': ''
            })

    return render(request, 'users/register.html', {
        'registration_form': registration_form,
        'login_form': login_form,
        'active_panel': ''
    })


def index_page(request):
    print(f"*** Index Page Accessed *** User authenticated: {request.user.is_authenticated}")
    return render(request, 'users/index.html')


def logout_view(request):
    print(f"*** Logout View Accessed *** User authenticated BEFORE logout: {request.user.is_authenticated}")
    logout(request)
    messages.info(request, 'You have been logged out.')
    print(f"*** Logout View Accessed *** User authenticated AFTER logout: {request.user.is_authenticated}")
    return redirect('auth_page')


def download_users_pdf(request):
    print(f"*** Download Users PDF Accessed *** User authenticated: {request.user.is_authenticated}")
    # ... (rest of your download_users_pdf code)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "Registered Users List")
    users = User.objects.all().order_by('username')
    y_position = 700
    line_height = 20
    p.setFont("Helvetica", 12)
    p.drawString(50, y_position, "Username")
    p.drawString(200, y_position, "Email")
    p.drawString(400, y_position, "Date Joined")
    y_position -= line_height
    p.line(50, y_position + 5, 550, y_position + 5)
    y_position -= (line_height / 2)
    for user in users:
        if y_position < 100:
            p.showPage()
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, 750, "Registered Users List (Continued)")
            p.setFont("Helvetica", 12)
            p.drawString(50, y_position, "Username")
            p.drawString(200, y_position, "Email")
            p.drawString(400, y_position, "Date Joined")
            y_position -= line_height
            p.line(50, y_position + 5, 550, y_position + 5)
            y_position -= (line_height / 2)
        p.drawString(50, y_position, user.username)
        p.drawString(200, y_position, user.email or "N/A")
        p.drawString(400, y_position, user.date_joined.strftime("%Y-%m-%d %H:%M"))
        y_position -= line_height
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="registered_users.pdf"'
    return response


def developer_team_view(request):
    print(f"*** Developer Team View Accessed *** User authenticated: {request.user.is_authenticated}")
    return render(request, 'developer_Team.html')

# Assuming these are the exact names in your urls.py (based on your last snippet)
# AND YOU HAVE PUT @login_required ON THEM IN YOUR ACTUAL FILE
@login_required
def model_page_view(request):
    #ipdb.set_trace() # <--- ADD THIS LINE HERE!
    print(f"*** Model Page View Accessed *** User authenticated: {request.user.is_authenticated}")
    return render(request, 'modelPage.html' , {'is_authenticated': True})

# Assuming this is the exact name in your urls.py (based on your last snippet)
# AND YOU HAVE PUT @login_required ON THEM IN YOUR ACTUAL FILE

def article_view(request):
    print(f"*** Article View Accessed *** User authenticated: {request.user.is_authenticated}")
    return render(request,'article.html', {'is_authenticated': True})


from django.shortcuts import render
from reviews.models import Review # Make sure this import is correct

# Your existing view functions would be here...
#  Add these lines for logging
# Add these lines for logging
import logging
logger = logging.getLogger(__name__)

def index_page(request):
    logger.info("--- DEBUG: Entering index_page view ---")
    print("--- DEBUG: Entering index_page view ---") # For console output

    # Fetch all reviews, ordered by creation date (newest first)
    all_reviews = Review.objects.all().order_by('-created_at')
    logger.info(f"--- DEBUG: Fetched {all_reviews.count()} reviews from DB ---")
    print(f"--- DEBUG: Fetched {all_reviews.count()} reviews from DB ---")

    # Log review details immediately after fetching from the database
    print("\n--- DEBUG: Review Details Immediately After Fetching ---")
    for review in all_reviews:
        # Check if a user is associated with the review
        user_id_debug = review.user.id if review.user else "None (Guest Review)"
        print(f"Review ID: {review.id}, Reviewer: {review.reviewer_name}, Rating (after fetch): {review.rating}, Associated User ID (after fetch): {user_id_debug}")

    total_reviews_count = all_reviews.count()

    context = {
        'reviews': all_reviews,
        'total_reviews_count': total_reviews_count,
    }
    logger.info("--- DEBUG: Context prepared for rendering ---")
    print("\n--- DEBUG: Review Details Just Before Rendering ---")

    # Log review details just before passing to the template context
    for review in context['reviews']:
        user_id_debug = review.user.id if review.user else "None (Guest Review)"
        print(f"Review ID: {review.id}, Reviewer: {review.reviewer_name}, Rating (before render): {review.rating}, Associated User ID (before render): {user_id_debug}")

    return render(request, 'users/index.html', context)
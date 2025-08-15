from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import json
import os
import re # Import the regular expressions module
import assemblyai as aai
from groq import Groq
import yt_dlp
from .models import BlogPost
from .supabase_client import supabase
from django.db import transaction

# --- Helper Functions ---

def clean_youtube_title(title):
    """
    Cleans a YouTube title by removing hashtags, emojis, and common promotional text.
    """
    # Remove hashtags
    title = re.sub(r'#\w+', '', title)
    
    # Remove text in parentheses or brackets (like "Official Video")
    title = re.sub(r'[\(\[].*?[\)\]]', '', title)
    
    # Remove non-alphanumeric characters except for essential punctuation
    # This will get rid of most emojis and special symbols
    title = re.sub(r'[^\w\s\-\'?!.,:]', '', title)
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    return title.strip()
def get_yt_metadata(link):
    """
    Gets YouTube video metadata and audio, using both a proxy and a cookies file.
    """
    try:
        # 1. Get the proxy URL from the environment variables
        proxy_url = os.environ.get('PROXY_URL')

        # 2. Define the path to your cookies file
        cookies_file_path = os.path.join(settings.BASE_DIR, 'cookies.txt')

        # 3. Define yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # Add the cookie file option
            'cookiefile': cookies_file_path,
        }

        # 4. Conditionally add the proxy to the options if it's set
        # This prevents an error if the PROXY_URL environment variable is not found
        if proxy_url:
            ydl_opts['proxy'] = proxy_url

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            original_title = info_dict.get('title', 'Unknown Title')
            cleaned_title = clean_youtube_title(original_title)

            video_id = info_dict.get('id')
            audio_file_path = os.path.join(settings.MEDIA_ROOT, f"{video_id}.mp3")

            # Fallback check in case the downloaded file has a different extension (e.g., .m4a, .webm)
            if not os.path.exists(audio_file_path):
                for file in os.listdir(settings.MEDIA_ROOT):
                    if file.startswith(video_id):
                        audio_file_path = os.path.join(settings.MEDIA_ROOT, file)
                        break

            return cleaned_title, audio_file_path
            
    except Exception as e:
        print(f"Error with yt-dlp: {e}")
        return None, None

def get_transcription(audio_file_path):
    """Transcribes the audio file and cleans it up."""
    try:
        aai.settings.api_key = os.environ.get("ASSEMBLYAI_API_KEY")
        if not aai.settings.api_key:
            raise ValueError("ASSEMBLYAI_API_KEY not set in environment variables.")

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file_path)

        if transcript.status == aai.TranscriptStatus.error:
            print(f"Transcription Error: {transcript.error}")
            return None
            
        return transcript.text
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None
    finally:
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)

def generate_blog_from_transcription(transcription):
    try:
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not set in environment variables.")

        client = Groq(api_key=groq_api_key)
        messages = [
            {"role": "system", "content": "You are a professional blog writer..."},
            {"role": "user", "content": f"Create a blog article from this transcript:\n\n{transcription}"}
        ]
        chat_completion = client.chat.completions.create(
            messages=messages, model="llama3-8b-8192", max_tokens=2048
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating blog content: {e}")
        return None

# --- Main Views ---

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        title, audio_path = get_yt_metadata(yt_link)
        if not audio_path:
             return JsonResponse({'error': "Failed to download audio..."}, status=500)
        
        transcription = get_transcription(audio_path)
        if not transcription:
            return JsonResponse({'error': "Failed to get transcript."}, status=500)

        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': "Failed to generate blog content."}, status=500)

        new_blog_post = BlogPost.objects.create(
            user=request.user,
            youtube_title=title, # The cleaned title is used here
            youtube_link=yt_link,
            generated_content=blog_content,
        )
        
        return JsonResponse({'blog_post_id': new_blog_post.pk})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# --- Other Views (Unchanged) ---
@login_required
def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})

@login_required
def blog_details(request, pk):
    try:
        blog_article = BlogPost.objects.get(pk=pk, user=request.user)
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article})
    except BlogPost.DoesNotExist:
        return redirect('blog-list')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error_message': "Invalid credentials."})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password != repeatPassword:
            return render(request, 'signup.html', {'error_message': 'Passwords do not match.'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error_message': 'Username is already taken.'})

        try:
            # Use a transaction to ensure both operations succeed or neither do.
            with transaction.atomic():
                # 1. Create the user in Supabase first
                supabase_user = supabase.auth.admin.create_user({
                    "email": email, 
                    "password": password,
                    "email_confirm": True, # You can set this to False to require email verification
                })
                
                # Check if the Supabase user was created successfully
                if not supabase_user:
                    raise Exception("Could not create user in Supabase.")
                django_user = User.objects.create_user(username, email, password)
                login(request, django_user)
                
                return redirect('/')

        except Exception as e:
            # Handle potential errors from Supabase (e.g., weak password, user exists)
            # or from Django.
            print(f"Error during signup: {e}")
            error_message = 'Error creating account. The user might already exist or the password is too weak.'
            return render(request, 'signup.html', {'error_message': error_message})
        
    return render(request, 'signup.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

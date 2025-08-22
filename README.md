# 🤖 AI YouTube-to-Blog Generator

Instantly convert any YouTube video into a well-structured, ready-to-publish blog post. This Django-powered web application uses a modern UI and powerful AI services to automate your content creation workflow.

---

## ✨ Key Features

-   **✍️ Automated Content Creation**: Paste a YouTube link and get a full blog article in minutes.
-   **🚀 Powered by AI**: Utilizes **AssemblyAI** for highly accurate audio transcription and **Groq** for lightning-fast content generation with state-of-the-art language models.
-   **🌓 Modern UI**: A clean, responsive interface with a persistent **dark/light mode** theme to suit your preference.
-   **👤 User Accounts**: Secure sign-up and login to save and manage all your generated blog posts.
-   **🖼️ Dynamic Thumbnails**: Automatically fetches and displays the YouTube video thumbnail for each saved article.
-   **🧹 Clean Titles**: Automatically removes hashtags, emojis, and other "clutter" from YouTube titles for clean, professional blog headings.

---

## 🛠️ Tech Stack

-   **Backend**: Django, Python
-   **Frontend**: HTML, Tailwind CSS, JavaScript
-   **APIs**:
    -   `yt-dlp` for downloading YouTube video audio.
    -   AssemblyAI for speech-to-text transcription.
    -   Groq for AI blog content generation.
-   **Database**: SQLite (for simple, local persistence)
-   **Core Prerequisite**: FFmpeg

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

Make sure you have the following software installed on your system:
-   Python 3.8+
-   `pip` (Python package installer)
-   **FFmpeg**: This is a crucial dependency for processing audio. You can install it from [ffmpeg.org](https://ffmpeg.org/download.html) or using a package manager:
    -   **Windows (with Chocolatey):** `choco install ffmpeg`
    -   **macOS (with Homebrew):** `brew install ffmpeg`
    -   **Linux (Debian/Ubuntu):** `sudo apt install ffmpeg`

### Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/IshanPaharia/AIBlogApp.git](https://github.com/IshanPaharia/AIBlogApp.git)
    cd AIBlogApp
    ```

2.  **Create and Activate a Virtual Environment**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    Install all the required Python packages from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    You need to provide your secret API keys. Create a file named `.env` in the root of the project directory.
    ```bash
    # On Windows (in Command Prompt):
    copy nul .env
    # On macOS/Linux:
    touch .env
    ```
    Now, open the `.env` file and add the following lines, replacing the placeholder text with your actual keys:
    ```env
    SECRET_KEY='your-strong-django-secret-key-here'
    ASSEMBLYAI_API_KEY='your-assemblyai-api-key-here'
    GROQ_API_KEY='your-groq-api-key-here'
    ```

5.  **Apply Database Migrations**
    This will set up the necessary tables in your SQLite database.
    ```bash
    python manage.py migrate
    ```

6.  **Run the Development Server**
    You're all set! Start the Django server.
    ```bash
    python manage.py runserver
    ```
    The application will be available at: **http://127.0.0.1:8000/**

---

## ⭐️ Show Your Support

If you find this project useful or interesting, please consider giving it a ⭐ on GitHub!

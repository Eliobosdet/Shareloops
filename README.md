# 🎵 Shareloops - Music Sharing Platform

**Shareloops** is a modern web platform for music producers to **share, discover, and download audio loops and sample packs**.  
Built with **Django**, it provides a comprehensive ecosystem for the music production community.

---

## 🚀 Features

### 🎶 Audio Content
- **Loop Sharing**: Upload and share individual audio loops with metadata (BPM, key, genre)
- **Sample Packs**: Share complete sample pack collections as ZIP files
- **Audio Preview**: Built-in audio player with play tracking
- **Cover Art**: Visual representation for all audio content

### 👤 User System
- **User Profiles**: Customizable profiles with bio and profile pictures
- **Authentication**: Secure login/registration system
- **User Content**: Personal dashboard to manage uploads

### 🔍 Discovery & Search
- **Advanced Search**: Search by title, description, tags, and metadata
- **Filter System**: Filter by genre, BPM, key, and tags
- **Tag System**: Organize content with custom tags using Tagify integration
- **Most Liked**: Discover popular content based on community engagement

### 💬 Social Features
- **Like System**: Like/unlike content with AJAX functionality
- **Comments**: Community discussion on uploaded content
- **Play Tracking**: Analytics for audio plays and downloads
- **Download System**: Track downloads for loops and sample packs

### 📱 Modern UI/UX
- **Responsive Design**: Mobile-first, Bootstrap-based interface
- **AJAX Interactions**: Seamless user experience without page reloads
- **Audio Player**: Custom HTML5 audio controls
- **Real-time Updates**: Dynamic content loading and updates

---

## 🛠️ Technology Stack

- **Backend**: Django 5.2, Python 3.13  
- **Frontend**: Bootstrap 5, JavaScript (ES6+), HTML5, CSS3  
- **Database**: SQLite (development), PostgreSQL-ready  
- **Audio Processing**: HTML5 Audio API  
- **File Handling**: Django file uploads with media management  
- **UI Components**: Tagify for tag management, FontAwesome icons  

---

## 📋 Requirements
- Python **3.13+**
- Virtualenv (consigliato)
- Libmagic (per Windows installare `python-magic-bin`)

---

## ⚡ Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Eliobosdet/shareloops.git
   cd shareloops

2. **Set up the environment
   ```bash
   # Create the environment
   python -m venv venv
   
   # Activate it
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # On Windows PowerShell: copy .env.example .env

5. **Database Initialization**
   ```bash
   python manage.py makemigrations
   python manage.py migrate

6. **Create a Superuser (Admin Access)**
   ```bash
   python manage.py createsuperuser
   
7. **Run development server**
   ```bash
   python manage.py runserver

8. **Visit the app**
   ```bash
   Open http://localhost:8000 in your browser.

## 🛡️ Security & Best Practices
- Environment Isolation: Sensitive keys and debug settings are managed via .env files and never committed to version control.

- Dependency Management: A clean requirements.txt is provided for reproducible builds.

- Git Discipline: Optimized .gitignore to exclude environment folders, databases, and temporary caches.

## 📄 License
Distributed under the MIT License. See LICENSE for more information.

Author: [Elio]

Project Link: https://github.com/Eliobosdet/shareloops

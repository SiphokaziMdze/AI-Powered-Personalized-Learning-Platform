# AI-Powered Personalized Learning Platform 🤖📚

An AI-powered learning platform developed as my **BEngTech Computer Engineering final-year project** for the module **Industrial Design Project 3**.

The platform was designed to make online learning more personalised by combining AI-powered content analysis, adaptive learning, assessments, educational games, learning analytics, and AI-assisted tutoring.

## 🎯 Project Overview

Traditional online learning platforms often provide the same content and difficulty level to every student. This project explores how AI can be used to create a more personalised, interactive, and engaging learning experience.

The platform can:

- Analyse the difficulty of learning content
- Generate quiz questions from lesson content
- Summarise learning material
- Identify key concepts and learning areas
- Analyse quiz and learning performance
- Identify strengths and weaker areas
- Recommend suitable next learning steps
- Adapt learning difficulty based on performance
- Provide AI-assisted tutoring and learning support
- Provide interactive educational games to reinforce learning

## 🧠 AI & Personalisation

The AI functionality is implemented using **Python and Hugging Face Transformers**.

The project includes AI pipelines for:

- **Zero-shot classification** using `facebook/bart-large-mnli` for content difficulty analysis
- **Text summarisation** using `facebook/bart-large-cnn`
- **Question generation** using `google/flan-t5-small`
- Personalised recommendations based on student progress and quiz performance
- Adaptive difficulty levels based on learning results

The system also includes fallback logic so that basic functionality can still be provided when the AI models are unavailable.

## 🎮 Educational Games

The platform includes interactive **educational games** designed to make learning more engaging while reinforcing concepts covered in the learning content.

The games form part of the wider personalised learning experience alongside quizzes, AI-generated learning content, progress tracking, and recommendations.

## 🏗️ Technology Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Django

### AI / NLP
- Hugging Face Transformers
- Natural Language Processing (NLP)
- Text classification
- Text summarisation
- Question generation
- Adaptive learning recommendations

### Database
- SQLite

### Tools
- Visual Studio Code
- Git
- GitHub

## 📂 Project Structure

```text
AI-Powered-Personalized-Learning-Platform/
│
├── backend/
│   ├── core/          # Django project configuration
│   ├── learning/      # Learning models and AI functionality
│   ├── frontend/      # Application frontend
│   └── manage.py      # Django management script
│
├── media/resources/   # Learning resources
├── requirements.txt   # Python dependencies
└── README.md
```

## 🚀 Key Features

### Adaptive Learning
Student performance is analysed to help determine appropriate difficulty levels and recommend what to study next.

### AI-Generated Questions
The platform can generate quiz questions from lesson content using a Hugging Face text-generation model.

### Content Analysis
Learning content can be analysed to estimate difficulty, generate summaries, and identify important concepts.

### Learning Analytics
The system tracks learning progress and quiz performance to identify strengths, weaker areas, and recommended areas for practice.

### Educational Games
Interactive educational games provide another way for students to practise and reinforce learning concepts.

### AI Tutor Support
The platform includes AI-assisted learning support through conversational functionality.

## 💡 What I Learned

This project gave me practical experience in combining **software development, artificial intelligence, NLP, databases, educational technology, and user-focused problem solving** into one application.

It also strengthened my understanding of how AI can be integrated into a software system rather than being treated as a standalone model.

## 👩🏽‍💻 About the Project

**Qualification:** BEngTech in Computer Engineering  
**Module:** Industrial Design Project 3  
**Project Type:** Final-Year Project

Built by **Siphokazi Veronica Mdze**.

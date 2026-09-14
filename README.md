# AI-Powered Personalized Learning Platform 🤖📚

An AI-powered learning platform developed as my **BEngTech Computer Engineering final-year project** for **Industrial Design Project 3**.

The platform was designed to make online learning more personalised by using AI to analyse learning content and student performance, generate learning material, and provide adaptive recommendations.

## 🎯 Project Overview

Traditional online learning platforms often provide the same content and difficulty level to every student. This project explores how AI can be used to create a more personalised learning experience.

The platform combines a web-based learning environment with AI services that can:

- Analyse the difficulty of learning content
- Generate quiz questions from lesson content
- Summarise learning material
- Identify key concepts and learning areas
- Analyse quiz and learning performance
- Identify strengths and weaker areas
- Recommend suitable next learning steps
- Adapt learning difficulty based on performance
- Provide AI-assisted tutoring and learning support

## 🧠 AI & Personalisation

The AI functionality is implemented using **Python and Hugging Face Transformers**.

The project includes AI pipelines for:

- **Zero-shot classification** using `facebook/bart-large-mnli` for content difficulty analysis
- **Text summarisation** using `facebook/bart-large-cnn`
- **Question generation** using `google/flan-t5-small`
- Personalised recommendations based on student progress and quiz performance
- Adaptive difficulty levels based on learning results

The system also includes fallback logic so that basic functionality can still be provided when the AI models are unavailable.

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

### AI Tutor Support
The platform includes AI-assisted learning support through conversational functionality.

## 💡 What I Learned

This project gave me practical experience in combining **software development, artificial intelligence, NLP, databases, and user-focused problem solving** into one application.

It also strengthened my understanding of how AI can be integrated into a software system rather than being treated as a standalone model.

## 👩🏽‍💻 About the Project

**Qualification:** BEngTech in Computer Engineering  
**Project:** Industrial Design Project 3  
**Project Type:** Final-Year Project

Built by **Siphokazi Veronica Mdze**.

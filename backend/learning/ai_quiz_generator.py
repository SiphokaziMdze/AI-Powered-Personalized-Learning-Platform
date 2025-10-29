# backend/learning/ai_quiz_generator.py
"""
Advanced AI-Powered Quiz Generation Service
Uses language models to generate high-quality quiz questions from lesson content
"""

import logging
import json
import re
from typing import List, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class AIQuizGenerator:
    """
    Generates quiz questions using AI based on lesson content
    Supports multiple AI backends: Anthropic Claude, OpenAI, HuggingFace
    """
    
    def __init__(self):
        self.backend = self._initialize_backend()
        
    def _initialize_backend(self):
        """Initialize the AI backend based on available API keys"""
        # Try Anthropic Claude first (best quality)
        if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Initialized Anthropic Claude for quiz generation")
                return 'anthropic'
            except ImportError:
                logger.warning("anthropic package not installed")
        
        # Try OpenAI
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            try:
                import openai
                openai.api_key = settings.OPENAI_API_KEY
                logger.info("Initialized OpenAI for quiz generation")
                return 'openai'
            except ImportError:
                logger.warning("openai package not installed")
        
        # Fallback to HuggingFace (requires local models)
        logger.info("Using HuggingFace local models for quiz generation")
        return 'huggingface'
    
    def generate_quiz_questions(
        self,
        lesson_content: str,
        lesson_title: str,
        difficulty: str = 'intermediate',
        num_questions: int = 5,
        question_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions from lesson content using AI
        
        Args:
            lesson_content: The lesson text content to generate questions from
            lesson_title: Title of the lesson
            difficulty: 'beginner', 'intermediate', or 'advanced'
            num_questions: Number of questions to generate
            question_types: Types of questions to generate
        
        Returns:
            List of question dictionaries
        """
        if not question_types:
            question_types = ['multiple_choice', 'true_false', 'short_answer']
        
        if self.backend == 'anthropic':
            return self._generate_with_anthropic(
                lesson_content, lesson_title, difficulty, num_questions, question_types
            )
        elif self.backend == 'openai':
            return self._generate_with_openai(
                lesson_content, lesson_title, difficulty, num_questions, question_types
            )
        else:
            return self._generate_with_huggingface(
                lesson_content, lesson_title, difficulty, num_questions, question_types
            )
    
    def _generate_with_anthropic(
        self,
        lesson_content: str,
        lesson_title: str,
        difficulty: str,
        num_questions: int,
        question_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate questions using Anthropic Claude"""
        try:
            prompt = self._build_quiz_prompt(
                lesson_content, lesson_title, difficulty, num_questions, question_types
            )
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            questions = self._parse_questions_from_response(response_text)
            
            logger.info(f"Generated {len(questions)} questions using Anthropic Claude")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions with Anthropic: {e}")
            return self._generate_fallback_questions(lesson_title, difficulty, num_questions)
    
    def _generate_with_openai(
        self,
        lesson_content: str,
        lesson_title: str,
        difficulty: str,
        num_questions: int,
        question_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate questions using OpenAI GPT"""
        try:
            import openai
            
            prompt = self._build_quiz_prompt(
                lesson_content, lesson_title, difficulty, num_questions, question_types
            )
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator who generates high-quality quiz questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            response_text = response.choices[0].message.content
            questions = self._parse_questions_from_response(response_text)
            
            logger.info(f"Generated {len(questions)} questions using OpenAI")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions with OpenAI: {e}")
            return self._generate_fallback_questions(lesson_title, difficulty, num_questions)
    
    def _generate_with_huggingface(
        self,
        lesson_content: str,
        lesson_title: str,
        difficulty: str,
        num_questions: int,
        question_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate questions using HuggingFace models"""
        try:
            from transformers import pipeline
            
            # Use a text generation model
            generator = pipeline('text-generation', model='gpt2')
            
            prompt = f"Generate {num_questions} quiz questions about {lesson_title}:\n\n"
            prompt += f"Content: {lesson_content[:500]}...\n\n"
            prompt += "Questions:\n1."
            
            result = generator(prompt, max_length=500, num_return_sequences=1)
            generated_text = result[0]['generated_text']
            
            # Parse and structure the generated questions
            questions = self._parse_huggingface_output(generated_text, difficulty)
            
            if not questions:
                return self._generate_fallback_questions(lesson_title, difficulty, num_questions)
            
            logger.info(f"Generated {len(questions)} questions using HuggingFace")
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Error generating questions with HuggingFace: {e}")
            return self._generate_fallback_questions(lesson_title, difficulty, num_questions)
    
    def _build_quiz_prompt(
        self,
        lesson_content: str,
        lesson_title: str,
        difficulty: str,
        num_questions: int,
        question_types: List[str]
    ) -> str:
        """Build the prompt for AI quiz generation"""
        
        difficulty_instructions = {
            'beginner': 'Focus on basic recall and understanding. Questions should test fundamental concepts.',
            'intermediate': 'Include application and analysis questions. Test deeper understanding and practical application.',
            'advanced': 'Create challenging questions that require critical thinking, synthesis, and evaluation.'
        }
        
        prompt = f"""Generate {num_questions} high-quality educational quiz questions based on the following lesson content.

Lesson Title: {lesson_title}
Difficulty Level: {difficulty.upper()}
{difficulty_instructions.get(difficulty, difficulty_instructions['intermediate'])}

Lesson Content:
{lesson_content[:2000]}

Generate questions in the following format as a JSON array:

[
  {{
    "question": "The question text",
    "type": "multiple_choice",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Why this is correct",
    "difficulty": "{difficulty}"
  }},
  {{
    "question": "The question text",
    "type": "true_false",
    "correct_answer": true,
    "explanation": "Why this is correct",
    "difficulty": "{difficulty}"
  }},
  {{
    "question": "The question text",
    "type": "short_answer",
    "sample_answer": "A good example answer",
    "key_points": ["Point 1", "Point 2"],
    "difficulty": "{difficulty}"
  }}
]

Include a mix of question types: {', '.join(question_types)}

Requirements:
1. Questions must be directly based on the lesson content
2. Avoid trivial or overly simple questions
3. Each question should test a different concept
4. Provide clear, unambiguous wording
5. For multiple choice, ensure wrong answers are plausible but clearly incorrect
6. Include helpful explanations for correct answers
7. Return ONLY the JSON array, no other text

Generate the questions now:"""
        
        return prompt
    
    def _parse_questions_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse questions from AI response"""
        try:
            # Try to find JSON array in the response
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                json_str = json_match.group(0)
                questions = json.loads(json_str)
                
                # Validate and clean questions
                validated_questions = []
                for q in questions:
                    if 'question' in q and 'type' in q:
                        validated_questions.append(q)
                
                return validated_questions
            
            # If JSON parsing fails, try to extract questions manually
            return self._manual_parse_questions(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            return self._manual_parse_questions(response_text)
    
    def _manual_parse_questions(self, text: str) -> List[Dict[str, Any]]:
        """Manually parse questions if JSON parsing fails"""
        questions = []
        
        # Split by question numbers
        question_blocks = re.split(r'\n\s*\d+\.\s+', text)
        
        for block in question_blocks[1:]:  # Skip first empty split
            if len(block.strip()) < 10:
                continue
            
            lines = block.strip().split('\n')
            question_text = lines[0].strip()
            
            # Try to determine question type
            if '?' in question_text:
                if 'true' in question_text.lower() or 'false' in question_text.lower():
                    questions.append({
                        'question': question_text,
                        'type': 'true_false',
                        'correct_answer': True,
                        'difficulty': 'medium'
                    })
                else:
                    # Extract options if present
                    options = []
                    for line in lines[1:5]:
                        if line.strip() and (line.strip()[0].isalpha() or line.strip().startswith('-')):
                            options.append(line.strip().lstrip('ABCD)-. '))
                    
                    if len(options) >= 2:
                        questions.append({
                            'question': question_text,
                            'type': 'multiple_choice',
                            'options': options[:4],
                            'correct_answer': options[0] if options else '',
                            'difficulty': 'medium'
                        })
                    else:
                        questions.append({
                            'question': question_text,
                            'type': 'short_answer',
                            'sample_answer': 'Student should explain the concept in their own words.',
                            'difficulty': 'medium'
                        })
        
        return questions[:5]  # Return up to 5 questions
    
    def _parse_huggingface_output(self, text: str, difficulty: str) -> List[Dict[str, Any]]:
        """Parse HuggingFace generated text into structured questions"""
        return self._manual_parse_questions(text)
    
    def _generate_fallback_questions(
        self,
        lesson_title: str,
        difficulty: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """Generate basic template questions as fallback"""
        logger.warning("Using fallback question generation")
        
        questions = []
        
        if difficulty == 'beginner':
            questions = [
                {
                    'question': f"What is the main concept covered in {lesson_title}?",
                    'type': 'multiple_choice',
                    'options': [
                        f"Core concept of {lesson_title}",
                        "Unrelated concept A",
                        "Unrelated concept B",
                        "None of the above"
                    ],
                    'correct_answer': f"Core concept of {lesson_title}",
                    'explanation': f"The lesson focuses on teaching the fundamental concept of {lesson_title}",
                    'difficulty': 'easy'
                },
                {
                    'question': f"True or False: Understanding {lesson_title} is important for further learning.",
                    'type': 'true_false',
                    'correct_answer': True,
                    'explanation': f"{lesson_title} provides foundational knowledge for advanced topics",
                    'difficulty': 'easy'
                },
                {
                    'question': f"Describe one practical application of {lesson_title}.",
                    'type': 'short_answer',
                    'sample_answer': f"{lesson_title} can be applied in various real-world scenarios to solve practical problems.",
                    'key_points': ["Practical application", "Real-world relevance", "Problem-solving"],
                    'difficulty': 'easy'
                }
            ]
        elif difficulty == 'advanced':
            questions = [
                {
                    'question': f"Analyze the implications of {lesson_title} in complex scenarios.",
                    'type': 'short_answer',
                    'sample_answer': f"{lesson_title} has far-reaching implications that affect multiple aspects of the field.",
                    'key_points': ["Deep analysis", "Multiple perspectives", "Critical evaluation"],
                    'difficulty': 'hard'
                },
                {
                    'question': f"Which approach best integrates {lesson_title} with other advanced concepts?",
                    'type': 'multiple_choice',
                    'options': [
                        "Holistic integration approach",
                        "Sequential learning approach",
                        "Isolated study approach",
                        "None are effective"
                    ],
                    'correct_answer': "Holistic integration approach",
                    'explanation': "Integrating concepts holistically leads to deeper understanding",
                    'difficulty': 'hard'
                },
                {
                    'question': f"What are the limitations and challenges when applying {lesson_title} in practice?",
                    'type': 'short_answer',
                    'sample_answer': "Limitations include complexity, resource requirements, and context-specific constraints.",
                    'key_points': ["Practical limitations", "Implementation challenges", "Context awareness"],
                    'difficulty': 'hard'
                }
            ]
        else:  # intermediate
            questions = [
                {
                    'question': f"Explain the relationship between {lesson_title} and related concepts.",
                    'type': 'short_answer',
                    'sample_answer': f"{lesson_title} connects to other concepts through shared principles and applications.",
                    'key_points': ["Conceptual relationships", "Interconnections", "Application context"],
                    'difficulty': 'medium'
                },
                {
                    'question': f"Which statement best describes {lesson_title}?",
                    'type': 'multiple_choice',
                    'options': [
                        f"A comprehensive approach to understanding the topic",
                        "A simple memorization task",
                        "An optional supplementary topic",
                        "A deprecated concept"
                    ],
                    'correct_answer': f"A comprehensive approach to understanding the topic",
                    'explanation': f"{lesson_title} requires comprehensive understanding, not just memorization",
                    'difficulty': 'medium'
                },
                {
                    'question': f"Provide an example of how {lesson_title} solves a real-world problem.",
                    'type': 'short_answer',
                    'sample_answer': f"{lesson_title} can be used to address practical challenges by applying its core principles.",
                    'key_points': ["Real-world application", "Problem-solving", "Practical implementation"],
                    'difficulty': 'medium'
                }
            ]
        
        return questions[:num_questions]
    
    def generate_explanation(
        self,
        lesson_content: str,
        lesson_title: str,
        difficulty: str = 'intermediate'
    ) -> str:
        """Generate AI-powered explanation of lesson content"""
        if self.backend == 'anthropic':
            return self._explain_with_anthropic(lesson_content, lesson_title, difficulty)
        elif self.backend == 'openai':
            return self._explain_with_openai(lesson_content, lesson_title, difficulty)
        else:
            return self._explain_with_huggingface(lesson_content, lesson_title, difficulty)
    
    def _explain_with_anthropic(self, lesson_content: str, lesson_title: str, difficulty: str) -> str:
        """Generate explanation using Anthropic Claude"""
        try:
            prompt = f"""Explain the following lesson in a {difficulty} level way.

Lesson Title: {lesson_title}

Lesson Content:
{lesson_content[:2000]}

Provide a clear, engaging explanation that:
1. Summarizes the main concepts
2. Uses examples and analogies appropriate for {difficulty} learners
3. Highlights key takeaways
4. Suggests practical applications

Explanation:"""
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating explanation with Anthropic: {e}")
            return self._generate_fallback_explanation(lesson_title, difficulty)
    
    def _explain_with_openai(self, lesson_content: str, lesson_title: str, difficulty: str) -> str:
        """Generate explanation using OpenAI"""
        try:
            import openai
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": f"You are an expert educator explaining concepts at a {difficulty} level."},
                    {"role": "user", "content": f"Explain this lesson:\n\n{lesson_title}\n\n{lesson_content[:2000]}"}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating explanation with OpenAI: {e}")
            return self._generate_fallback_explanation(lesson_title, difficulty)
    
    def _explain_with_huggingface(self, lesson_content: str, lesson_title: str, difficulty: str) -> str:
        """Generate explanation using HuggingFace"""
        return self._generate_fallback_explanation(lesson_title, difficulty)
    
    def _generate_fallback_explanation(self, lesson_title: str, difficulty: str) -> str:
        """Generate basic explanation as fallback"""
        if difficulty == 'beginner':
            return f"""Let me explain {lesson_title} in simple terms:

This lesson covers fundamental concepts that are essential for understanding the topic. We'll break it down step by step to make it easy to follow.

Key concepts:
- Basic understanding of {lesson_title}
- Practical examples you can relate to
- Simple exercises to practice

Don't worry if it seems challenging at first - take your time and practice regularly!"""
        
        elif difficulty == 'advanced':
            return f"""Advanced analysis of {lesson_title}:

This lesson explores complex concepts and their applications. We'll dive deep into the theoretical foundations and practical implementations.

Core topics:
- Advanced principles of {lesson_title}
- Real-world applications and case studies
- Optimization techniques and best practices

Challenge yourself with the advanced exercises to master this topic!"""
        
        else:
            return f"""Understanding {lesson_title}:

This lesson builds on your existing knowledge and introduces new concepts. You'll learn both theory and practical application.

What you'll learn:
- Core concepts of {lesson_title}
- Practical examples and use cases
- Hands-on exercises to reinforce learning

You're making great progress - keep it up!"""


# Singleton instance
_quiz_generator_instance = None

def get_quiz_generator() -> AIQuizGenerator:
    """Get or create the quiz generator instance"""
    global _quiz_generator_instance
    if _quiz_generator_instance is None:
        _quiz_generator_instance = AIQuizGenerator()
    return _quiz_generator_instance
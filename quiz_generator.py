"""
Quiz Generator Module
Generates adaptive and final quizzes using AI
"""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import random
from typing import Dict, List, Any

class QuizGenerator:
    def __init__(self, api_key: str):
        """Initialize Quiz Generator with OpenAI API key"""
        self.api_key = api_key
        self.llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=2000
        )
    
    def generate_adaptive_quiz(self, topic: str, subject: str, class_level: str, 
                             difficulty: str = "easy", num_questions: int = 3) -> List[Dict]:
        """Generate adaptive quiz questions based on difficulty level"""
        
        system_prompt = f"""
        You are an expert quiz creator for {class_level} students studying {subject}.
        Create {num_questions} multiple-choice questions about "{topic}" with {difficulty} difficulty level.
        
        Difficulty Guidelines:
        - Easy: Basic recall and understanding questions
        - Medium: Application and analysis questions  
        - Hard: Synthesis and evaluation questions
        
        Format your response as a valid JSON array with this exact structure:
        [
            {{
                "question": "Question text here?",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A) Option 1",
                "explanation": "Brief explanation of why this is correct"
            }}
        ]
        
        Requirements:
        1. Questions must be appropriate for {class_level} students
        2. Use clear, simple language
        3. Avoid trick questions
        4. Make sure only one option is clearly correct
        5. Include realistic distractors
        6. Questions should test understanding, not just memorization
        """
        
        human_prompt = f"""
        Create {num_questions} {difficulty} difficulty multiple-choice questions about "{topic}" for {class_level} students studying {subject}.
        
        Topic: {topic}
        Subject: {subject}
        Class Level: {class_level}
        Difficulty: {difficulty}
        Number of Questions: {num_questions}
        
        Return only the JSON array, no additional text.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Try to parse JSON response
            try:
                questions = json.loads(response.content)
                return questions
            except json.JSONDecodeError:
                # If JSON parsing fails, create fallback questions
                return self._create_fallback_questions(topic, subject, class_level, difficulty, num_questions)
                
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return self._create_fallback_questions(topic, subject, class_level, difficulty, num_questions)
    
    def generate_final_quiz(self, topic: str, subject: str, class_level: str) -> List[Dict]:
        """Generate a comprehensive 10-question final quiz"""
        
        system_prompt = f"""
        You are an expert educator creating a comprehensive final assessment for {class_level} students.
        Create 10 multiple-choice questions about "{topic}" in {subject} that test complete understanding.
        
        Question Distribution:
        - 4 Easy questions (basic concepts and recall)
        - 4 Medium questions (application and analysis)
        - 2 Hard questions (synthesis and critical thinking)
        
        Format your response as a valid JSON array with this exact structure:
        [
            {{
                "question": "Question text here?",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A) Option 1",
                "explanation": "Brief explanation of why this is correct",
                "difficulty": "easy"
            }}
        ]
        
        Requirements:
        1. Cover different aspects of the topic
        2. Use age-appropriate language for {class_level}
        3. No repeated questions or concepts
        4. Clear, unambiguous correct answers
        5. Good distractors that test understanding
        6. Progressive difficulty throughout the quiz
        """
        
        human_prompt = f"""
        Create a comprehensive 10-question final quiz about "{topic}" for {class_level} students studying {subject}.
        
        The quiz should:
        - Test complete understanding of the topic
        - Include questions of varying difficulty
        - Cover all major concepts within the topic
        - Be fair and appropriate for the grade level
        
        Topic: {topic}
        Subject: {subject}
        Class Level: {class_level}
        
        Return only the JSON array with exactly 10 questions, no additional text.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Try to parse JSON response
            try:
                questions = json.loads(response.content)
                # Ensure we have exactly 10 questions
                if len(questions) != 10:
                    questions = questions[:10] if len(questions) > 10 else questions + self._create_fallback_questions(topic, subject, class_level, "mixed", 10 - len(questions))
                return questions
            except json.JSONDecodeError:
                # If JSON parsing fails, create fallback questions
                return self._create_fallback_questions(topic, subject, class_level, "mixed", 10)
                
        except Exception as e:
            print(f"Error generating final quiz: {e}")
            return self._create_fallback_questions(topic, subject, class_level, "mixed", 10)
    
    def _create_fallback_questions(self, topic: str, subject: str, class_level: str, 
                                 difficulty: str, num_questions: int) -> List[Dict]:
        """Create fallback questions when AI generation fails"""
        
        # Generic question templates based on subject
        templates = {
            "Mathematics": [
                {
                    "question": f"What is the main concept in {topic}?",
                    "options": ["A) Addition", "B) Subtraction", "C) Multiplication", "D) Division"],
                    "correct_answer": "A) Addition",
                    "explanation": "This is a basic concept question."
                }
            ],
            "Science": [
                {
                    "question": f"Which of the following is related to {topic}?",
                    "options": ["A) Plants", "B) Animals", "C) Water", "D) Air"],
                    "correct_answer": "A) Plants",
                    "explanation": "This relates to the topic being studied."
                }
            ],
            "Environmental Studies": [
                {
                    "question": f"What can we learn from {topic}?",
                    "options": ["A) Conservation", "B) Pollution", "C) Resources", "D) All of the above"],
                    "correct_answer": "D) All of the above",
                    "explanation": "Environmental studies covers many interconnected topics."
                }
            ]
        }
        
        # Use generic template or create simple questions
        fallback_questions = []
        base_template = templates.get(subject, templates["Science"])
        
        for i in range(num_questions):
            question = {
                "question": f"Question {i+1}: What is an important aspect of {topic}?",
                "options": [
                    f"A) Concept {i+1}",
                    f"B) Concept {i+2}",
                    f"C) Concept {i+3}",
                    f"D) All of the above"
                ],
                "correct_answer": f"A) Concept {i+1}",
                "explanation": f"This is related to understanding {topic}.",
                "difficulty": difficulty
            }
            fallback_questions.append(question)
        
        return fallback_questions
    
    def validate_quiz_questions(self, questions: List[Dict]) -> List[Dict]:
        """Validate and clean quiz questions"""
        validated_questions = []
        
        for q in questions:
            # Ensure required fields exist
            if all(key in q for key in ['question', 'options', 'correct_answer']):
                # Ensure options is a list with 4 items
                if isinstance(q['options'], list) and len(q['options']) == 4:
                    # Ensure correct_answer is in options
                    if q['correct_answer'] in q['options']:
                        validated_questions.append(q)
        
        return validated_questions
    
    def shuffle_questions(self, questions: List[Dict]) -> List[Dict]:
        """Shuffle the order of questions"""
        shuffled = questions.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def get_question_feedback(self, question: Dict, selected_answer: str) -> str:
        """Generate feedback for a quiz question"""
        is_correct = selected_answer == question['correct_answer']
        
        if is_correct:
            feedback = f"🎉 Correct! {question.get('explanation', 'Well done!')}"
        else:
            feedback = f"❌ Incorrect. The correct answer is {question['correct_answer']}. "
            feedback += question.get('explanation', 'Keep studying and try again!')
        
        return feedback

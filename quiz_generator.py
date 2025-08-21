"""
Quiz Generator Module
Generates adaptive and final quizzes using AI
Enhanced with continuous adaptive questioning
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
    
    def generate_next_adaptive_question(self, topic: str, subject: str, class_level: str, 
                                      difficulty: str = "easy", previous_wrong_answer: str = None,
                                      question_history: List[str] = None) -> Dict:
        """Generate the next adaptive question based on performance"""
        
        # Ensure question_history is a list
        if question_history is None:
            question_history = []
        
        system_prompt = f"""
        You are an expert adaptive quiz creator for {class_level} students studying {subject}.
        Create 1 multiple-choice question about "{topic}" with {difficulty} difficulty level.
        
        IMPORTANT ADAPTIVE RULES:
        - If student got previous question wrong, create a RELATED but DIFFERENT question on the same concept
        - If student is doing well, gradually increase difficulty
        - Focus on the specific area where student struggled
        - Never repeat the exact same question
        
        Difficulty Guidelines:
        - Easy: Basic recall and understanding questions
        - Medium: Application and analysis questions  
        - Hard: Synthesis and evaluation questions
        
        Format your response as a valid JSON object with this exact structure:
        {{
            "question": "Question text here?",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "A) Option 1",
            "explanation": "Brief explanation of why this is correct and how it relates to the concept",
            "concept_focus": "The specific concept this question tests",
            "difficulty": "{difficulty}"
        }}
        
        Requirements:
        1. Questions must be appropriate for {class_level} students
        2. Use clear, simple language
        3. Make sure only one option is clearly correct
        4. Include realistic distractors
        5. If previous answer was wrong, focus on that concept area
        6. Never repeat questions from history
        """
        
        human_prompt = f"""
        Create 1 {difficulty} difficulty adaptive question about "{topic}" for {class_level} students studying {subject}.
        
        Context:
        - Topic: {topic}
        - Subject: {subject}
        - Class Level: {class_level}
        - Current Difficulty: {difficulty}
        """
        
        # Add context about previous wrong answer
        if previous_wrong_answer:
            human_prompt += f"\n- Previous Wrong Answer: The student struggled with: {previous_wrong_answer}"
            human_prompt += "\n- Focus on the same concept but ask it differently to reinforce learning"
        
        # Add question history to avoid repeats
        if question_history:
            human_prompt += f"\n- Previous Questions Asked: {', '.join(question_history[-5:])}"  # Last 5 questions
            human_prompt += "\n- Make sure this question is different from previous ones"
        
        human_prompt += "\n\nReturn only the JSON object, no additional text."
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Try to parse JSON response
            try:
                question_data = json.loads(response.content)
                # Validate required fields
                if self._validate_question_data(question_data):
                    return question_data
                else:
                    return self._create_fallback_adaptive_question(topic, subject, class_level, difficulty)
            except json.JSONDecodeError:
                return self._create_fallback_adaptive_question(topic, subject, class_level, difficulty)
                
        except Exception as e:
            print(f"Error generating adaptive question: {e}")
            return self._create_fallback_adaptive_question(topic, subject, class_level, difficulty)
    
    def _validate_question_data(self, question_data: Dict) -> bool:
        """Validate question data structure"""
        required_fields = ['question', 'options', 'correct_answer', 'explanation']
        
        if not all(field in question_data for field in required_fields):
            return False
        
        if not isinstance(question_data['options'], list) or len(question_data['options']) != 4:
            return False
        
        if question_data['correct_answer'] not in question_data['options']:
            return False
        
        return True
    
    def _create_fallback_adaptive_question(self, topic: str, subject: str, class_level: str, difficulty: str) -> Dict:
        """Create fallback question when AI generation fails"""
        
        question_templates = {
            "Mathematics": {
                "easy": f"What is a basic concept in {topic}?",
                "medium": f"How do you apply {topic} in problem solving?",
                "hard": f"What is an advanced application of {topic}?"
            },
            "Science": {
                "easy": f"What is {topic}?",
                "medium": f"How does {topic} work in nature?", 
                "hard": f"What are the complex aspects of {topic}?"
            },
            "Environmental Studies": {
                "easy": f"What do we learn about {topic}?",
                "medium": f"How does {topic} affect our environment?",
                "hard": f"What are the broader implications of {topic}?"
            }
        }
        
        # Get template based on subject and difficulty
        templates = question_templates.get(subject, question_templates["Science"])
        question_text = templates.get(difficulty, templates["easy"])
        
        return {
            "question": question_text,
            "options": [
                f"A) Basic concept of {topic}",
                f"B) Advanced concept of {topic}",
                f"C) Related concept to {topic}",
                f"D) All concepts are important"
            ],
            "correct_answer": f"A) Basic concept of {topic}",
            "explanation": f"This relates to understanding the fundamental concepts of {topic}.",
            "concept_focus": f"Basic understanding of {topic}",
            "difficulty": difficulty
        }
    
    def determine_next_difficulty(self, current_difficulty: str, is_correct: bool, consecutive_correct: int, consecutive_wrong: int) -> str:
        """Determine next question difficulty based on performance"""
        
        if consecutive_wrong >= 2:
            # If student got 2+ wrong in a row, make it easier or stay same level
            if current_difficulty == "hard":
                return "medium"
            elif current_difficulty == "medium":
                return "easy"
            else:
                return "easy"  # Stay at easy level
        
        elif consecutive_correct >= 2:
            # If student got 2+ correct in a row, increase difficulty
            if current_difficulty == "easy":
                return "medium"
            elif current_difficulty == "medium":
                return "hard"
            else:
                return "hard"  # Stay at hard level
        
        else:
            # Keep current difficulty if performance is mixed
            return current_difficulty
    
    def generate_adaptive_quiz(self, topic: str, subject: str, class_level: str, 
                             difficulty: str = "easy", num_questions: int = 3) -> List[Dict]:
        """Generate adaptive quiz questions based on difficulty level (Legacy method for compatibility)"""
        
        questions = []
        for i in range(num_questions):
            question = self.generate_next_adaptive_question(topic, subject, class_level, difficulty)
            questions.append(question)
        
        return questions
    
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
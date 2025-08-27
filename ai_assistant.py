"""
AI Assistant Module
Handles all AI-powered educational content generation
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import openai
from typing import Dict, List, Any

class AIAssistant:
    def __init__(self, api_key: str):
        """Initialize AI Assistant with OpenAI API key"""
        self.api_key = api_key
        self.llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1500
        )
    
    def generate_topic_explanation(self, topic: str, subject: str, class_level: str) -> str:
        """Generate a comprehensive topic explanation suitable for the student's grade level"""
        
        system_prompt = f"""
        You are an expert teacher for AP State Board curriculum. Generate a clear, engaging, and age-appropriate explanation for {class_level} students.
        
        Guidelines:
        1. Use simple, clear language appropriate for {class_level} students
        2. Include real-world examples and analogies
        3. Break down complex concepts into smaller, digestible parts
        4. Use emojis and engaging formatting to make it interesting
        5. Include practical applications where relevant
        6. Keep explanations comprehensive but not overwhelming
        7. Focus on building conceptual understanding
        
        Subject: {subject}
        Topic: {topic}
        Class Level: {class_level}
        """
        
        human_prompt = f"""
        Please provide a detailed explanation of the topic "{topic}" from {subject} for {class_level} students following the AP State Board syllabus.
        
        Structure your explanation as follows:
        1. 🎯 **Introduction** - What is this topic about?
        2. 🔍 **Key Concepts** - Main ideas broken down simply
        3. 🌟 **Real-world Examples** - How this applies in daily life
        4. 📝 **Important Points to Remember** - Key takeaways
        5. 🚀 **Fun Facts** (if applicable) - Interesting related information
        
        Make sure the explanation is engaging, easy to understand, and encourages further learning.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"🚫 Sorry, I couldn't generate the explanation right now. Error: {str(e)}"
    
    def answer_question(self, question: str, topic: str, subject: str, class_level: str) -> str:
        """Answer student questions about the topic contextually"""
        
        system_prompt = f"""
        You are a friendly and knowledgeable teacher helping a {class_level} student with {subject}.
        The student is currently learning about "{topic}".
        
        Guidelines:
        1. Answer in a warm, encouraging tone
        2. Use language appropriate for {class_level} students
        3. Connect your answer back to the current topic when possible
        4. Provide examples to clarify concepts
        5. If the question is off-topic, gently guide back to the subject
        6. Use emojis to make responses engaging
        7. Encourage further questions and curiosity
        8. If you don't know something, admit it and suggest how to find the answer
        """
        
        human_prompt = f"""
        Student Question: "{question}"
        
        Current Topic: {topic}
        Subject: {subject}
        Class: {class_level}
        
        Please provide a helpful, encouraging response that addresses the student's question while staying relevant to their current learning context.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"🚫 Sorry, I couldn't answer your question right now. Please try again! Error: {str(e)}"
    
    def generate_study_tips(self, topic: str, subject: str, class_level: str) -> str:
        """Generate personalized study tips for the topic"""
        
        system_prompt = f"""
        You are an educational consultant providing study strategies for {class_level} students studying {subject}.
        Focus on practical, actionable study tips that are age-appropriate and effective.
        """
        
        human_prompt = f"""
        Generate specific study tips for learning "{topic}" in {subject} for {class_level} students.
        Include:
        1. 📚 Study techniques
        2. 🧠 Memory aids
        3. ⏰ Time management tips
        4. 🔄 Review strategies
        5. 🎯 Practice suggestions
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"🚫 Sorry, I couldn't generate study tips right now. Error: {str(e)}"
    
    def analyze_learning_strengths_weaknesses(self, quiz_history: List[Dict]) -> str:
        """Analyze student performance and provide insights"""
        
        if not quiz_history:
            return "📊 No quiz data available yet. Take some quizzes to get personalized insights!"
        
        # Calculate basic statistics
        total_quizzes = len(quiz_history)
        total_score = sum(quiz['score'] for quiz in quiz_history)
        total_possible = sum(quiz['total'] for quiz in quiz_history)
        average_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
        
        # Find best and worst performing topics
        topic_scores = {}
        for quiz in quiz_history:
            topic = quiz['topic']
            percentage = (quiz['score'] / quiz['total']) * 100
            if topic not in topic_scores:
                topic_scores[topic] = []
            topic_scores[topic].append(percentage)
        
        # Average scores per topic
        topic_averages = {topic: sum(scores)/len(scores) for topic, scores in topic_scores.items()}
        
        best_topics = sorted(topic_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        weak_topics = sorted(topic_averages.items(), key=lambda x: x[1])[:3]
        
        system_prompt = """
        You are an educational analyst providing personalized learning insights.
        Analyze the student's performance data and provide constructive feedback with actionable recommendations.
        """
        
        human_prompt = f"""
        Analyze this student's learning performance:
        
        📊 Overall Statistics:
        - Total Quizzes Taken: {total_quizzes}
        - Average Score: {average_percentage:.1f}%
        
        🏆 Strongest Topics:
        {chr(10).join([f"- {topic}: {score:.1f}%" for topic, score in best_topics])}
        
        📚 Areas for Improvement:
        {chr(10).join([f"- {topic}: {score:.1f}%" for topic, score in weak_topics])}
        
        Provide:
        1. 👍 Strengths analysis
        2. 📈 Areas for improvement
        3. 🎯 Specific recommendations
        4. 📅 Study plan suggestions
        5. 💪 Motivational feedback
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"🚫 Sorry, I couldn't analyze your performance right now. Error: {str(e)}"
    
    def generate_interactive_hint(self, question: Dict, student_input: str, hint_level: int, 
                                subject: str, class_level: str, topic: str) -> str:
        """Generate progressive interactive hints for quiz questions"""
        
        question_text = question.get('question', '')
        correct_answer = question.get('correct_answer', '')
        all_options = question.get('options', [])
        explanation = question.get('explanation', '')
        
        system_prompt = f"""
        You are an expert tutor for {class_level} students studying {subject}, specifically the topic "{topic}".
        Your goal is to help students solve THIS SPECIFIC QUESTION step by step WITHOUT giving away the full answer immediately.
        
        QUESTION DETAILS:
        Question: {question_text}
        Options: {all_options}
        Correct Answer: {correct_answer}
        Explanation: {explanation}
        
        HINT STRATEGY - Make hints SPECIFIC to this question:
        - Level 1: Analyze the question, identify key concepts, point out what to look for IN THIS QUESTION
        - Level 2: Give specific approach/method to solve THIS PARTICULAR QUESTION  
        - Level 3: Provide step-by-step direction for THIS QUESTION, eliminate wrong options
        - Level 4+: Give the complete solution with detailed explanation
        
        CURRENT CONTEXT:
        Student's previous input: "{student_input}"
        Current hint level: {hint_level}
        
        CRITICAL RULES:
        1. Generate SPECIFIC hints that directly help solve THIS question, not generic study advice
        2. Focus on the actual content, numbers, concepts, and data in THIS question
        3. Point out specific keywords, terms, or information in THIS question
        4. Guide them through the actual problem-solving process for THIS question
        5. Use the question content to create targeted, helpful hints
        6. Be encouraging and use emojis
        """
        
        if hint_level == 1:
            human_prompt = f"""
            This is the FIRST hint for this specific question: "{question_text}"
            
            Analyze THIS EXACT QUESTION and provide a targeted first hint that:
            1. Identifies the specific concept being tested in THIS question
            2. Points out the most important keywords, numbers, or data in THIS question  
            3. Explains what the student should focus on to solve THIS specific question
            4. Gives a specific approach or method to start solving THIS question
            5. Does NOT reveal the answer directly
            
            Start with: "👋 Hi! I'm your tutor for this question.

            My goal: Help you solve this step by step, WITHOUT giving away the full answer immediately!
            
            How I work: 🔍 I'll give you progressive hints 💭 Wait for your response before the next hint
            
            📝 Guide you through the problem-solving process ✨ Only show the complete solution if you really need it
            
            Your first hint: [Generate a SPECIFIC hint about THIS question's content, keywords, numbers, or approach]"
            
            Examples of GOOD specific hints:
            - "Look at the number 25 in the question - this tells us about..."
            - "The key word 'photosynthesis' in this question means we need to think about..."
            - "This question is asking you to calculate... focus on the given values of..."
            - "Notice the question asks 'which of the following' - this means you need to compare..."
            
            Make your hint specific to what's actually written in THIS question.
            """
        else:
            human_prompt = f"""
            This is hint level {hint_level} for the question: "{question_text}"
            Student's previous response: "{student_input}"
            
            Based on the student's response and hint level {hint_level}, provide the next progressive hint that:
            1. Responds directly to what the student said
            2. Builds on previous hints with more specific guidance about THIS question
            3. If level 2: Give more detailed approach or method for solving THIS specific question
            4. If level 3: Guide through step-by-step process for THIS question, maybe eliminate some wrong options
            5. If level 4+: Provide complete solution with detailed explanation of how to solve THIS question
            
            Focus on the specific content and details of THIS question, not general study advice.
            Use the actual question data to help them solve it.
            """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            # Provide a more specific fallback based on the actual question
            if hint_level == 1:
                # Extract key info from the question for a specific fallback
                question_keywords = []
                if any(word in question_text.lower() for word in ['calculate', 'find', 'solve']):
                    question_keywords.append("calculation")
                if any(word in question_text.lower() for word in ['what', 'which', 'identify']):
                    question_keywords.append("identification")
                if any(char.isdigit() for char in question_text):
                    question_keywords.append("numerical values")
                
                return f"""👋 Hi! I'm your tutor for this question.
My goal: Help you solve this step by step, WITHOUT giving away the full answer immediately!

🔍 Your first hint: Look carefully at this question: "{question_text[:100]}..." 

I notice this question involves {', '.join(question_keywords) if question_keywords else 'key concepts'}. Focus on identifying what specific information is given and what exactly you need to find. 

What part of this question stands out to you as most important? 🤔"""
            else:
                return f"Let me help you with this question! Looking at your response '{student_input}', what specific part of the question would you like me to explain further? 🤔"

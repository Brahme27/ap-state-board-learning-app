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

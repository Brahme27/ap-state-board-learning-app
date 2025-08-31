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
            max_tokens=2000
        )
    
    def generate_topic_explanation(self, topic: str, subject: str, class_level: str, user_preferences: Dict = None) -> str:
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
        
        # Add user preference personalization if available
        if user_preferences:
            system_prompt += "\n\n----- IMPORTANT: REQUIRED PERSONALIZATION -----"
            system_prompt += "\nYou MUST personalize this explanation based on the following student preferences:"
            
            if user_preferences.get('activities'):
                activities = ', '.join(user_preferences['activities'][:3])
                system_prompt += f"\n- ACTIVITIES: Integrate references, analogies, and examples related to: {activities}"
            
            if user_preferences.get('storytelling_styles'):
                styles = ', '.join(user_preferences['storytelling_styles'][:3])
                system_prompt += f"\n- STORYTELLING: Structure your explanation using these styles: {styles}"
            
            if user_preferences.get('memory_techniques'):
                techniques = ', '.join(user_preferences['memory_techniques'])
                system_prompt += f"\n- MEMORY TECHNIQUES: Apply these specific learning techniques throughout: {techniques}"
            
            if user_preferences.get('learning_approach'):
                system_prompt += f"\n- LEARNING APPROACH: Your explanation MUST follow this approach: {user_preferences['learning_approach']}"
            
            if user_preferences.get('difficulty_preference'):
                system_prompt += f"\n- DIFFICULTY STRUCTURE: Present information according to this preference: {user_preferences['difficulty_preference']}"
            
            system_prompt += "\n\nFor each section of your explanation, explicitly incorporate these personalization elements."
            system_prompt += "\nThis personalization is MANDATORY and should be obvious in your explanation."
        
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
        
        # Add a personalization reminder if preferences exist
        if user_preferences:
            human_prompt += """
            
            CRITICAL: Your explanation MUST be heavily personalized based on the student's preferences. 
            Make the personalization obvious by:
            1. Choosing examples that directly relate to their interests
            2. Using their preferred storytelling styles throughout
            3. Applying their preferred memory techniques in key points
            4. Following their preferred learning approach
            5. Structuring difficulty according to their preference
            
            The personalization should be evident in every section of your explanation.
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
    
    def generate_interactive_hint(self, question: Dict[str, Any], student_input: str, hint_level: int, 
                            subject: str, class_level: str, topic: str) -> str:
        """Generate progressive interactive hints for quiz questions"""
        
        # Extract question components
        question_text = question.get('question', '')
        correct_answer = question.get('correct_answer', '')
        all_options = question.get('options', [])
        explanation = question.get('explanation', '')
        
        # Extract key components from the question for analysis
        question_keywords = []
        numerical_values = []
        
        # Find numbers in the question
        import re
        numbers = re.findall(r'\b\d+\.?\d*\b', question_text)
        if numbers:
            numerical_values = numbers[:3]  # Take first 3 numbers found
        
        # Find key subject-specific terms
        subject_keywords = {
            'Mathematics': ['calculate', 'solve', 'find', 'area', 'volume', 'percentage', 'fraction', 'decimal', 'equation', 'formula'],
            'Science': ['photosynthesis', 'respiration', 'digestion', 'circulation', 'gravity', 'force', 'energy', 'matter', 'chemical', 'physical'],
            'Environmental Studies': ['pollution', 'conservation', 'ecosystem', 'biodiversity', 'natural resources', 'climate', 'environment', 'sustainable'],
            'English': ['noun', 'verb', 'adjective', 'sentence', 'paragraph', 'story', 'character', 'setting', 'plot', 'theme'],
            'Social Studies': ['history', 'geography', 'government', 'democracy', 'civilization', 'culture', 'society', 'economy', 'trade']
        }
        
        relevant_keywords = subject_keywords.get(subject, [])
        for keyword in relevant_keywords:
            if keyword.lower() in question_text.lower():
                question_keywords.append(keyword)
        
        # Analyze the options to understand the question type
        option_analysis = ""
        if all_options:
            # Check if it's a calculation question
            if any(char.isdigit() for option in all_options for char in option):
                option_analysis = "This appears to be a calculation-based question."
            # Check if it's a definition question
            elif any(word in ' '.join(all_options).lower() for word in ['is', 'are', 'means', 'refers']):
                option_analysis = "This appears to be a definition or concept identification question."
            # Check if it's a process question
            elif any(word in ' '.join(all_options).lower() for word in ['first', 'second', 'step', 'process']):
                option_analysis = "This appears to be about understanding a process or sequence."
        
        system_prompt = f"""
        You are an expert tutor for {class_level} students studying {subject}, specifically the topic "{topic}".
        Your goal is to help students solve THIS SPECIFIC QUESTION step by step using progressive hints.
        
        QUESTION ANALYSIS:
        Question: {question_text}
        Options: {all_options}
        Correct Answer: {correct_answer}
        Explanation: {explanation}
        Keywords Found: {question_keywords}
        Numbers Found: {numerical_values}
        Question Type: {option_analysis}
        
        PROGRESSIVE HINT STRATEGY:
        Level 1: Point out SPECIFIC elements in this question (keywords, numbers, concepts) and what to focus on
        Level 2: Guide through the thinking process - what method/approach to use for THIS question
        Level 3: Give more detailed steps, eliminate obviously wrong options, provide partial solution
        Level 4+: Provide complete solution with step-by-step working
        
        CURRENT CONTEXT:
        Student's response: "{student_input}"
        Hint Level: {hint_level}
        
        CRITICAL REQUIREMENTS:
        1. Be SPECIFIC to this question's content - use the actual numbers, terms, and data from the question
        2. Build on the student's previous response if they provided one
        3. Make each hint progressively more revealing
        4. Use encouraging language and emojis
        5. For calculation questions, show the actual calculation steps
        6. For concept questions, break down the concept specifically as it applies to this question
        """
        
        if hint_level == 1:
            # First hint - analyze the question and point out key elements
            hint_elements = []
            
            if numerical_values:
                hint_elements.append(f"I notice the numbers {', '.join(numerical_values)} in this question")
            
            if question_keywords:
                hint_elements.append(f"The key concept here is about {', '.join(question_keywords)}")
            
            # Identify what type of question this is based on question words
            if any(word in question_text.lower() for word in ['what is', 'which is', 'what does']):
                hint_elements.append("This is asking you to identify or define something")
            elif any(word in question_text.lower() for word in ['how', 'calculate', 'find']):
                hint_elements.append("This requires you to work through a process or calculation")
            elif any(word in question_text.lower() for word in ['why', 'because', 'reason']):
                hint_elements.append("This is asking you to explain reasoning or cause-effect")
            
            specific_focus = ""
            if subject == "Mathematics" and numerical_values:
                specific_focus = f"Focus on what operation you need to perform with these numbers: {', '.join(numerical_values)}"
            elif subject == "Science" and question_keywords:
                specific_focus = f"Think about how {question_keywords[0]} works in this context" if question_keywords else ""
            elif "percentage" in question_text.lower():
                specific_focus = "This is a percentage problem - think about the formula: (part/whole) × 100"
            elif "area" in question_text.lower():
                specific_focus = "This is asking about area - remember the formula depends on the shape"
            
            human_prompt = f"""
            Generate the FIRST hint for this question: "{question_text}"
            
            Start with: "👋 Hi! I'm your tutor for this question. Let me help you solve this step by step!
            
            🎯 My goal: Guide you through the solution without giving away the answer immediately.
            
            💭 How I work: I'll give you progressive hints and wait for your thoughts before the next hint.
            
            📝 First, let's analyze this question together:
            
            Your first hint should:
            1. Point out the specific elements: {hint_elements}
            2. {specific_focus if specific_focus else 'Identify what the question is really asking'}
            3. Give them a specific starting point or approach
            4. Ask them what they think about these elements
            
            Make it engaging and specific to THIS question's content!"
            """
            
        elif hint_level == 2:
            human_prompt = f"""
            The student responded: "{student_input}"
            
            Now provide the SECOND progressive hint that:
            1. Acknowledges their response positively
            2. Guides them toward the correct method/approach for THIS specific question
            3. If it's a calculation: show them what formula or operation to use
            4. If it's a concept: break down the concept as it applies here
            5. Give them a more specific direction without revealing the answer
            6. Use the actual content from the question (numbers: {numerical_values}, keywords: {question_keywords})
            """
            
        elif hint_level == 3:
            human_prompt = f"""
            The student responded: "{student_input}"
            
            Provide the THIRD progressive hint that:
            1. Builds on their understanding so far
            2. Shows partial working/steps for THIS question
            3. Eliminates 1-2 obviously wrong options from: {all_options}
            4. Gives them most of the solution process but lets them complete it
            5. If it's calculation: show the setup and maybe first step of calculation
            6. Be very specific to this question's data and context
            """
            
        elif hint_level >= 4:
            human_prompt = f"""
            The student has asked for more help. Provide the COMPLETE solution:
            
            1. Show the full step-by-step solution for this specific question
            2. Use the actual numbers and data from the question: {numerical_values}
            3. Explain WHY the correct answer is: {correct_answer}
            4. Show all calculation steps if it's a math problem
            5. Explain the reasoning clearly
            6. Connect it back to the topic: {topic}
            7. End with encouragement about understanding the concept
            
            The student responded: "{student_input}"
            Be comprehensive but still encouraging!
            """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            # Enhanced fallback based on hint level and question content
            if hint_level == 1:
                fallback_hint = f"👋 Hi! I'm your tutor for this question.\n\n🎯 Let's look at this question: \"{question_text}\"\n\n"
                
                if numerical_values:
                    fallback_hint += f"🔢 I notice there are numbers in this question: {', '.join(numerical_values)}. "
                
                if question_keywords:
                    fallback_hint += f"📖 This question is about {', '.join(question_keywords)}. "
                
                if "calculate" in question_text.lower() or numerical_values:
                    fallback_hint += "This looks like a calculation problem. What operation do you think we need to use? 🤔"
                elif "what is" in question_text.lower():
                    fallback_hint += "This is asking you to identify something. Look at the options and think about which one best fits. 🤔"
                else:
                    fallback_hint += "Think about what this question is really asking. What's the main concept being tested? 🤔"
                    
                return fallback_hint
                
            elif hint_level == 2:
                return f"Good thinking! Now let's focus on the key part of this question. Looking at \"{question_text}\", what specific approach or method should we use? Think about the main concept of {topic}. 💡"
                
            elif hint_level == 3:
                wrong_options = [opt for opt in all_options if opt != correct_answer][:2] if all_options else []
                return f"Let me help you narrow it down! We can eliminate these options: {', '.join(wrong_options)} because they don't fit the question. Now focus on the remaining choices. What do you think? 🎯"
                
            else:
                return f"Here's the complete solution: The correct answer is {correct_answer}. {explanation if explanation else 'This relates to the key concepts of ' + topic + '.'} Now you can see how to approach similar questions! 🌟"
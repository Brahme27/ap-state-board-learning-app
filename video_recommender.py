"""
Video Recommender Module
Finds educational YouTube videos for topics
"""

from youtubesearchpython import VideosSearch
import requests
from typing import List, Dict, Any
import re

class VideoRecommender:
    def __init__(self):
        """Initialize Video Recommender"""
        self.educational_channels = [
            "Khan Academy",
            "BYJU'S",
            "Vedantu",
            "Unacademy",
            "NCERT Official",
            "ExamFear Education",
            "Physics Wallah",
            "Crash Course",
            "TED-Ed",
            "National Geographic Kids"
        ]
    
    def search_educational_videos(self, topic: str, subject: str, class_level: str, 
                                limit: int = 5) -> List[Dict]:
        """Search for educational videos related to the topic"""
        
        # Create search query
        search_queries = self._generate_search_queries(topic, subject, class_level)
        
        all_videos = []
        
        for query in search_queries:
            try:
                videos = self._search_youtube_videos(query, limit)
                all_videos.extend(videos)
            except Exception as e:
                print(f"Error searching for videos with query '{query}': {e}")
                continue
        
        # Filter and rank videos
        filtered_videos = self._filter_educational_videos(all_videos)
        ranked_videos = self._rank_videos(filtered_videos, topic, subject)
        
        return ranked_videos[:limit]
    
    def _generate_search_queries(self, topic: str, subject: str, class_level: str) -> List[str]:
        """Generate multiple search queries for better video discovery"""
        
        # Extract class number for search
        class_num = re.findall(r'\d+', class_level)
        grade = class_num[0] if class_num else ""
        
        queries = [
            f"{topic} {subject} class {grade} explanation",
            f"{topic} {subject} grade {grade} tutorial",
            f"{topic} for students educational video",
            f"{subject} {topic} easy explanation",
            f"learn {topic} {subject} basics",
            f"{topic} {subject} NCERT class {grade}",
            f"{topic} concepts {subject} students"
        ]
        
        return queries
    
    def _search_youtube_videos(self, query: str, limit: int) -> List[Dict]:
        """Search YouTube for videos using the query"""
        
        try:
            videos_search = VideosSearch(query, limit=limit)
            results = videos_search.result()
            
            videos = []
            for video in results['result']:
                video_data = {
                    'title': video.get('title', ''),
                    'url': video.get('link', ''),
                    'duration': video.get('duration', ''),
                    'views': video.get('viewCount', {}).get('text', ''),
                    'channel': video.get('channel', {}).get('name', ''),
                    'thumbnail': video.get('thumbnails', [{}])[0].get('url', ''),
                    'description': video.get('descriptionSnippet', [{}])[0].get('text', '') if video.get('descriptionSnippet') else '',
                    'published': video.get('publishedTime', '')
                }
                videos.append(video_data)
            
            return videos
            
        except Exception as e:
            print(f"Error in YouTube search: {e}")
            return []
    
    def _filter_educational_videos(self, videos: List[Dict]) -> List[Dict]:
        """Filter videos to keep only educational content"""
        
        educational_keywords = [
            'tutorial', 'explanation', 'learn', 'education', 'class', 'grade',
            'lesson', 'concept', 'basics', 'introduction', 'understand',
            'ncert', 'cbse', 'state board', 'syllabus', 'chapter'
        ]
        
        non_educational_keywords = [
            'song', 'music', 'dance', 'funny', 'comedy', 'prank',
            'gaming', 'entertainment', 'movie', 'trailer'
        ]
        
        filtered_videos = []
        
        for video in videos:
            title_lower = video['title'].lower()
            description_lower = video['description'].lower()
            channel_lower = video['channel'].lower()
            
            # Check for educational keywords
            has_educational_content = any(
                keyword in title_lower or 
                keyword in description_lower or 
                keyword in channel_lower
                for keyword in educational_keywords
            )
            
            # Check for non-educational keywords
            has_non_educational_content = any(
                keyword in title_lower or 
                keyword in description_lower
                for keyword in non_educational_keywords
            )
            
            # Check if channel is in educational channels list
            is_educational_channel = any(
                edu_channel.lower() in channel_lower
                for edu_channel in self.educational_channels
            )
            
            # Include video if it's educational and not non-educational
            if (has_educational_content or is_educational_channel) and not has_non_educational_content:
                filtered_videos.append(video)
        
        return filtered_videos
    
    def _rank_videos(self, videos: List[Dict], topic: str, subject: str) -> List[Dict]:
        """Rank videos based on relevance and quality indicators"""
        
        ranked_videos = []
        
        for video in videos:
            score = 0
            
            # Title relevance
            title_lower = video['title'].lower()
            topic_lower = topic.lower()
            subject_lower = subject.lower()
            
            if topic_lower in title_lower:
                score += 3
            if subject_lower in title_lower:
                score += 2
            
            # Channel reputation (educational channels get higher score)
            channel_lower = video['channel'].lower()
            for edu_channel in self.educational_channels:
                if edu_channel.lower() in channel_lower:
                    score += 4
                    break
            
            # Duration preference (5-20 minutes is ideal for educational content)
            duration = video.get('duration', '')
            if duration:
                # Parse duration to estimate if it's in good range
                if '5:' in duration or '6:' in duration or '7:' in duration or '8:' in duration or '9:' in duration:
                    score += 2
                elif '10:' in duration or '11:' in duration or '12:' in duration or '15:' in duration:
                    score += 3
                elif '20:' in duration or '25:' in duration:
                    score += 1
            
            # Views indicator (more views can indicate quality, but not always)
            views_text = video.get('views', '')
            if 'K' in views_text or 'M' in views_text:
                score += 1
            
            video['relevance_score'] = score
            ranked_videos.append(video)
        
        # Sort by score in descending order
        ranked_videos.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return ranked_videos
    
    def get_video_categories(self) -> List[str]:
        """Get available video categories"""
        return [
            "Concept Explanation",
            "Solved Examples", 
            "Practice Problems",
            "Real-world Applications",
            "Revision Videos",
            "Exam Preparation"
        ]
    
    def search_by_category(self, topic: str, subject: str, class_level: str, 
                          category: str) -> List[Dict]:
        """Search videos by specific category"""
        
        category_keywords = {
            "Concept Explanation": ["explanation", "concept", "theory", "basics"],
            "Solved Examples": ["solved", "examples", "problems", "solutions"],
            "Practice Problems": ["practice", "problems", "exercises", "worksheet"],
            "Real-world Applications": ["applications", "real world", "uses", "practical"],
            "Revision Videos": ["revision", "review", "summary", "quick"],
            "Exam Preparation": ["exam", "test", "preparation", "tips", "tricks"]
        }
        
        keywords = category_keywords.get(category, ["tutorial"])
        
        # Create category-specific search query
        query = f"{topic} {subject} {' '.join(keywords)} class {class_level}"
        
        try:
            videos = self._search_youtube_videos(query, 5)
            filtered_videos = self._filter_educational_videos(videos)
            return self._rank_videos(filtered_videos, topic, subject)
        except Exception as e:
            print(f"Error searching videos by category: {e}")
            return []

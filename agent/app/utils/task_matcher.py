"""Smart task matching utilities using semantic similarity and fuzzy matching."""

import re
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
from datetime import datetime
from .llm_model import get_llm_model


class TaskMatcher:
    """Smart task matcher that uses multiple strategies to find the best matching task."""
    
    def __init__(self):
        self.llm = get_llm_model()
    
    def find_best_match(self, task_identifier: str, tasks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the best matching task using multiple strategies.
        Returns the best matching task or None if no good match is found.
        """
        if not tasks:
            return None
        
        # Strategy 1: Exact title match
        exact_match = self._find_exact_match(task_identifier, tasks)
        if exact_match:
            return exact_match
        
        # Strategy 2: Fuzzy string matching
        fuzzy_matches = self._find_fuzzy_matches(task_identifier, tasks)
        if fuzzy_matches and fuzzy_matches[0][1] > 0.7:  # High confidence threshold
            return fuzzy_matches[0][0]
        
        # Strategy 3: Semantic similarity using keywords
        keyword_matches = self._find_keyword_matches(task_identifier, tasks)
        if keyword_matches and keyword_matches[0][1] > 0.6:
            return keyword_matches[0][0]
        
        # Strategy 4: LLM-based semantic matching (for complex cases)
        if fuzzy_matches and fuzzy_matches[0][1] > 0.4:  # Medium confidence
            llm_match = self._llm_assisted_match(task_identifier, [match[0] for match in fuzzy_matches[:3]])
            if llm_match:
                return llm_match
        
        return None
    
    def find_multiple_matches(self, task_identifier: str, tasks: List[Dict[str, Any]], 
                            threshold: float = 0.4) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find multiple potential matches for disambiguation.
        Returns list of (task, confidence_score) tuples.
        """
        all_matches = []
        
        # Get fuzzy matches
        fuzzy_matches = self._find_fuzzy_matches(task_identifier, tasks, threshold)
        all_matches.extend(fuzzy_matches)
        
        # Get keyword matches
        keyword_matches = self._find_keyword_matches(task_identifier, tasks, threshold)
        all_matches.extend(keyword_matches)
        
        # Remove duplicates and sort by confidence
        seen_ids = set()
        unique_matches = []
        for task, score in sorted(all_matches, key=lambda x: x[1], reverse=True):
            task_id = task.get("_id")
            if task_id not in seen_ids:
                seen_ids.add(task_id)
                unique_matches.append((task, score))
        
        return unique_matches[:5]  # Return top 5 matches
    
    def _find_exact_match(self, identifier: str, tasks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find exact title match."""
        identifier_lower = identifier.lower().strip()
        for task in tasks:
            if task.get("title", "").lower().strip() == identifier_lower:
                return task
        return None
    
    def _find_fuzzy_matches(self, identifier: str, tasks: List[Dict[str, Any]], 
                          threshold: float = 0.3) -> List[Tuple[Dict[str, Any], float]]:
        """Find fuzzy string matches."""
        matches = []
        identifier_lower = identifier.lower().strip()
        
        for task in tasks:
            title = task.get("title", "").lower().strip()
            if not title:
                continue
            
            # Calculate similarity score
            similarity = SequenceMatcher(None, identifier_lower, title).ratio()
            
            # Also check for partial matches
            if identifier_lower in title or title in identifier_lower:
                similarity = max(similarity, 0.8)
            
            if similarity >= threshold:
                matches.append((task, similarity))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def _find_keyword_matches(self, identifier: str, tasks: List[Dict[str, Any]], 
                            threshold: float = 0.3) -> List[Tuple[Dict[str, Any], float]]:
        """Find matches based on keyword overlap."""
        matches = []
        identifier_words = set(re.findall(r'\w+', identifier.lower()))
        
        if not identifier_words:
            return matches
        
        for task in tasks:
            title = task.get("title", "")
            title_words = set(re.findall(r'\w+', title.lower()))
            
            if not title_words:
                continue
            
            # Calculate Jaccard similarity (intersection over union)
            intersection = identifier_words.intersection(title_words)
            union = identifier_words.union(title_words)
            
            if union:
                similarity = len(intersection) / len(union)
                
                # Boost score if important keywords match
                important_words = {"urgent", "important", "high", "priority", "meeting", "deadline"}
                if intersection.intersection(important_words):
                    similarity += 0.2
                
                if similarity >= threshold:
                    matches.append((task, similarity))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def _llm_assisted_match(self, identifier: str, candidate_tasks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Use LLM to determine the best match among candidates."""
        if not candidate_tasks:
            return None
        
        # Format candidates for LLM
        candidates_text = ""
        for i, task in enumerate(candidate_tasks, 1):
            candidates_text += f"{i}. Title: '{task.get('title', '')}'\n"
            candidates_text += f"   Priority: {task.get('priority', 'medium')}\n"
            candidates_text += f"   Status: {task.get('status', 'pending')}\n"
            candidates_text += f"   Created: {task.get('created_at', '')}\n\n"
        
        prompt = f"""
Given the user's task identifier: "{identifier}"

And these candidate tasks:
{candidates_text}

Which task is the user most likely referring to? Consider:
1. Semantic similarity of the titles
2. Context and meaning
3. Recent activity (more recent tasks are more likely to be referenced)
4. Task priority and status

Respond with only the number (1, 2, 3, etc.) of the best matching task, or "none" if no task is a good match.
"""
        
        try:
            response = self.llm.invoke(prompt)
            result = response.content.strip().lower()
            
            # Parse the response
            if result == "none":
                return None
            
            # Try to extract number
            import re
            numbers = re.findall(r'\d+', result)
            if numbers:
                choice = int(numbers[0])
                if 1 <= choice <= len(candidate_tasks):
                    return candidate_tasks[choice - 1]
        
        except Exception as e:
            print(f"LLM matching error: {e}")
        
        return None
    
    def is_ambiguous_match(self, matches: List[Tuple[Dict[str, Any], float]]) -> bool:
        """Check if the matches are ambiguous (multiple similar confidence scores)."""
        if len(matches) < 2:
            return False
        
        # If top two matches have similar scores, it's ambiguous
        top_score = matches[0][1]
        second_score = matches[1][1]
        
        return abs(top_score - second_score) < 0.2


# Global task matcher instance
task_matcher = TaskMatcher()
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import re

class TaskDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        
    async def connect(self):
        """Connect to MongoDB"""
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client.task_manager
        self.collection = self.db.tasks
        
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    async def add_task(self, title: str, date: Optional[str] = None, 
                      priority: str = "medium", status: str = "pending") -> Dict[str, Any]:
        """Add a new task"""
        try:
            if date:
                task_date = self._parse_date(date)
            else:
                task_date = datetime.now()
            
            task = {
                "title": title,
                "date": task_date,
                "priority": priority.lower(),
                "status": status.lower(),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result = await self.collection.insert_one(task)
            task["_id"] = str(result.inserted_id)
            
            return {
                "success": True,
                "message": f"Task '{title}' added successfully",
                "task": task
            }
        except Exception as e:
            print(f"Error adding task: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to add task: {str(e)}"
            }
    
    async def get_tasks(self, date_range: Optional[str] = None, 
                       priority_filter: Optional[str] = None,
                       status_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get tasks based on filters"""
        try:
            query = {}
            
            # Date filter
            if date_range:
                date_filter = self._build_date_filter(date_range)
                if date_filter:
                    query["date"] = date_filter
            
            # Priority filter
            if priority_filter:
                query["priority"] = priority_filter.lower()
            
            # Status filter  
            if status_filter:
                query["status"] = status_filter.lower()
            
            cursor = self.collection.find(query).sort("date", 1)
            tasks = await cursor.to_list(length=100)
            
            # Convert ObjectId to string
            for task in tasks:
                task["_id"] = str(task["_id"])
            
            return {
                "success": True,
                "tasks": tasks,
                "count": len(tasks)
            }
        except Exception as e:
            print(f"Error getting tasks: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get tasks: {str(e)}"
            }
    
    async def update_task(self, task_identifier: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task"""
        # TODO: Implement smarter task matching
        #  this should:
        # 1. Fetch all tasks from the database
        # 2. Use semantic similarity or fuzzy matching to find the closest match to user's prompt
        # 3. Consider task content, context, and user intent
        # 4. Possibly use LLM to understand which task the user is referring to
        # 5. Handle ambiguous cases by asking for clarification
        # lets just return True for now
        return {
            "success": True,
            "message": f"Task matching '{task_identifier}' would be updated (smart matching not implemented yet)"
        }
    
    async def delete_task(self, task_identifier: str) -> Dict[str, Any]:
        """Delete a task"""
        # TODO: Implement smarter task matching
        #  this should:
        # 1. Fetch all tasks from the database
        # 2. Use semantic similarity or fuzzy matching to find the closest match to user's prompt
        # 3. Analyze task content, title, description, and context
        # 4. Possibly use LLM to understand which task the user is referring to
        # 5. Handle cases where multiple tasks match and ask for clarification
        # 6. Consider task priority, recency, and relevance in matching
        # lets just return True for now        
        return {
            "success": True,
            "message": f"Task matching '{task_identifier}' would be deleted (smart matching not implemented yet)"
        }
    
    async def mark_done(self, task_identifier: str) -> Dict[str, Any]:
        """Mark a task as done"""
        return await self.update_task(task_identifier, {"status": "done"})
    
    async def set_priority(self, task_identifier: str, priority: str) -> Dict[str, Any]:
        """Set task priority"""
        if priority.lower() not in ["high", "medium", "low"]:
            return {
                "success": False,
                "message": "Priority must be high, medium, or low"
            }
        return await self.update_task(task_identifier, {"priority": priority})
    
    async def get_task_summary(self, filter_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get task summary with statistics"""
        try:
            pipeline = []
            
            # Add match stage if filters provided
            if filter_criteria:
                match_query = {}
                if "date_range" in filter_criteria:
                    date_filter = self._build_date_filter(filter_criteria["date_range"])
                    if date_filter:
                        match_query["date"] = date_filter
                if "priority" in filter_criteria:
                    match_query["priority"] = filter_criteria["priority"].lower()
                if "status" in filter_criteria:
                    match_query["status"] = filter_criteria["status"].lower()
                
                if match_query:
                    pipeline.append({"$match": match_query})
            
            # Aggregation pipeline for statistics
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_tasks": {"$sum": 1},
                        "high_priority": {
                            "$sum": {"$cond": [{"$eq": ["$priority", "high"]}, 1, 0]}
                        },
                        "medium_priority": {
                            "$sum": {"$cond": [{"$eq": ["$priority", "medium"]}, 1, 0]}
                        },
                        "low_priority": {
                            "$sum": {"$cond": [{"$eq": ["$priority", "low"]}, 1, 0]}
                        },
                        "pending_tasks": {
                            "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                        },
                        "done_tasks": {
                            "$sum": {"$cond": [{"$eq": ["$status", "done"]}, 1, 0]}
                        },
                        "tasks": {"$push": "$$ROOT"}
                    }
                }
            ])
            
            cursor = self.collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            if result:
                summary = result[0]
                # Convert ObjectIds to strings in tasks
                for task in summary["tasks"]:
                    task["_id"] = str(task["_id"])
                return {
                    "success": True,
                    "summary": summary
                }
            else:
                return {
                    "success": True,
                    "summary": {
                        "total_tasks": 0,
                        "high_priority": 0,
                        "medium_priority": 0,
                        "low_priority": 0,
                        "pending_tasks": 0,
                        "done_tasks": 0,
                        "tasks": []
                    }
                }
        except Exception as e:
            print(f"Error getting task summary: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get task summary: {str(e)}"
            }
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return datetime.now()
        
        # Handle relative dates
        date_str = date_str.lower().strip()
        now = datetime.now()
        
        if date_str in ["today", "now"]:
            return now
        elif date_str == "tomorrow":
            return now + timedelta(days=1)
        elif date_str == "yesterday":
            return now - timedelta(days=1)
        elif "next week" in date_str:
            return now + timedelta(weeks=1)
        elif "this week" in date_str:
            return now
        
        # Try to parse specific date formats
        try:
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except:
            pass
        
        return now 
    
    def _build_date_filter(self, date_range: str) -> Optional[Dict[str, Any]]:
        """Build MongoDB date filter from date range string"""
        if not date_range:
            return None
        
        date_range = date_range.lower().strip()
        now = datetime.now()
        
        if date_range == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            return {"$gte": start, "$lt": end}
        elif date_range == "tomorrow":
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            return {"$gte": start, "$lt": end}
        elif date_range == "this week":
            # Get start of week (Monday)
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(weeks=1)
            return {"$gte": start, "$lt": end}
        elif date_range == "next week":
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday) + timedelta(weeks=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(weeks=1)
            return {"$gte": start, "$lt": end}
        
        # Try to parse as specific date
        try:
            target_date = self._parse_date(date_range)
            start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            return {"$gte": start, "$lt": end}
        except:
            return None

# Global database instance
task_db = TaskDatabase()
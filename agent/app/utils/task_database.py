import os
from datetime import datetime
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from .date_utils import parse_date, build_date_filter
from .task_matcher import task_matcher

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
                task_date = parse_date(date)
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
            
            # Get all tasks after adding to show updated list
            all_tasks = await self.get_tasks()
            
            return {
                "success": True,
                "message": f"Task '{title}' added successfully",
                "task": task,
                "tasks": all_tasks.get("tasks", [])  # Include all tasks in response
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
                date_filter = build_date_filter(date_range)
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
            
            # Create a descriptive message based on filters
            filter_desc = []
            if priority_filter:
                filter_desc.append(f"{priority_filter} priority")
            if status_filter:
                filter_desc.append(f"{status_filter} status")
            if date_range:
                filter_desc.append(f"from {date_range}")
            
            if filter_desc:
                message = f"Found {len(tasks)} tasks with {', '.join(filter_desc)}"
            else:
                message = f"Retrieved all {len(tasks)} tasks" if len(tasks) > 0 else "No tasks found"
            
            return {
                "success": True,
                "message": message,
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
        """Update a task using smart matching"""
        try:
            # Get all tasks for matching
            cursor = self.collection.find({})
            all_tasks = await cursor.to_list(length=None)
            
            if not all_tasks:
                return {
                    "success": False,
                    "message": "No tasks found in database"
                }
            
            # Convert ObjectId to string for matching
            for task in all_tasks:
                task["_id"] = str(task["_id"])
            
            # Find best match
            best_match = task_matcher.find_best_match(task_identifier, all_tasks)
            
            if not best_match:
                # Check for multiple potential matches
                potential_matches = task_matcher.find_multiple_matches(task_identifier, all_tasks)
                if potential_matches:
                    match_list = "\n".join([f"- {task['title']}" for task, _ in potential_matches[:3]])
                    return {
                        "success": False,
                        "message": f"Multiple tasks found that could match '{task_identifier}'. Please be more specific.\nPotential matches:\n{match_list}",
                        "potential_matches": [task for task, _ in potential_matches[:3]]
                    }
                else:
                    return {
                        "success": False,
                        "message": f"No task found matching '{task_identifier}'"
                    }
            
            # Update the matched task
            updates["updated_at"] = datetime.now()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(best_match["_id"])},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                # Get updated list of all tasks
                updated_tasks = await self.get_tasks()
                
                return {
                    "success": True,
                    "message": f"Task '{best_match['title']}' updated successfully",
                    "matched_task": best_match,
                    "updates": updates,
                    "tasks": updated_tasks.get("tasks", [])  # Include all tasks
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to update task '{best_match['title']}'"
                }
                
        except Exception as e:
            print(f"Error updating task: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to update task: {str(e)}"
            }
    
    async def delete_task(self, task_identifier: str) -> Dict[str, Any]:
        """Delete a task using smart matching"""
        try:
            # Get all tasks for matching
            cursor = self.collection.find({})
            all_tasks = await cursor.to_list(length=None)
            
            if not all_tasks:
                return {
                    "success": False,
                    "message": "No tasks found in database"
                }
            
            # Convert ObjectId to string for matching
            for task in all_tasks:
                task["_id"] = str(task["_id"])
            
            # Find best match
            best_match = task_matcher.find_best_match(task_identifier, all_tasks)
            
            if not best_match:
                # Check for multiple potential matches
                potential_matches = task_matcher.find_multiple_matches(task_identifier, all_tasks)
                if potential_matches:
                    match_list = "\n".join([f"- {task['title']}" for task, _ in potential_matches[:3]])
                    return {
                        "success": False,
                        "message": f"Multiple tasks found that could match '{task_identifier}'. Please be more specific.\nPotential matches:\n{match_list}",
                        "potential_matches": [task for task, _ in potential_matches[:3]]
                    }
                else:
                    return {
                        "success": False,
                        "message": f"No task found matching '{task_identifier}'"
                    }
            
            # Delete the matched task
            result = await self.collection.delete_one({"_id": ObjectId(best_match["_id"])})
            
            if result.deleted_count > 0:
                # Get updated list of all tasks after deletion
                updated_tasks = await self.get_tasks()
                
                return {
                    "success": True,
                    "message": f"Task '{best_match['title']}' deleted successfully",
                    "deleted_task": best_match,
                    "tasks": updated_tasks.get("tasks", [])  # Include remaining tasks
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to delete task '{best_match['title']}'"
                }
                
        except Exception as e:
            print(f"Error deleting task: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to delete task: {str(e)}"
            }
    
    async def mark_done(self, task_identifier: str) -> Dict[str, Any]:
        """Mark a task as done"""
        result = await self.update_task(task_identifier, {"status": "completed"})
        if result.get("success"):
            result["message"] = result["message"].replace("updated", "marked as completed")
        return result
    
    async def set_priority(self, task_identifier: str, priority: str) -> Dict[str, Any]:
        """Set task priority"""
        if priority.lower() not in ["high", "medium", "low"]:
            return {
                "success": False,
                "message": "Priority must be high, medium, or low"
            }
        result = await self.update_task(task_identifier, {"priority": priority.lower()})
        if result.get("success"):
            result["message"] = f"Task priority updated to {priority}"
        return result
    
    async def get_task_summary(self, filter_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get task summary with statistics"""
        try:
            pipeline = []
            
            # Add match stage if filters provided
            if filter_criteria:
                # Handle date range filtering
                if "date_range" in filter_criteria:
                    date_filter = build_date_filter(filter_criteria["date_range"])
                    if date_filter:
                        filter_criteria["date"] = date_filter
                    del filter_criteria["date_range"]
                
                # Handle other filters (priority, status, etc.)
                pipeline.append({"$match": filter_criteria})
            
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
                        "completed_tasks": {
                            "$sum": {"$cond": [{"$in": ["$status", ["completed", "done"]]}, 1, 0]}
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
                
                # Create descriptive message
                total = summary["total_tasks"]
                completed = summary["completed_tasks"]
                pending = summary["pending_tasks"]
                message = f"Found {total} tasks: {completed} completed, {pending} pending"
                
                return {
                    "success": True,
                    "message": message,
                    "summary": summary,
                    "tasks": summary["tasks"]  # Include tasks for frontend display
                }
            else:
                return {
                    "success": True,
                    "message": "No tasks found",
                    "summary": {
                        "total_tasks": 0,
                        "high_priority": 0,
                        "medium_priority": 0,
                        "low_priority": 0,
                        "pending_tasks": 0,
                        "completed_tasks": 0,
                        "tasks": []
                    },
                    "tasks": []
                }
        except Exception as e:
            print(f"Error getting task summary: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get task summary: {str(e)}"
            }
# Global database instance
task_db = TaskDatabase()
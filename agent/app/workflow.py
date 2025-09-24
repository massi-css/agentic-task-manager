"""Main workflow orchestration for the task manager agent."""

from utils.workflow_builder import create_compiled_workflow

# Initialize the compiled workflow
task_manager_graph = create_compiled_workflow()
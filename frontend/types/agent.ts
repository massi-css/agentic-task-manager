export interface Task {
  _id: string;
  title: string;
  date: string;
  priority: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ToolLog {
  id: string;
  message: string;
  status: string;
}

export interface AgentState {
  messages?: any[];
  tool_logs?: ToolLog[];
  operation?: string;
  parameters?: {
    title?: string;
    date?: string;
    priority?: string;
    status?: string;
    date_range?: string;
    priority_filter?: string;
    status_filter?: string;
  };
  db_result?: {
    success: boolean;
    message?: string;
    tasks?: Task[];
    task?: Task;
    error?: string;
    error_type?: string;
  };
  final_response?: string;
  retry_count?: number;
}

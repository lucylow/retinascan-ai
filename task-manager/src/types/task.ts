// types/task.ts
export interface Task {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
  tags: string[];
}

export interface TaskFormData {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
  tags: string[];
}

export type FilterType = 'all' | 'active' | 'completed';
export type SortType = 'dueDate' | 'priority' | 'createdAt';


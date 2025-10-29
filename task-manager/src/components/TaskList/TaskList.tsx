// components/TaskList/TaskList.tsx
import React from 'react';
import { Task } from '../../types/task';
import { TaskItem } from '../TaskItem/TaskItem';
import { Button } from '../UI/Button';

interface TaskListProps {
  tasks: Task[];
  onToggleTask: (id: string) => void;
  onUpdateTask: (id: string, updates: Partial<Task>) => void;
  onDeleteTask: (id: string) => void;
  filter: string;
  sort: string;
  onSetFilter: (filter: any) => void;
  onSetSort: (sort: any) => void;
}

export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onToggleTask,
  onUpdateTask,
  onDeleteTask,
  filter,
  sort,
  onSetFilter,
  onSetSort,
}) => {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 text-6xl mb-4">📝</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks found</h3>
        <p className="text-gray-500">
          {filter === 'all' 
            ? 'Get started by creating your first task!' 
            : `No ${filter} tasks at the moment.`
          }
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex gap-2">
          <select
            value={filter}
            onChange={(e) => onSetFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Tasks</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
          
          <select
            value={sort}
            onChange={(e) => onSetSort(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="createdAt">Newest First</option>
            <option value="dueDate">Due Date</option>
            <option value="priority">Priority</option>
          </select>
        </div>
        
        <div className="text-sm text-gray-600">
          {tasks.length} task{tasks.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="space-y-3">
        {tasks.map(task => (
          <div key={task.id} className="group">
            <TaskItem
              task={task}
              onToggle={onToggleTask}
              onUpdate={onUpdateTask}
              onDelete={onDeleteTask}
            />
          </div>
        ))}
      </div>
    </div>
  );
};


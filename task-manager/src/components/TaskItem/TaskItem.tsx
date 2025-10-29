// components/TaskItem/TaskItem.tsx
import React, { useState } from 'react';
import { Task } from '../../types/task';
import { Button } from '../UI/Button';

interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onUpdate: (id: string, updates: Partial<Task>) => void;
  onDelete: (id: string) => void;
}

export const TaskItem: React.FC<TaskItemProps> = ({
  task,
  onToggle,
  onUpdate,
  onDelete,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);

  const handleSave = () => {
    if (editTitle.trim()) {
      onUpdate(task.id, { title: editTitle.trim() });
      setIsEditing(false);
    }
  };

  const priorityColors = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-4 transition-all duration-200 group ${
      task.completed ? 'opacity-75 bg-gray-50' : ''
    }`}>
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggle(task.id)}
          className="mt-1 h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
        />
        
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="flex-1 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSave();
                }}
              />
              <Button size="sm" onClick={handleSave}>Save</Button>
              <Button variant="secondary" size="sm" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
            </div>
          ) : (
            <div 
              className={`cursor-pointer ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}
              onDoubleClick={() => setIsEditing(true)}
            >
              <h3 className="font-medium text-lg">{task.title}</h3>
            </div>
          )}
          
          {task.description && (
            <p className="text-gray-600 mt-1 text-sm">{task.description}</p>
          )}
          
          <div className="flex flex-wrap gap-2 mt-3">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityColors[task.priority]}`}>
              {task.priority}
            </span>
            
            {task.dueDate && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                Due: {new Date(task.dueDate).toLocaleDateString()}
              </span>
            )}
            
            {task.tags.map(tag => (
              <span
                key={tag}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
        
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIsEditing(true)}
          >
            Edit
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={() => onDelete(task.id)}
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
};


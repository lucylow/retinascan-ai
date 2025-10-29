// hooks/useTasks.ts
import { useState, useEffect, useCallback } from 'react';
import { Task, TaskFormData, FilterType, SortType } from '../types/task';
import { generateUUID } from '../utils/uuid';

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<FilterType>('all');
  const [sort, setSort] = useState<SortType>('createdAt');

  // Load tasks from localStorage on mount
  useEffect(() => {
    const savedTasks = localStorage.getItem('tasks');
    if (savedTasks) {
      try {
        setTasks(JSON.parse(savedTasks));
      } catch (error) {
        console.error('Error loading tasks:', error);
      }
    }
    setLoading(false);
  }, []);

  // Save tasks to localStorage whenever tasks change
  useEffect(() => {
    if (!loading) {
      localStorage.setItem('tasks', JSON.stringify(tasks));
    }
  }, [tasks, loading]);

  const addTask = useCallback((taskData: TaskFormData) => {
    const newTask: Task = {
      id: generateUUID(),
      ...taskData,
      completed: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      tags: taskData.tags || [],
    };
    setTasks(prev => [...prev, newTask]);
  }, []);

  const updateTask = useCallback((id: string, updates: Partial<Task>) => {
    setTasks(prev =>
      prev.map(task =>
        task.id === id
          ? { ...task, ...updates, updatedAt: new Date().toISOString() }
          : task
      )
    );
  }, []);

  const deleteTask = useCallback((id: string) => {
    setTasks(prev => prev.filter(task => task.id !== id));
  }, []);

  const toggleTask = useCallback((id: string) => {
    updateTask(id, { completed: !tasks.find(task => task.id === id)?.completed });
  }, [tasks, updateTask]);

  // Filter and sort tasks
  const filteredAndSortedTasks = useCallback(() => {
    let filtered = tasks;
    
    // Apply filter
    switch (filter) {
      case 'active':
        filtered = tasks.filter(task => !task.completed);
        break;
      case 'completed':
        filtered = tasks.filter(task => task.completed);
        break;
      default:
        filtered = tasks;
    }

    // Apply sort
    return filtered.sort((a, b) => {
      switch (sort) {
        case 'dueDate':
          if (!a.dueDate) return 1;
          if (!b.dueDate) return -1;
          return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
        case 'priority':
          const priorityOrder = { high: 3, medium: 2, low: 1 };
          return priorityOrder[b.priority] - priorityOrder[a.priority];
        case 'createdAt':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        default:
          return 0;
      }
    });
  }, [tasks, filter, sort]);

  return {
    tasks: filteredAndSortedTasks(),
    addTask,
    updateTask,
    deleteTask,
    toggleTask,
    setFilter,
    setSort,
    filter,
    sort,
    loading,
  };
};


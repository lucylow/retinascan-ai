// App.tsx
import React, { useState } from 'react';
import { TaskForm } from './components/TaskForm/TaskForm';
import { TaskList } from './components/TaskList/TaskList';
import { useTasks } from './hooks/useTasks';
import { Button } from './components/UI/Button';
import { TaskFormData } from './types/task';

function App() {
  const {
    tasks,
    addTask,
    updateTask,
    deleteTask,
    toggleTask,
    setFilter,
    setSort,
    filter,
    sort,
    loading,
  } = useTasks();

  const [showForm, setShowForm] = useState(false);

  const handleAddTask = (taskData: TaskFormData) => {
    addTask(taskData);
    setShowForm(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Task Manager
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Organize your tasks efficiently with priority levels, due dates, and tags.
          </p>
        </header>

        <main className="space-y-8">
          {showForm ? (
            <TaskForm
              onSubmit={handleAddTask}
              onCancel={() => setShowForm(false)}
            />
          ) : (
            <div className="text-center">
              <Button
                onClick={() => setShowForm(true)}
                size="lg"
                className="shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
              >
                + Add New Task
              </Button>
            </div>
          )}

          <TaskList
            tasks={tasks}
            onToggleTask={toggleTask}
            onUpdateTask={updateTask}
            onDeleteTask={deleteTask}
            filter={filter}
            sort={sort}
            onSetFilter={setFilter}
            onSetSort={setSort}
          />
        </main>

        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>Tasks are saved locally in your browser</p>
        </footer>
      </div>
    </div>
  );
}

export default App;


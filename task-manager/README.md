# Task Manager

A modern, full-featured task management application built with React, TypeScript, and Tailwind CSS.

## Features

- ✅ **Task Management**: Create, update, delete, and complete tasks
- 🏷️ **Tags System**: Organize tasks with custom tags
- 📅 **Due Dates**: Set and track due dates for tasks
- ⚡ **Priority Levels**: Low, Medium, and High priority classification
- 🔍 **Filtering**: Filter tasks by All, Active, or Completed
- 📊 **Sorting**: Sort by Due Date, Priority, or Creation Date
- 💾 **Local Storage**: Persistent storage using browser localStorage
- 🎨 **Modern UI**: Beautiful, responsive design with Tailwind CSS
- ♿ **Accessible**: Keyboard navigation and proper ARIA labels
- 📱 **Responsive**: Mobile-first design

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Vite** - Build tool and dev server

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
task-manager/
├── src/
│   ├── components/
│   │   ├── TaskList/      # Task list component with filtering
│   │   ├── TaskForm/      # Task creation form
│   │   ├── TaskItem/      # Individual task component
│   │   └── UI/            # Reusable UI components
│   ├── hooks/
│   │   └── useTasks.ts    # Custom hook for task management
│   ├── types/
│   │   └── task.ts        # TypeScript type definitions
│   ├── utils/
│   │   └── dateUtils.ts   # Date utility functions
│   ├── styles/
│   │   └── globals.css    # Global styles and Tailwind imports
│   ├── App.tsx            # Main application component
│   └── main.tsx           # Application entry point
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Usage

1. **Create a Task**: Click the "Add New Task" button
2. **Fill Task Details**: Enter title, description, priority, due date, and tags
3. **Edit Task**: Double-click on a task title or click the Edit button
4. **Complete Task**: Check the checkbox next to the task
5. **Delete Task**: Click the Delete button (visible on hover)
6. **Filter Tasks**: Use the filter dropdown to view All, Active, or Completed tasks
7. **Sort Tasks**: Use the sort dropdown to organize by Due Date, Priority, or Creation Date

## Features in Detail

### Task Properties
- **Title**: Required field
- **Description**: Optional detailed description
- **Priority**: Low, Medium, or High
- **Due Date**: Optional date picker
- **Tags**: Multiple custom tags for organization

### Local Storage
All tasks are automatically saved to browser localStorage and persist across page refreshes.

### Responsive Design
The application is fully responsive and works seamlessly on desktop, tablet, and mobile devices.

## Customization

### Colors
Edit `tailwind.config.js` to customize the color scheme:

```javascript
theme: {
  extend: {
    colors: {
      // Add your custom colors
    }
  }
}
```

### Styles
Modify `src/styles/globals.css` to add custom global styles or override Tailwind defaults.

## License

This project is provided as an example implementation for educational and development purposes.


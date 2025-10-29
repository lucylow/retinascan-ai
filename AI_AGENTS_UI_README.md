# Multi-Agent AI Dashboard - UI/UX Documentation

## 🎨 Overview

A comprehensive, modern UI/UX dashboard for monitoring and interacting with the RetinaScan AI Multi-Agent System. The dashboard provides real-time monitoring, workflow visualization, and detailed diagnostic results.

## 📍 Access

Navigate to: **`/ai-agents`** route in your application

Example: `http://localhost:5173/ai-agents`

## 🎯 Features

### 1. Real-Time Agent Monitoring
- **Live Status**: See which agents are online, offline, or processing
- **Performance Metrics**: Tasks processed, success rates, average processing times
- **Current Tasks**: View what each agent is currently working on
- **Visual Indicators**: Color-coded status badges and icons

### 2. Image Upload & Processing
- **Drag & Drop**: Intuitive drag-and-drop interface
- **File Selection**: Click to browse and select images
- **Supported Formats**: JPG, PNG, DICOM
- **Processing Feedback**: Real-time progress indicators
- **Image Guidelines**: Built-in tips for best results

### 3. Workflow Visualization
- **Step-by-Step Progress**: Track each stage of processing
- **Status Tracking**: See workflows as they move through the pipeline
- **History**: View recent workflows with timestamps
- **Error Handling**: Clear error messages and retry options

### 4. Diagnostic Results
- **Comprehensive Reports**: Detailed diagnostic findings
- **Clinical Assessment**: Urgency levels, risk factors, recommendations
- **Visual Hierarchy**: Color-coded urgency indicators
- **Export Options**: Download and share capabilities

### 5. System Analytics
- **Performance Metrics**: Overall system statistics
- **Agent Performance**: Individual agent statistics
- **Success Rates**: Track system reliability
- **Throughput**: Monitor processing capacity

## 🏗️ Architecture

### Components Structure

```
src/
├── components/
│   ├── AIAgentsDashboard.tsx          # Main dashboard component
│   ├── AIAgentsDashboard.css          # Dashboard styles
│   └── ai-agents/
│       ├── AgentCard.tsx              # Individual agent display
│       ├── ImageUploadArea.tsx        # Upload interface
│       ├── WorkflowList.tsx           # Workflow history
│       ├── WorkflowResults.tsx        # Results display
│       └── SystemMetrics.tsx          # System analytics
├── services/
│   └── aiAgentService.ts              # API communication
└── pages/
    └── AIAgentsDashboardPage.tsx      # Page wrapper
```

### Data Flow

1. **Initialization**: Dashboard connects to backend API
2. **Polling**: Updates metrics every 2 seconds
3. **User Action**: User uploads image
4. **Processing**: Image sent to multi-agent workflow
5. **Updates**: Real-time progress updates via polling
6. **Results**: Final diagnostic report displayed

## 🎨 Design System

### Color Palette
- **Primary**: `#667eea` (Purple gradient)
- **Success**: `#48bb78` (Green)
- **Warning**: `#ed8936` (Orange)
- **Error**: `#e53e3e` (Red)
- **Info**: `#4299e1` (Blue)

### Typography
- **Font Family**: Inter, system fonts
- **Headings**: Bold, 1.25-1.5rem
- **Body**: Regular, 0.875rem
- **Labels**: Medium weight, 0.75rem

### Layout
- **Grid System**: 3-column layout (Agents | Workflow | Results)
- **Responsive**: Adapts to smaller screens
- **Glass Morphism**: Translucent panels with blur effects
- **Spacing**: Consistent 1rem base unit

### Components

#### Agent Card
- **Background**: White with border
- **Hover**: Border color change + shadow
- **Processing**: Gradient background
- **Status Badge**: Color-coded indicator

#### Upload Zone
- **Default**: Dashed border, light background
- **Drag Over**: Border highlights
- **Processing**: Disabled state with spinner

#### Workflow Item
- **Default**: White card with border
- **Selected**: Highlighted border + background
- **Progress Bar**: Gradient fill with percentage

#### Result Card
- **Urgency Levels**: Color-coded borders
- **Emergency**: Red border + light red background
- **Normal**: Blue border

## 📱 Responsive Design

### Desktop (>1200px)
- 3-column grid layout
- Full-height panels
- Side-by-side display

### Tablet (768px - 1200px)
- 2-column grid (Agents + Workflow)
- Results panel full width below

### Mobile (<768px)
- Single column stack
- Full-width panels
- Reduced padding

## 🔌 API Integration

### Service: `aiAgentService.ts`

Handles all backend communication:

- `processImage()`: Upload and process image
- `getSystemMetrics()`: Fetch system statistics
- `getAgentStatuses()`: Get agent information
- `getWorkflowStatus()`: Check specific workflow
- `getRecentWorkflows()`: Get workflow history
- `healthCheck()`: Verify system connectivity

### API Base URL

Configure via environment variable:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 🚀 Getting Started

### 1. Backend Setup

Ensure your FastAPI backend has the multi-agent endpoints (see `AI_AGENTS_BACKEND_API.md`)

### 2. Frontend Configuration

Set the API base URL in `.env`:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Access Dashboard

Navigate to `/ai-agents` in your browser

### 4. Test Upload

Try uploading a retinal image to see the workflow in action

## 🐛 Troubleshooting

### Dashboard Shows "System Offline"
- Check if backend is running
- Verify `VITE_API_BASE_URL` is correct
- Check browser console for CORS errors
- Ensure `/ai-agent/health` endpoint exists

### Images Not Processing
- Verify image format is supported (JPG, PNG, DICOM)
- Check file size (max 16MB typically)
- Look for errors in browser console
- Verify backend `/ai-agent/process` endpoint

### No Agent Data
- Check if agents are initialized in backend
- Verify `/ai-agent/agents` endpoint returns data
- Check network tab for API responses

### Metrics Not Updating
- Verify polling interval (2 seconds)
- Check if `/ai-agent/metrics` endpoint exists
- Look for console errors
- Verify WebSocket or polling is working

## 🎯 User Experience

### Interactions

1. **Upload Image**
   - Drag & drop or click to select
   - Immediate visual feedback
   - Processing animation

2. **Monitor Progress**
   - Real-time workflow updates
   - Step-by-step progress bar
   - Live status indicators

3. **View Results**
   - Click workflow to see details
   - Expandable sections
   - Color-coded urgency

4. **Analyze Performance**
   - System metrics overview
   - Agent-specific stats
   - Historical data

### Feedback Mechanisms

- **Visual**: Icons, colors, animations
- **Textual**: Status messages, descriptions
- **Progress**: Bars, percentages
- **Errors**: Clear error messages with retry options

## 🔮 Future Enhancements

- [ ] WebSocket for real-time updates
- [ ] Export reports as PDF
- [ ] Email sharing functionality
- [ ] Advanced filtering and search
- [ ] Agent activity timeline
- [ ] Performance charts and graphs
- [ ] Notification system
- [ ] Dark mode support
- [ ] Multi-language support
- [ ] Keyboard shortcuts

## 📚 Related Documentation

- `AI_AGENTS_BACKEND_API.md` - Backend API endpoints
- `MULTI_AGENT_README.md` - Multi-agent system overview
- `MULTI_AGENT_SETUP.md` - Setup and integration guide

## 🎉 Summary

The Multi-Agent AI Dashboard provides a comprehensive, user-friendly interface for interacting with the RetinaScan AI system. With real-time monitoring, intuitive workflows, and detailed diagnostics, it offers a complete solution for managing AI-powered retinal analysis.

---

**Built with** ❤️ **for healthcare professionals**


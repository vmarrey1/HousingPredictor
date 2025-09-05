# Video PDF Summarizer - Frontend

A modern Next.js TypeScript frontend for the Video PDF Summarizer application.

## Features

- **Modern UI**: Built with Tailwind CSS and Framer Motion for smooth animations
- **Dual Input Methods**: Support for YouTube URLs and direct video file uploads
- **Drag & Drop**: Intuitive file upload with drag and drop functionality
- **Real-time Feedback**: Toast notifications and loading states
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **React Dropzone**: File upload handling
- **React Hot Toast**: Notification system
- **Axios**: HTTP client for API calls
- **Lucide React**: Beautiful icons

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main page component
├── components/              # Reusable components
├── public/                  # Static assets
├── package.json
├── tailwind.config.js       # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
└── next.config.js          # Next.js configuration
```

## API Integration

The frontend communicates with the Flask backend through:
- `/api/process-video` - Process YouTube videos
- `/api/upload-video` - Process uploaded video files
- `/api/health` - Health check endpoint

## Styling

The application uses a custom design system with:
- Primary color palette (blue tones)
- Consistent spacing and typography
- Smooth animations and transitions
- Responsive grid layouts
- Modern card-based UI components

## Build for Production

```bash
npm run build
npm start
```


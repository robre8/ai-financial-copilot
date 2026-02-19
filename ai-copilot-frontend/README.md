# AI Financial Copilot Frontend

React + Vite + Tailwind CSS frontend for the AI Financial Copilot application.

## Features

- ✨ **Professional UI** with Tailwind CSS
- 🌙 **Dark Mode** support with localStorage persistence
- 💬 **Chat History** with expandable context
- 📊 **Model Indicator** showing which LLM model was used (8B, 70B, Mixtral)
- 🔍 **Context Visualization** - see the chunks retrieved from documents
- ⚡ **Real-time Responses** with loading indicators
- 🎨 **Responsive Design** - works on mobile, tablet, desktop
- ♿ **Accessible** - semantic HTML and ARIA labels

## Setup

```bash
# Install dependencies
npm install

# Dev server (port 5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

Create a `.env.local` file:

```env
VITE_API_BASE=http://localhost:8000
```

For production (Vercel):
```env
VITE_API_BASE=https://ai-financial-copilot.onrender.com
```

## Build

The `npm run build` command:
1. Runs TypeScript compiler
2. Builds optimized production bundle
3. Outputs to `dist/` directory

Ready to deploy on Vercel!

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

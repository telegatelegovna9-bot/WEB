# Crypto Screener Frontend

Professional cryptocurrency screening platform with AI-powered signal intelligence.

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Features

- 🚀 Real-time signal detection
- 🧠 AI-powered signal intelligence with explanations
- 📊 Market heatmap visualization
- 📈 Order book analysis
- 💰 Smart money flow detection
- 🔔 Customizable notifications

## Tech Stack

- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **Charts:** Recharts, Lightweight Charts
- **Real-time:** WebSocket

## Project Structure

```
src/
├── components/     # React components
├── hooks/          # Custom React hooks
├── pages/          # Next.js pages
├── store/          # Zustand stores
├── styles/         # Global styles
└── types/          # TypeScript types
```

## License

MIT

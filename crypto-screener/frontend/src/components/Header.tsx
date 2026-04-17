interface HeaderProps {
  connected: boolean;
}

export default function Header({ connected }: HeaderProps) {
  return (
    <header className="border-b border-surface2 bg-surface/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Crypto Screener</h1>
              <p className="text-xs text-gray-400">Intelligent Market Analysis</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2 px-3 py-1.5 bg-surface2 rounded-full">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-success animate-pulse' : 'bg-danger'}`}></div>
              <span className="text-xs text-gray-400">{connected ? 'Live' : 'Disconnected'}</span>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-6">
              <a href="#" className="text-sm text-gray-300 hover:text-white transition-colors">Dashboard</a>
              <a href="#" className="text-sm text-gray-300 hover:text-white transition-colors">Signals</a>
              <a href="#" className="text-sm text-gray-300 hover:text-white transition-colors">Settings</a>
            </nav>
          </div>
        </div>
      </div>
    </header>
  );
}

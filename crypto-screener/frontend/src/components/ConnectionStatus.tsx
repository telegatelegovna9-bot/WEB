'use client';

interface ConnectionStatusProps {
  connected: boolean;
}

export function ConnectionStatus({ connected }: ConnectionStatusProps) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
      <span className={connected ? 'text-green-500' : 'text-red-500'}>
        {connected ? 'Connected' : 'Disconnected'}
      </span>
    </div>
  );
}

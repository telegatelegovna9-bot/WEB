import type { Metadata } from 'next'
import '../styles/globals.css'

export const metadata: Metadata = {
  title: 'Crypto Screener - Intelligent Market Analysis',
  description: 'Advanced cryptocurrency screening platform with intelligent signals and market behavior analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

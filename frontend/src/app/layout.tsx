import '@/app/globals.css';
import { AuthProvider } from '@/lib/auth-context';

export const metadata = {
  title: 'JanSeva AI - Multilingual Legal Welfare Assistant',
  description: 'Offline-first Multilingual Legal Welfare Assistant for Indian Citizens',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}

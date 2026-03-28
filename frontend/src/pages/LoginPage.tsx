import { SignIn } from '@clerk/clerk-react';
import AuthLayout from '../components/auth/AuthLayout';

export default function LoginPage() {
  return (
    <AuthLayout
      title={'Track Insider Trades.\nMake Smarter Decisions.'}
      subtitle="Real-time insider trading analytics powered by AI"
      features={[
        'Real-time SEC filing alerts',
        'AI-powered market insights',
        'Multi-tier subscription plans',
        'Advanced analytics dashboard',
      ]}
    >
      <SignIn
        routing="path"
        path="/login"
        signUpUrl="/register"
        fallbackRedirectUrl="/dashboard"
        appearance={{
          elements: {
            rootBox: 'w-full',
            card: 'shadow-none bg-transparent w-full',
          },
        }}
      />
    </AuthLayout>
  );
}

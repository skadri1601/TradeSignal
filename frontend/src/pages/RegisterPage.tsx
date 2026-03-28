import { SignUp } from '@clerk/clerk-react';
import AuthLayout from '../components/auth/AuthLayout';

export default function RegisterPage() {
  return (
    <AuthLayout
      title={'Join TradeSignal.\nStart Trading Smarter.'}
      subtitle="Get access to real-time insider trading data and AI-powered insights"
      features={[
        'Free tier with essential features',
        'Real-time SEC filing notifications',
        'Advanced analytics & AI insights',
        'Upgrade anytime to unlock more',
      ]}
    >
      <SignUp
        routing="path"
        path="/register"
        signInUrl="/login"
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

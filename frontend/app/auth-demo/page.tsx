'use client';

import { useState } from 'react';
import { Card, Button, Modal } from '@/components/ui';
import { LoginForm, RegisterForm, PasswordResetForm } from '@/components/auth';

export default function AuthDemo() {
  const [activeModal, setActiveModal] = useState<'login' | 'register' | 'reset' | null>(null);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold mb-8">Authentication Components Demo</h1>

        <section>
          <h2 className="text-2xl font-semibold mb-4">Authentication Forms</h2>
          <Card>
            <p className="mb-4 text-gray-600">
              Click the buttons below to test the authentication forms. These forms include
              validation and will show error messages for invalid inputs.
            </p>
            <div className="flex flex-wrap gap-4">
              <Button onClick={() => setActiveModal('login')}>Login Form</Button>
              <Button variant="secondary" onClick={() => setActiveModal('register')}>
                Register Form
              </Button>
              <Button variant="secondary" onClick={() => setActiveModal('reset')}>
                Password Reset Form
              </Button>
            </div>
          </Card>
        </section>

        {/* Login Modal */}
        <Modal
          isOpen={activeModal === 'login'}
          onClose={() => setActiveModal(null)}
          title="Login"
        >
          <LoginForm onSuccess={() => setActiveModal(null)} />
        </Modal>

        {/* Register Modal */}
        <Modal
          isOpen={activeModal === 'register'}
          onClose={() => setActiveModal(null)}
          title="Create Account"
        >
          <RegisterForm onSuccess={() => setActiveModal(null)} />
        </Modal>

        {/* Password Reset Modal */}
        <Modal
          isOpen={activeModal === 'reset'}
          onClose={() => setActiveModal(null)}
          title="Reset Password"
        >
          <PasswordResetForm onSuccess={() => setActiveModal(null)} />
        </Modal>

        <section>
          <h2 className="text-2xl font-semibold mb-4">Features</h2>
          <Card>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Form validation with real-time error messages</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Loading states during API calls</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Accessible forms with ARIA labels and error descriptions</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Token storage in localStorage</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Automatic token refresh every 14 minutes</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span>Protected route HOC for role-based access control</span>
              </li>
            </ul>
          </Card>
        </section>
      </div>
    </div>
  );
}

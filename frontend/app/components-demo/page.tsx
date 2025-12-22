'use client';

import { useState } from 'react';
import { Card, Button, Modal, useToast } from '@/components/ui';

export default function ComponentsDemo() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { addToast } = useToast();

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold mb-8">UI Components Demo</h1>

        {/* Card Demo */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Card Component</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <h3 className="text-lg font-semibold mb-2">Basic Card</h3>
              <p className="text-gray-600">
                This is a card with 2xl rounded corners and soft shadows.
              </p>
            </Card>
            <Card onClick={() => addToast('Card clicked!', 'info')}>
              <h3 className="text-lg font-semibold mb-2">Interactive Card</h3>
              <p className="text-gray-600">
                Click this card to see the toast notification.
              </p>
            </Card>
          </div>
        </section>

        {/* Button Demo */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Button Component</h2>
          <Card>
            <div className="space-y-4">
              <div className="flex flex-wrap gap-4">
                <Button onClick={() => addToast('Primary button clicked', 'success')}>
                  Primary Button
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => addToast('Secondary button clicked', 'info')}
                >
                  Secondary Button
                </Button>
                <Button
                  variant="danger"
                  onClick={() => addToast('Danger button clicked', 'warning')}
                >
                  Danger Button
                </Button>
              </div>
              <div className="flex flex-wrap gap-4">
                <Button disabled>Disabled Button</Button>
                <Button loading>Loading Button</Button>
              </div>
            </div>
          </Card>
        </section>

        {/* Modal Demo */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Modal Component</h2>
          <Card>
            <Button onClick={() => setIsModalOpen(true)}>Open Modal</Button>
            <Modal
              isOpen={isModalOpen}
              onClose={() => setIsModalOpen(false)}
              title="Example Modal"
            >
              <p className="mb-4">
                This is a modal with focus trap. Try pressing Tab to navigate through
                focusable elements, or press Escape to close.
              </p>
              <div className="flex gap-2">
                <Button onClick={() => setIsModalOpen(false)}>Close</Button>
                <Button
                  variant="secondary"
                  onClick={() => {
                    addToast('Action confirmed!', 'success');
                    setIsModalOpen(false);
                  }}
                >
                  Confirm
                </Button>
              </div>
            </Modal>
          </Card>
        </section>

        {/* Toast Demo */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Toast Notification System</h2>
          <Card>
            <div className="flex flex-wrap gap-4">
              <Button onClick={() => addToast('Success message!', 'success')}>
                Success Toast
              </Button>
              <Button onClick={() => addToast('Error occurred!', 'error')}>
                Error Toast
              </Button>
              <Button onClick={() => addToast('Warning message!', 'warning')}>
                Warning Toast
              </Button>
              <Button onClick={() => addToast('Information message!', 'info')}>
                Info Toast
              </Button>
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
}

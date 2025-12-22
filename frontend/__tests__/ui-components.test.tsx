/**
 * Tests for shared UI components
 * Validates Requirements 10.1, 10.5
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Modal } from '../components/ui/Modal';
import { ToastProvider, useToast } from '../components/ui/Toast';

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByText('Loading')).toBeInTheDocument();
  });

  it('supports different variants', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-blue-600');
    
    rerender(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-gray-600');
  });

  it('is accessible with keyboard navigation', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Accessible Button</Button>);
    
    const button = screen.getByRole('button');
    button.focus();
    expect(button).toHaveFocus();
    
    await userEvent.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalled();
  });
});

describe('Card Component', () => {
  it('renders children correctly', () => {
    render(
      <Card>
        <h2>Card Title</h2>
        <p>Card content</p>
      </Card>
    );
    
    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('applies correct styling classes', () => {
    const { container } = render(<Card>Content</Card>);
    const card = container.firstChild;
    
    expect(card).toHaveClass('rounded-2xl');
    expect(card).toHaveClass('shadow-lg');
    expect(card).toHaveClass('bg-white');
  });

  it('supports custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    expect(container.firstChild).toHaveClass('custom-class');
  });
});

describe('Modal Component', () => {
  it('renders when open', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        <h2>Modal Content</h2>
      </Modal>
    );
    
    expect(screen.getByText('Modal Content')).toBeInTheDocument();
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <Modal isOpen={false} onClose={() => {}}>
        <h2>Modal Content</h2>
      </Modal>
    );
    
    expect(screen.queryByText('Modal Content')).not.toBeInTheDocument();
  });

  it('calls onClose when overlay is clicked', async () => {
    const handleClose = jest.fn();
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <h2>Modal Content</h2>
      </Modal>
    );
    
    const overlay = screen.getByTestId('modal-overlay');
    await userEvent.click(overlay);
    expect(handleClose).toHaveBeenCalled();
  });

  it('calls onClose when escape key is pressed', async () => {
    const handleClose = jest.fn();
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <h2>Modal Content</h2>
      </Modal>
    );
    
    await userEvent.keyboard('{Escape}');
    expect(handleClose).toHaveBeenCalled();
  });

  it('traps focus within modal', async () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        <button>First Button</button>
        <button>Second Button</button>
      </Modal>
    );
    
    const firstButton = screen.getByText('First Button');
    const secondButton = screen.getByText('Second Button');
    
    // Focus should be trapped within modal
    firstButton.focus();
    expect(firstButton).toHaveFocus();
    
    await userEvent.tab();
    expect(secondButton).toHaveFocus();
    
    await userEvent.tab();
    expect(firstButton).toHaveFocus(); // Should cycle back
  });
});

describe('Toast Component', () => {
  it('renders with message', () => {
    render(<Toast message="Success message" type="success" />);
    expect(screen.getByText('Success message')).toBeInTheDocument();
  });

  it('applies correct styling for different types', () => {
    const { rerender } = render(<Toast message="Success" type="success" />);
    expect(screen.getByRole('alert')).toHaveClass('bg-green-500');
    
    rerender(<Toast message="Error" type="error" />);
    expect(screen.getByRole('alert')).toHaveClass('bg-red-500');
    
    rerender(<Toast message="Warning" type="warning" />);
    expect(screen.getByRole('alert')).toHaveClass('bg-yellow-500');
  });

  it('calls onDismiss when close button is clicked', async () => {
    const handleDismiss = jest.fn();
    render(<Toast message="Test" type="info" onDismiss={handleDismiss} />);
    
    const closeButton = screen.getByRole('button', { name: /close/i });
    await userEvent.click(closeButton);
    expect(handleDismiss).toHaveBeenCalled();
  });

  it('auto-dismisses after timeout', async () => {
    const handleDismiss = jest.fn();
    render(<Toast message="Test" type="info" onDismiss={handleDismiss} autoHide={true} />);
    
    await waitFor(() => {
      expect(handleDismiss).toHaveBeenCalled();
    }, { timeout: 6000 });
  });

  it('is accessible with proper ARIA attributes', () => {
    render(<Toast message="Accessible toast" type="info" />);
    
    const toast = screen.getByRole('alert');
    expect(toast).toHaveAttribute('aria-live', 'polite');
    expect(toast).toHaveAttribute('aria-atomic', 'true');
  });
});
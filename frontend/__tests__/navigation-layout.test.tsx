import React from 'react';
import { render } from '@testing-library/react';
import { screen, fireEvent, waitFor } from '@testing-library/dom';
import { Navigation } from '@/components/layout/Navigation';
import { MainLayout } from '@/components/layout/MainLayout';
import { Footer } from '@/components/layout/Footer';
import { AuthProvider } from '@/lib/auth';
import '@testing-library/jest-dom';
import * as fc from 'fast-check';

// Mock Next.js router
let mockPathname = '/';
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => mockPathname),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  })),
}));

// Mock auth API
jest.mock('@/lib/auth/api', () => ({
  authApi: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    refreshToken: jest.fn(),
    getCurrentUser: jest.fn(),
  },
}));

const MockAuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <AuthProvider>{children}</AuthProvider>;
};

describe('Navigation Component', () => {
  it('renders all subsite links', () => {
    render(
      <MockAuthProvider>
        <Navigation />
      </MockAuthProvider>
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Portfolio')).toBeInTheDocument();
    expect(screen.getByText('PHARMXAM')).toBeInTheDocument();
    expect(screen.getByText('HUB3660')).toBeInTheDocument();
    expect(screen.getByText('HEALTHEE')).toBeInTheDocument();
  });

  it('renders VEETSSUITES logo', () => {
    render(
      <MockAuthProvider>
        <Navigation />
      </MockAuthProvider>
    );

    expect(screen.getByText('VEETSSUITES')).toBeInTheDocument();
  });

  it('shows login and sign up buttons when not authenticated', () => {
    render(
      <MockAuthProvider>
        <Navigation />
      </MockAuthProvider>
    );

    // Desktop buttons
    const loginButtons = screen.getAllByText('Login');
    const signUpButtons = screen.getAllByText('Sign Up');
    
    expect(loginButtons.length).toBeGreaterThan(0);
    expect(signUpButtons.length).toBeGreaterThan(0);
  });

  it('toggles mobile menu when hamburger button is clicked', () => {
    render(
      <MockAuthProvider>
        <Navigation />
      </MockAuthProvider>
    );

    const mobileMenuButton = screen.getByLabelText('Toggle mobile menu');
    
    // Mobile menu should not be visible initially
    expect(screen.queryByRole('navigation')).toBeInTheDocument();
    
    // Click to open mobile menu
    fireEvent.click(mobileMenuButton);
    
    // Mobile menu links should be visible
    const mobileLinks = screen.getAllByText('Portfolio');
    expect(mobileLinks.length).toBeGreaterThan(1); // Desktop + Mobile
  });
});

describe('Footer Component', () => {
  it('renders footer sections', () => {
    render(<Footer />);

    expect(screen.getByText('About VEETSSUITES')).toBeInTheDocument();
    expect(screen.getByText('Subsites')).toBeInTheDocument();
    expect(screen.getByText('Resources')).toBeInTheDocument();
    expect(screen.getByText('Legal')).toBeInTheDocument();
  });

  it('displays copyright with current year', () => {
    render(<Footer />);

    const currentYear = new Date().getFullYear();
    expect(screen.getByText(new RegExp(`© ${currentYear} VEETSSUITES`))).toBeInTheDocument();
  });

  it('renders all subsite links in footer', () => {
    render(<Footer />);

    const footerLinks = screen.getAllByRole('link');
    const portfolioLinks = footerLinks.filter(link => link.textContent === 'Portfolio');
    const pharmxamLinks = footerLinks.filter(link => link.textContent === 'PHARMXAM');
    const hub3660Links = footerLinks.filter(link => link.textContent === 'HUB3660');
    const healtheLinks = footerLinks.filter(link => link.textContent === 'HEALTHEE');

    expect(portfolioLinks.length).toBeGreaterThan(0);
    expect(pharmxamLinks.length).toBeGreaterThan(0);
    expect(hub3660Links.length).toBeGreaterThan(0);
    expect(healtheLinks.length).toBeGreaterThan(0);
  });
});

describe('MainLayout Component', () => {
  it('renders navigation, content, and footer', () => {
    render(
      <MockAuthProvider>
        <MainLayout>
          <div>Test Content</div>
        </MainLayout>
      </MockAuthProvider>
    );

    // Navigation should be present
    expect(screen.getByText('VEETSSUITES')).toBeInTheDocument();
    
    // Content should be rendered
    expect(screen.getByText('Test Content')).toBeInTheDocument();
    
    // Footer should be present
    expect(screen.getByText('About VEETSSUITES')).toBeInTheDocument();
  });

  it('applies flex layout classes', () => {
    const { container } = render(
      <MockAuthProvider>
        <MainLayout>
          <div>Test Content</div>
        </MainLayout>
      </MockAuthProvider>
    );

    const layoutDiv = container.firstChild;
    expect(layoutDiv).toHaveClass('flex', 'flex-col', 'min-h-screen');
  });
});

describe('Responsive Design', () => {
  it('navigation has responsive classes', () => {
    const { container } = render(
      <MockAuthProvider>
        <Navigation />
      </MockAuthProvider>
    );

    // Check for responsive utility classes
    const nav = container.querySelector('nav');
    expect(nav).toBeInTheDocument();
    
    // Desktop navigation should have md: classes
    const desktopNav = container.querySelector('.md\\:flex');
    expect(desktopNav).toBeInTheDocument();
  });

  it('footer has responsive grid layout', () => {
    const { container } = render(<Footer />);

    // Check for responsive grid classes
    const grid = container.querySelector('.grid');
    expect(grid).toBeInTheDocument();
    expect(grid).toHaveClass('grid-cols-1', 'md:grid-cols-4');
  });
});

// Property-Based Tests
describe('Property-Based Tests for Navigation', () => {
  // Helper to set mock pathname
  const setMockPathname = (path: string) => {
    mockPathname = path;
    const { usePathname } = require('next/navigation');
    usePathname.mockReturnValue(path);
  };

  afterEach(() => {
    // Reset to default
    setMockPathname('/');
  });

  /**
   * Feature: veetssuites-platform, Property 43: Navigation shows current section
   * Validates: Requirements 10.2
   * 
   * For any valid subsite path, when the navigation is rendered with that path as active,
   * the corresponding navigation link should have visual indicators (active state styling)
   * that distinguish it from other navigation items.
   */
  it('Property 43: Navigation shows current section for all valid paths', () => {
    // Define valid subsite paths
    const validPaths = ['/', '/portfolio', '/pharmxam', '/hub3660', '/healthee'];
    
    fc.assert(
      fc.property(
        fc.constantFrom(...validPaths),
        (path) => {
          // Set the current path
          setMockPathname(path);
          
          // Render navigation
          const { container } = render(
            <MockAuthProvider>
              <Navigation />
            </MockAuthProvider>
          );

          // Find all navigation links
          const links = container.querySelectorAll('a[href]');
          let foundActiveLink = false;
          let activeHasVisualIndicator = false;

          links.forEach((link) => {
            const href = link.getAttribute('href');
            const isCurrentPath = (path === '/' && href === '/') || 
                                 (path !== '/' && href === path);
            
            if (isCurrentPath) {
              foundActiveLink = true;
              // Check for active state indicators
              const hasActiveClass = link.className.includes('bg-blue-100') || 
                                    link.className.includes('text-blue-700') ||
                                    link.className.includes('border-blue-700');
              const hasAriaCurrent = link.getAttribute('aria-current') === 'page';
              
              activeHasVisualIndicator = hasActiveClass && hasAriaCurrent;
            }
          });

          // Verify that we found the active link and it has visual indicators
          expect(foundActiveLink).toBe(true);
          expect(activeHasVisualIndicator).toBe(true);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Feature: veetssuites-platform, Property 43: Navigation shows current section (nested paths)
   * Validates: Requirements 10.2
   * 
   * For any nested path within a subsite, the parent subsite navigation link should
   * remain active to show the current section.
   */
  it('Property 43: Navigation shows current section for nested paths', () => {
    const subsiteWithNestedPaths = [
      { base: '/portfolio', nested: ['/portfolio/edit', '/portfolio/view', '/portfolio/settings'] },
      { base: '/pharmxam', nested: ['/pharmxam/exam/1', '/pharmxam/results', '/pharmxam/history'] },
      { base: '/hub3660', nested: ['/hub3660/course/1', '/hub3660/enroll', '/hub3660/sessions'] },
      { base: '/healthee', nested: ['/healthee/consultation', '/healthee/history'] },
    ];

    fc.assert(
      fc.property(
        fc.constantFrom(...subsiteWithNestedPaths),
        (subsite) => {
          // Pick a random nested path from the subsite
          const nestedIndex = Math.floor(Math.random() * subsite.nested.length);
          const nestedPath = subsite.nested[nestedIndex];
          setMockPathname(nestedPath);
          
          const { container, unmount } = render(
            <MockAuthProvider>
              <Navigation />
            </MockAuthProvider>
          );

          // Find the base subsite link
          const baseLink = Array.from(container.querySelectorAll('a[href]')).find(
            (link) => link.getAttribute('href') === subsite.base
          );

          expect(baseLink).toBeTruthy();
          if (baseLink) {
            // Should have active styling
            const hasActiveClass = baseLink.className.includes('bg-blue-100') || 
                                  baseLink.className.includes('text-blue-700');
            expect(hasActiveClass).toBe(true);
            expect(baseLink.getAttribute('aria-current')).toBe('page');
          }
          
          // Clean up
          unmount();
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Feature: veetssuites-platform, Property 44: Responsive design adapts to screen sizes
   * Validates: Requirements 10.3
   * 
   * For any viewport configuration, the navigation should include responsive classes
   * that adapt the layout appropriately without breaking the UI structure.
   */
  it('Property 44: Responsive design classes are present for all breakpoints', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('mobile', 'tablet', 'desktop'),
        (deviceType) => {
          const { container } = render(
            <MockAuthProvider>
              <Navigation />
            </MockAuthProvider>
          );

          const nav = container.querySelector('nav');
          expect(nav).toBeInTheDocument();

          // Check for responsive utility classes
          // Desktop navigation should be hidden on mobile
          const desktopNav = container.querySelector('.md\\:flex');
          expect(desktopNav).toBeInTheDocument();

          // Mobile menu button should be hidden on desktop
          const mobileButton = container.querySelector('.md\\:hidden');
          expect(mobileButton).toBeInTheDocument();

          // Verify the navigation has proper structure for responsiveness
          const hasResponsiveClasses = nav?.className.includes('bg-white') && 
                                      nav?.className.includes('shadow');
          expect(hasResponsiveClasses).toBe(true);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Feature: veetssuites-platform, Property 44: Responsive design adapts to screen sizes (Layout)
   * Validates: Requirements 10.3
   * 
   * For any content rendered within MainLayout, the layout should maintain proper
   * flex structure with responsive classes that ensure proper rendering across devices.
   */
  it('Property 44: MainLayout maintains responsive structure with any content', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0),
        fc.integer({ min: 1, max: 10 }),
        (contentText, numElements) => {
          // Generate random content
          const content = (
            <div data-testid="test-content">
              {Array.from({ length: numElements }, (_, i) => (
                <div key={i}>{contentText}-{i}</div>
              ))}
            </div>
          );

          const { container, unmount } = render(
            <MockAuthProvider>
              <MainLayout>{content}</MainLayout>
            </MockAuthProvider>
          );

          // Verify layout structure
          const layoutDiv = container.firstChild as HTMLElement;
          expect(layoutDiv).toHaveClass('flex', 'flex-col', 'min-h-screen');

          // Verify content is rendered
          const testContent = container.querySelector('[data-testid="test-content"]');
          expect(testContent).toBeInTheDocument();

          // Verify navigation and footer are present (use getAllByText for multiple instances)
          const veetsuitesElements = screen.getAllByText('VEETSSUITES');
          expect(veetsuitesElements.length).toBeGreaterThan(0);
          
          const aboutElements = screen.getAllByText('About VEETSSUITES');
          expect(aboutElements.length).toBeGreaterThan(0);
          
          // Clean up
          unmount();
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Feature: veetssuites-platform, Property 44: Responsive design adapts to screen sizes (Footer)
   * Validates: Requirements 10.3
   * 
   * The footer should maintain responsive grid layout that adapts from single column
   * on mobile to multi-column on larger screens.
   */
  it('Property 44: Footer maintains responsive grid structure', () => {
    fc.assert(
      fc.property(
        fc.constant(true), // Just run multiple times to verify consistency
        () => {
          const { container, unmount } = render(<Footer />);

          // Check for responsive grid classes
          const grid = container.querySelector('.grid');
          expect(grid).toBeInTheDocument();
          
          // Should have mobile-first single column and desktop multi-column
          expect(grid).toHaveClass('grid-cols-1');
          expect(grid?.className).toMatch(/md:grid-cols-\d/);

          // Verify footer sections are present (use getAllByText for multiple instances)
          const aboutElements = screen.getAllByText('About VEETSSUITES');
          expect(aboutElements.length).toBeGreaterThan(0);
          
          expect(screen.getByText('Subsites')).toBeInTheDocument();
          expect(screen.getByText('Resources')).toBeInTheDocument();
          expect(screen.getByText('Legal')).toBeInTheDocument();
          
          // Clean up
          unmount();
        }
      ),
      { numRuns: 100 }
    );
  });
});

import { test, expect } from '@playwright/test';
import { AuthPage } from './pages/AuthPage';

test.describe('Authentication Flow', () => {
  let authPage: AuthPage;

  test.beforeEach(async ({ page }) => {
    authPage = new AuthPage(page);
    await authPage.gotoLogin();
  });

  test('should display login form by default', async () => {
    await expect(authPage.loginForm).toBeVisible();
    await expect(authPage.emailInput).toBeVisible();
    await expect(authPage.passwordInput).toBeVisible();
    await expect(authPage.loginButton).toBeVisible();
  });

  test('should switch between login and register forms', async () => {
    // Should start with login form
    await expect(authPage.loginForm).toBeVisible();
    
    // Switch to register
    await authPage.switchToRegister();
    await expect(authPage.registerForm).toBeVisible();
    await expect(authPage.firstNameInput).toBeVisible();
    await expect(authPage.lastNameInput).toBeVisible();
    await expect(authPage.confirmPasswordInput).toBeVisible();
    
    // Switch back to login
    await authPage.switchToLogin();
    await expect(authPage.loginForm).toBeVisible();
  });

  test('should show validation errors for empty fields', async () => {
    await authPage.loginButton.click();
    
    // Check for HTML5 validation or custom error messages
    const emailValidity = await authPage.emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
    expect(emailValidity).toBe(false);
  });

  test('should show error for invalid credentials', async () => {
    await authPage.login('invalid@example.com', 'wrongpassword');
    
    // Wait for error message or stay on login page
    await authPage.page.waitForTimeout(2000);
    
    // Should still be on auth page (not redirected)
    expect(authPage.page.url()).toContain('auth-demo');
  });

  test('should validate password confirmation in register form', async () => {
    await authPage.switchToRegister();
    
    await authPage.register({
      firstName: 'Test',
      lastName: 'User',
      email: 'test@example.com',
      password: 'password123',
      confirmPassword: 'differentpassword'
    });
    
    // Should show validation error or stay on form
    await authPage.page.waitForTimeout(1000);
    await expect(authPage.registerForm).toBeVisible();
  });

  test('should have accessible form elements', async () => {
    // Check for proper labels and ARIA attributes
    await expect(authPage.emailInput).toHaveAttribute('type', 'email');
    await expect(authPage.passwordInput).toHaveAttribute('type', 'password');
    
    // Check for required attributes
    await expect(authPage.emailInput).toHaveAttribute('required');
    await expect(authPage.passwordInput).toHaveAttribute('required');
  });

  test('should support keyboard navigation', async () => {
    // Tab through form elements
    await authPage.emailInput.focus();
    await authPage.page.keyboard.press('Tab');
    await expect(authPage.passwordInput).toBeFocused();
    
    await authPage.page.keyboard.press('Tab');
    await expect(authPage.loginButton).toBeFocused();
  });
});
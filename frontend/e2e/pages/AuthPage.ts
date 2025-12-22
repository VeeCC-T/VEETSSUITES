import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class AuthPage extends BasePage {
  readonly loginForm: Locator;
  readonly registerForm: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly loginButton: Locator;
  readonly registerButton: Locator;
  readonly switchToRegisterLink: Locator;
  readonly switchToLoginLink: Locator;
  readonly forgotPasswordLink: Locator;

  constructor(page: Page) {
    super(page);
    this.loginForm = page.locator('[data-testid="login-form"]');
    this.registerForm = page.locator('[data-testid="register-form"]');
    this.emailInput = page.locator('input[name="email"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.confirmPasswordInput = page.locator('input[name="confirmPassword"]');
    this.firstNameInput = page.locator('input[name="firstName"]');
    this.lastNameInput = page.locator('input[name="lastName"]');
    this.loginButton = page.locator('button[type="submit"]', { hasText: 'Login' });
    this.registerButton = page.locator('button[type="submit"]', { hasText: 'Register' });
    this.switchToRegisterLink = page.locator('text=Create an account');
    this.switchToLoginLink = page.locator('text=Already have an account');
    this.forgotPasswordLink = page.locator('text=Forgot password');
  }

  async gotoLogin() {
    await this.goto('/auth-demo');
    await this.waitForLoad();
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async register(userData: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    confirmPassword: string;
  }) {
    // Switch to register form if not already visible
    if (await this.switchToRegisterLink.isVisible()) {
      await this.switchToRegisterLink.click();
    }

    await this.firstNameInput.fill(userData.firstName);
    await this.lastNameInput.fill(userData.lastName);
    await this.emailInput.fill(userData.email);
    await this.passwordInput.fill(userData.password);
    await this.confirmPasswordInput.fill(userData.confirmPassword);
    await this.registerButton.click();
  }

  async switchToRegister() {
    await this.switchToRegisterLink.click();
  }

  async switchToLogin() {
    await this.switchToLoginLink.click();
  }

  async getErrorMessage() {
    const errorElement = this.page.locator('[data-testid="error-message"]');
    if (await errorElement.isVisible()) {
      return await errorElement.textContent();
    }
    return null;
  }
}
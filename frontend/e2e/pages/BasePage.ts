import { Page, Locator } from '@playwright/test';

export class BasePage {
  readonly page: Page;
  readonly navigation: Locator;
  readonly footer: Locator;

  constructor(page: Page) {
    this.page = page;
    this.navigation = page.locator('nav');
    this.footer = page.locator('footer');
  }

  async goto(path: string = '/') {
    await this.page.goto(path);
  }

  async waitForLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  async getTitle() {
    return await this.page.title();
  }

  async clickNavLink(text: string) {
    await this.navigation.getByText(text).click();
  }

  async isLoggedIn() {
    // Check if user menu or logout button is visible
    const userMenu = this.page.locator('[data-testid="user-menu"]');
    const logoutButton = this.page.locator('[data-testid="logout-button"]');
    
    try {
      await userMenu.waitFor({ timeout: 1000 });
      return true;
    } catch {
      try {
        await logoutButton.waitFor({ timeout: 1000 });
        return true;
      } catch {
        return false;
      }
    }
  }

  async logout() {
    if (await this.isLoggedIn()) {
      const userMenu = this.page.locator('[data-testid="user-menu"]');
      const logoutButton = this.page.locator('[data-testid="logout-button"]');
      
      try {
        await userMenu.click();
        await logoutButton.click();
      } catch {
        await logoutButton.click();
      }
    }
  }
}
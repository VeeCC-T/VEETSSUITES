import { test, expect } from '@playwright/test';
import { HomePage } from './pages/HomePage';

test.describe('Homepage', () => {
  let homePage: HomePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.goto();
  });

  test('should display main navigation', async () => {
    await expect(homePage.page.locator('nav')).toBeVisible();
  });

  test('should have proper page title', async () => {
    await expect(homePage.page).toHaveTitle(/VEETSSUITES/);
  });

  test('should display main content sections', async () => {
    await expect(homePage.page.locator('main')).toBeVisible();
  });
});
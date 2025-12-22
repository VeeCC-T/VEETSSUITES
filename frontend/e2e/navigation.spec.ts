import { test, expect } from '@playwright/test';
import { HomePage } from './pages/HomePage';

test.describe('Navigation and Layout', () => {
  let homePage: HomePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.gotoHome();
  });

  test('should display main navigation', async () => {
    await expect(homePage.navigation).toBeVisible();
    
    // Check for main navigation links
    await expect(homePage.page.locator('nav a[href="/portfolio"]')).toBeVisible();
    await expect(homePage.page.locator('nav a[href="/pharmxam"]')).toBeVisible();
    await expect(homePage.page.locator('nav a[href="/hub3660"]')).toBeVisible();
    await expect(homePage.page.locator('nav a[href="/healthee"]')).toBeVisible();
  });

  test('should display footer', async () => {
    await expect(homePage.footer).toBeVisible();
  });

  test('should navigate to different subsites', async () => {
    // Test Portfolio navigation
    await homePage.clickNavLink('Portfolio');
    await homePage.waitForLoad();
    expect(homePage.page.url()).toContain('/portfolio');
    
    // Test PHARMXAM navigation
    await homePage.clickNavLink('PHARMXAM');
    await homePage.waitForLoad();
    expect(homePage.page.url()).toContain('/pharmxam');
    
    // Test HUB3660 navigation
    await homePage.clickNavLink('HUB3660');
    await homePage.waitForLoad();
    expect(homePage.page.url()).toContain('/hub3660');
    
    // Test HEALTHEE navigation
    await homePage.clickNavLink('HEALTHEE');
    await homePage.waitForLoad();
    expect(homePage.page.url()).toContain('/healthee');
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await homePage.gotoHome();
    
    // Navigation should still be visible (might be collapsed)
    await expect(homePage.navigation).toBeVisible();
    
    // Check if mobile menu toggle exists
    const mobileMenuToggle = page.locator('[data-testid="mobile-menu-toggle"]');
    if (await mobileMenuToggle.isVisible()) {
      await mobileMenuToggle.click();
      // Navigation links should be visible after clicking toggle
      await expect(page.locator('nav a[href="/portfolio"]')).toBeVisible();
    }
  });

  test('should highlight active navigation item', async () => {
    // Go to portfolio page
    await homePage.clickNavLink('Portfolio');
    await homePage.waitForLoad();
    
    // Check if portfolio nav item has active class or aria-current
    const portfolioLink = homePage.page.locator('nav a[href="/portfolio"]');
    const hasActiveClass = await portfolioLink.evaluate((el) => 
      el.classList.contains('active') || 
      el.getAttribute('aria-current') === 'page' ||
      el.classList.contains('text-blue-600') // Tailwind active color
    );
    
    expect(hasActiveClass).toBe(true);
  });

  test('should have proper page titles', async () => {
    // Home page
    await homePage.gotoHome();
    const homeTitle = await homePage.getTitle();
    expect(homeTitle).toContain('VeetsSuites');
    
    // Portfolio page
    await homePage.clickNavLink('Portfolio');
    await homePage.waitForLoad();
    const portfolioTitle = await homePage.getTitle();
    expect(portfolioTitle).toContain('Portfolio');
    
    // PHARMXAM page
    await homePage.clickNavLink('PHARMXAM');
    await homePage.waitForLoad();
    const pharmxamTitle = await homePage.getTitle();
    expect(pharmxamTitle).toContain('PHARMXAM');
  });

  test('should have accessible navigation', async () => {
    // Check for proper ARIA labels
    const nav = homePage.navigation;
    const navRole = await nav.getAttribute('role');
    expect(navRole).toBe('navigation');
    
    // Check for skip links
    const skipLink = homePage.page.locator('a[href="#main-content"]');
    if (await skipLink.count() > 0) {
      await expect(skipLink).toHaveText(/skip to main content/i);
    }
  });
});
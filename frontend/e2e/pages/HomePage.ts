import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class HomePage extends BasePage {
  readonly heroSection: Locator;
  readonly portfolioCard: Locator;
  readonly pharmxamCard: Locator;
  readonly hub3660Card: Locator;
  readonly healtheeCard: Locator;
  readonly getStartedButton: Locator;

  constructor(page: Page) {
    super(page);
    this.heroSection = page.locator('[data-testid="hero-section"]');
    this.portfolioCard = page.locator('[data-testid="portfolio-card"]');
    this.pharmxamCard = page.locator('[data-testid="pharmxam-card"]');
    this.hub3660Card = page.locator('[data-testid="hub3660-card"]');
    this.healtheeCard = page.locator('[data-testid="healthee-card"]');
    this.getStartedButton = page.locator('[data-testid="get-started-button"]');
  }

  async gotoHome() {
    await this.goto('/');
    await this.waitForLoad();
  }

  async clickPortfolioCard() {
    await this.portfolioCard.click();
  }

  async clickPharmxamCard() {
    await this.pharmxamCard.click();
  }

  async clickHub3660Card() {
    await this.hub3660Card.click();
  }

  async clickHealtheeCard() {
    await this.healtheeCard.click();
  }

  async clickGetStarted() {
    await this.getStartedButton.click();
  }

  async isHeroVisible() {
    return await this.heroSection.isVisible();
  }

  async areAllCardsVisible() {
    const cards = [
      this.portfolioCard,
      this.pharmxamCard,
      this.hub3660Card,
      this.healtheeCard
    ];

    for (const card of cards) {
      if (!(await card.isVisible())) {
        return false;
      }
    }
    return true;
  }
}
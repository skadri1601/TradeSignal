import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should show login page', async ({ page }) => {
    await page.goto('/login');

    // Check for login form elements
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
    await expect(page.getByPlaceholderText(/email/i)).toBeVisible();
    await expect(page.getByPlaceholderText(/password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should show register page', async ({ page }) => {
    await page.goto('/register');

    // Check for registration form elements
    await expect(page.getByRole('heading', { name: /create.*account/i })).toBeVisible();
    await expect(page.getByPlaceholderText(/email/i)).toBeVisible();
    await expect(page.getByPlaceholderText(/username/i)).toBeVisible();
  });

  test('should navigate from login to register', async ({ page }) => {
    await page.goto('/login');

    // Click the register link
    await page.getByRole('link', { name: /create.*account|sign up|register/i }).click();

    // Should be on register page
    await expect(page).toHaveURL(/\/register/);
  });

  test('should show validation errors on empty login', async ({ page }) => {
    await page.goto('/login');

    // Try to submit empty form
    await page.getByRole('button', { name: /sign in/i }).click();

    // Form should not submit (HTML5 validation)
    await expect(page).toHaveURL(/\/login/);
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    // Try to access dashboard without being logged in
    await page.goto('/');

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/);
  });

  test('should show forgot password page', async ({ page }) => {
    await page.goto('/forgot-password');

    await expect(page.getByRole('heading', { name: /forgot.*password|reset.*password/i })).toBeVisible();
    await expect(page.getByPlaceholderText(/email/i)).toBeVisible();
  });
});

test.describe('Public Pages', () => {
  test('should show pricing page', async ({ page }) => {
    await page.goto('/pricing');

    await expect(page.getByRole('heading', { name: /pricing/i })).toBeVisible();
    // Check for pricing tiers
    await expect(page.getByText(/free/i)).toBeVisible();
    await expect(page.getByText(/pro/i)).toBeVisible();
  });

  test('should show FAQ page', async ({ page }) => {
    await page.goto('/faq');

    await expect(page.getByRole('heading', { name: /faq|frequently asked/i })).toBeVisible();
  });

  test('should show about page', async ({ page }) => {
    await page.goto('/about');

    await expect(page.getByRole('heading', { name: /about/i })).toBeVisible();
  });
});

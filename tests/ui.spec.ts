import { test, expect } from '@playwright/test';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';

let server: ChildProcess;

// start the API server before the suite and shut it down afterwards
test.beforeAll(async () => {
  server = spawn('python', ['api.py'], { stdio: 'ignore' });
  // give it a moment to come up
  await new Promise((r) => setTimeout(r, 1000));
});

test.afterAll(() => {
  if (server && !server.killed) {
    server.kill();
  }
});

const BASE = 'http://localhost:8094';

test('page loads and basic elements are present', async ({ page }) => {
  await page.goto(BASE);
  await expect(page.locator('h1')).toHaveText('DOCX → HTML');
  await expect(page.locator('#drop-zone')).toBeVisible();
  await expect(page.locator('#convert-btn')).toBeDisabled();
});

test('theme toggle toggles dark class', async ({ page }) => {
  await page.goto(BASE);
  const body = page.locator('body');
  const theme = page.locator('#theme-toggle');
  await theme.click();
  await expect(body).toHaveClass(/dark/);
  await theme.click();
  await expect(body).not.toHaveClass(/dark/);
});

test('uploading sample docx and converting', async ({ page }) => {
  await page.goto(BASE);
  const filePath = path.resolve(__dirname, '../test_sample.docx');
  await page.setInputFiles('#file-input', filePath);
  await expect(page.locator('#message')).toContainText('Selected:');
  await page.click('#convert-btn');
  await expect(page.locator('#message')).toHaveText('Conversion complete!');
  await expect(page.locator('#download-link')).toBeVisible();
});

import { test, expect } from '@playwright/test';

test('renames a column and persists change', async ({ page, request }) => {
  const base = 'http://localhost:8000';

  // Read the current board via API
  const boardRes = await request.get(`${base}/api/board/user`);
  if (boardRes.status() !== 200) throw new Error('GET /api/board/user failed');
  const board = await boardRes.json();

  // Modify and PUT the updated board
  board.columns[0].title = 'Renamed Column';
  const putRes = await request.put(`${base}/api/board/user`, { data: board });
  if (putRes.status() !== 200) throw new Error('PUT /api/board/user failed');

  // Load the app and sign in
  await page.goto(base);
  await page.getByPlaceholder(/user/i).fill('user');
  await page.getByPlaceholder(/password/i).fill('password');
  await page.getByRole('button', { name: /sign in/i }).click();

  // Assert the UI reads the persisted column title
  const firstColumnInput = page.locator('input[aria-label="Column title"]').first();
  await expect(firstColumnInput).toHaveValue('Renamed Column', { timeout: 10000 });
});

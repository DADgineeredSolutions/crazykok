import { expect, test } from '@playwright/test'

test('@smoke loads every core workspace through primary navigation', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('navigation', { name: 'Primary navigation' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'New venue' })).toBeVisible()

  await page.getByRole('button', { name: 'Opportunities' }).click()
  await expect(page.getByRole('button', { name: 'New opportunity' })).toBeVisible()

  await page.getByRole('button', { name: 'Map & calendar' }).click()
  await expect(page.getByRole('heading', { name: 'Map & calendar' })).toBeVisible()
  await expect(page.getByLabel('Planning filters')).toBeVisible()

  await page.getByRole('button', { name: 'Import venues' }).click()
  await expect(page.getByRole('heading', { name: 'Venue research import' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Download complete research kit' })).toBeVisible()
})

test('creates, edits, archives, restores, and deletes an opportunity', async ({ page }) => {
  const name = `E2E Opportunity ${Date.now()}`
  const editedName = `${name} updated`

  await page.goto('/')
  await page.getByRole('button', { name: 'Opportunities' }).click()
  await page.getByRole('button', { name: 'New opportunity' }).click()

  await page.getByLabel('Opportunity name').fill(name)
  await page.getByLabel('Opportunity date').fill('2026-09-12')
  await page.getByLabel('Deadline').fill('2026-08-15')
  await page.getByLabel('Location').fill('Emmen')
  await page.getByLabel('Profit score').fill('82')
  await page.getByRole('button', { name: 'Save opportunity' }).click()

  await expect(page.getByRole('row', { name: new RegExp(name) })).toBeVisible()
  await page.getByLabel('Opportunity name').fill(editedName)
  await page.getByLabel('Status').selectOption('applied')
  await page.getByRole('button', { name: 'Save opportunity' }).click()
  await expect(page.getByRole('row', { name: new RegExp(editedName) })).toContainText('applied')

  await page.getByRole('button', { name: 'Archive' }).click()
  await expect(page.getByText('No matching opportunities yet.')).toBeVisible()
  await page.locator('section.filters select').nth(1).selectOption('archived')
  await expect(page.getByRole('row', { name: new RegExp(editedName) })).toBeVisible()
  await page.getByRole('button', { name: 'Restore' }).click()

  await expect(page.getByText('No matching opportunities yet.')).toBeVisible()
  await page.locator('section.filters select').nth(1).selectOption('active')
  await expect(page.getByRole('row', { name: new RegExp(editedName) })).toBeVisible()
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: 'Delete' }).click()
  await expect(page.getByText(editedName)).toHaveCount(0)
})

test('creates, edits, and archives a venue', async ({ page }) => {
  const suffix = Date.now()
  const name = `E2E Venue ${suffix}`
  const editedName = `${name} updated`

  await page.goto('/')
  await page.getByRole('button', { name: 'New venue' }).click()
  await page.getByLabel('Venue External Id').fill(`VEN-E2E-${suffix}`)
  await page.getByLabel('Venue Name').fill(name)
  await page.getByRole('button', { name: 'Save venue' }).click()

  await expect(page.getByRole('heading', { name })).toBeVisible()
  await page.getByLabel('Venue Name').fill(editedName)
  await page.getByRole('button', { name: 'Save venue' }).click()
  await expect(page.getByRole('heading', { name: editedName })).toBeVisible()

  await page.getByRole('button', { name: 'Archive' }).click()
  await page.locator('.venue-filters select').nth(1).selectOption('false')
  await expect(page.getByRole('button', { name: new RegExp(editedName) })).toBeVisible()
})

test('previews and applies a venue research import', async ({ page }) => {
  const suffix = Date.now()
  const externalId = `VEN-E2E-IMPORT-${suffix}`
  const venueName = `E2E Imported Venue ${suffix}`
  const csv = [
    'venue_external_id,venue_name,research_status,confidence_rating,active',
    `${externalId},${venueName},discovered,E,true`,
  ].join('\n')

  await page.goto('/')
  await page.getByRole('button', { name: 'Import venues' }).click()
  const filename = `e2e-venues-${suffix}.csv`
  await page.getByLabel('Venue CSV').setInputFiles({
    name: filename,
    mimeType: 'text/csv',
    buffer: Buffer.from(csv),
  })
  await page.getByRole('button', { name: 'Preview import' }).click()

  await expect(page.getByRole('heading', { name: filename })).toBeVisible()
  await expect(page.getByRole('row', { name: new RegExp(venueName) })).toContainText('create')
  await page.getByRole('button', { name: 'Apply reviewed batch' }).click()
  await expect(page.getByText(/Import applied:/)).toBeVisible()
  await expect(page.getByRole('article').filter({ hasText: filename })).toContainText('1 created')
})

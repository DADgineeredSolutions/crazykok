import { defineConfig, devices } from '@playwright/test'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const deployedBaseUrl = process.env.E2E_BASE_URL
const runId = process.env.GITHUB_RUN_ID ?? String(process.pid)
const apiPort = 18_080
const webPort = 15_173
const databasePath = join(tmpdir(), `crazykok-e2e-${runId}.db`)
const attachmentRoot = join(tmpdir(), `crazykok-e2e-attachments-${runId}`)
const repositoryRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const python = process.env.E2E_PYTHON ?? 'python3'
const localRunName = `crazykok-e2e-${runId.replace(/[^a-zA-Z0-9_.-]/g, '-')}`
const publicApiBaseUrl = `http://127.0.0.1:${webPort}/api/v1`
process.env.E2E_CONTAINER_NAME = localRunName
const backendCommand = process.env.CI || process.env.E2E_PYTHON
  ? `${python} -m alembic -c backend/alembic.ini upgrade head && ${python} -m uvicorn backend.app.main:app --host 127.0.0.1 --port ${apiPort}`
  : `docker build --file docker/Dockerfile.api --tag ${localRunName} . && docker create --name ${localRunName} --publish 127.0.0.1:${apiPort}:8000 --env ADR_AUTHORING_ENABLED=false --env ATTACHMENT_ROOT=/tmp/e2e-attachments --env DATABASE_URL=sqlite:////tmp/e2e.db --env PUBLIC_API_BASE_URL=${publicApiBaseUrl} ${localRunName} && trap 'docker rm --force ${localRunName} >/dev/null 2>&1 || true' EXIT INT TERM && docker start --attach ${localRunName}`

export default defineConfig({
  testDir: './e2e',
  globalTeardown: './e2e/global-teardown.ts',
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: process.env.CI ? [['line'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: deployedBaseUrl ?? `http://127.0.0.1:${webPort}`,
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: deployedBaseUrl
    ? undefined
    : [
        {
          command: backendCommand,
          cwd: repositoryRoot,
          env: {
            ...process.env,
            ADR_AUTHORING_ENABLED: 'false',
            API_PORT: String(apiPort),
            ATTACHMENT_ROOT: attachmentRoot,
            DATABASE_URL: `sqlite:///${databasePath}`,
            DATA_DIR: join(tmpdir(), `crazykok-e2e-data-${runId}`),
            PUBLIC_API_BASE_URL: publicApiBaseUrl,
          },
          url: `http://127.0.0.1:${apiPort}/health`,
          reuseExistingServer: false,
          timeout: 120_000,
        },
        {
          command: `npm run dev -- --config vite.config.ts --host 127.0.0.1 --port ${webPort} --strictPort`,
          env: {
            ...process.env,
            VITE_API_PROXY_TARGET: `http://127.0.0.1:${apiPort}`,
          },
          url: `http://127.0.0.1:${webPort}`,
          reuseExistingServer: false,
          timeout: 120_000,
        },
      ],
})

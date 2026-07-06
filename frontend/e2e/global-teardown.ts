import { execFileSync } from 'node:child_process'

export default function globalTeardown() {
  const containerName = process.env.E2E_CONTAINER_NAME
  if (!containerName || process.env.CI || process.env.E2E_BASE_URL || process.env.E2E_PYTHON) return

  try {
    execFileSync('docker', ['rm', '--force', containerName], { stdio: 'ignore' })
  } catch {
    // The web-server process may already have removed the transient container.
  }
}

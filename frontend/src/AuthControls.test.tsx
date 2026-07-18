import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import AuthControls, { FULL_SIGN_OUT_PATH } from './AuthControls'

describe('AuthControls', () => {
  it('starts the configured full sign-out chain through the application host', () => {
    render(<AuthControls />)

    expect(screen.getByRole('link', { name: 'Log out' })).toHaveAttribute(
      'href',
      FULL_SIGN_OUT_PATH,
    )
  })
})

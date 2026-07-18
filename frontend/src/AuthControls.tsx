export const FULL_SIGN_OUT_PATH = '/logout'

export default function AuthControls() {
  return (
    <a className="logout-link" href={FULL_SIGN_OUT_PATH}>
      Log out
    </a>
  )
}

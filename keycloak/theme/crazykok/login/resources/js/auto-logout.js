// The bundled Keycloak instance is a disposable local IdP. Authentik cannot
// attach Keycloak's ID-token hint when logout starts from its app dashboard,
// so Keycloak otherwise pauses on an RP-initiated logout confirmation form.
// Auto-submit only that form; normal login and error pages are unchanged.
document.addEventListener("DOMContentLoaded", () => {
  const logoutForm = document.querySelector("#kc-logout-confirm form");
  if (logoutForm) {
    logoutForm.requestSubmit();
  }
});

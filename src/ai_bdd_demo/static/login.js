"use strict";

document.getElementById("login-form").addEventListener("reset", () => {
  // Let the native reset finish before returning keyboard focus to the account field.
  requestAnimationFrame(() => document.getElementById("username").focus());
});

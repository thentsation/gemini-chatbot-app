# CHANGELOG

<!-- version list -->

## v1.1.1 (2026-09-05)

### Bug Fixes

- Prune stale image tags left behind on deploy
  ([`c5895aa`](https://github.com/thentsation/gemini-chatbot-app/commit/c5895aa8f8b081741785329deed20a9efd3b0386))


## v1.1.0 (2026-09-04)

### Bug Fixes

- Gracefully handle missing Dependabot alerts permission
  ([`8313816`](https://github.com/thentsation/gemini-chatbot-app/commit/83138162158c2582fe6b8f8ec0cc8adba3e257eb))

- Pass --repo explicitly to gh CLI calls with no checkout
  ([`2a9aee4`](https://github.com/thentsation/gemini-chatbot-app/commit/2a9aee42ed6e4f51ebf2f0a447a5f6b4cb77986b))

- Send the workflow warning annotation to stderr, not the issue body
  ([`f023b9e`](https://github.com/thentsation/gemini-chatbot-app/commit/f023b9ece15dec814f8419bf635b5e0068bb2680))

- Use RELEASE_PAT to let semantic-release push past branch protection
  ([`5cdc31b`](https://github.com/thentsation/gemini-chatbot-app/commit/5cdc31bdcc3dd115df3195fa40426f23e9ec7825))

### Continuous Integration

- Add Dependency & Security Dashboard, label major Dependabot PRs
  ([`9d643d8`](https://github.com/thentsation/gemini-chatbot-app/commit/9d643d8f4f1a562a09864929d0f34024e31b465f))

- Gate Docker pipeline on CI success and add Dependabot auto-merge
  ([`54218d8`](https://github.com/thentsation/gemini-chatbot-app/commit/54218d8693c8146876a579ac7fbe5fddbd7a39cd))

### Features

- Auto-close the dashboard issue when nothing is pending
  ([`af7602f`](https://github.com/thentsation/gemini-chatbot-app/commit/af7602f2d03d8e1973762bf91907c6b335dd9a85))


## v1.0.5 (2026-09-03)

### Bug Fixes

- Point GHCR_IMAGE at the thentsation org after the repo transfer
  ([`a0fa10f`](https://github.com/thentsation/gemini-chatbot-app/commit/a0fa10f91f45f23c7e25c19a5db0dff398a47620))


## v1.0.4 (2026-09-03)

### Bug Fixes

- Drop GHA layer cache from the GHCR push build
  ([`40e860e`](https://github.com/thentsation/gemini-chatbot-app/commit/40e860ed1a5798860820b3c8e11b9446e3b9b86c))


## v1.0.3 (2026-09-03)

### Bug Fixes

- Keep genai.Client alive alongside its cached Chat session
  ([`a363e86`](https://github.com/thentsation/gemini-chatbot-app/commit/a363e86a2667d692193a8389cd7eb09dedc408a1))


## v1.0.2 (2026-09-03)

### Bug Fixes

- Use ETag-based optimistic concurrency for security list updates
  ([`cec9a43`](https://github.com/thentsation/gemini-chatbot-app/commit/cec9a4378fde4b3a60f48380ca3cae0b151127c0))


## v1.0.1 (2026-09-03)

### Bug Fixes

- Preserve trailing newline when writing SSH key from secret
  ([`840d638`](https://github.com/thentsation/gemini-chatbot-app/commit/840d6381b35602fe7132a996a4bc172f32e2a606))


## v1.0.0 (2026-09-03)

- Initial Release

# Frontend Design Update

## Final document-aligned polish (25 August 2026)

- Matched the internal workspace more closely to the dissertation screenshots with a clear purple-and-white hierarchy.
- Added a visible active state to the responsive sidebar navigation.
- Replaced dashboard emoji decorations with consistent inline SVG icons.
- Standardised panels, form focus states, authentication screens and primary actions.
- Retained the original group-event photograph on the Home page and removed the remaining rotated badge treatment.
- No backend endpoint, request payload, session rule or database behaviour was changed.

The application backend and API integration files were not modified.

## Visual improvements

- Premium dark AI-themed landing hero with stronger hierarchy
- Real event-photography imagery in the gallery
- Modern gradient buttons, cards, panels and background treatments
- Consistent dashboard sidebar and workspace header styling
- Improved hover states and responsive layouts
- Balanced dark and light sections for clearer visual separation
- Consistent inline SVG icon system instead of device-dependent emoji
- Active-section navigation, keyboard focus states and reduced-motion support
- Working gallery call-to-action and corrected service links
- Graceful visual fallbacks if an external event image cannot load

## Preserved application behaviour

- Existing routes and navigation
- Form fields and submission handlers
- API calls, event upload flow and selfie search
- Privacy, consent and retention controls
- Engineering content describing asynchronous processing, preprocessing,
  vector search, media optimisation and biometric safeguards

## Run locally

1. Open this folder in Terminal.
2. Run `npm install`.
3. Run `npm run dev`.
4. Open the local URL shown in Terminal.

The event photographs used in the landing gallery are loaded from Unsplash and
therefore require an internet connection to display.

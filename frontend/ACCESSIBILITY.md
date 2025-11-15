# Accessibility Implementation Guide

This document describes the accessibility features implemented in the Multilingual Education Platform frontend.

## WCAG 2.0 Level AA Compliance

### Perceivable

#### Text Alternatives (1.1)
- All images have alt text
- Form inputs have associated labels
- ARIA labels on interactive elements without visible text

#### Adaptable (1.3)
- Semantic HTML structure (header, nav, main, footer)
- Proper heading hierarchy (h1, h2, h3)
- Form labels programmatically associated with inputs
- ARIA landmarks for screen reader navigation

#### Distinguishable (1.4)
- Minimum contrast ratio of 4.5:1 for normal text
- High contrast mode option available
- Text can be resized up to 200% without loss of functionality
- Focus indicators visible on all interactive elements

### Operable

#### Keyboard Accessible (2.1)
- All functionality available via keyboard
- No keyboard traps
- Skip to main content link
- Visible focus indicators
- Logical tab order

#### Enough Time (2.2)
- No time limits on content interaction
- Audio can be paused and controlled by user

#### Navigable (2.4)
- Page titles describe topic or purpose
- Focus order follows logical sequence
- Link purpose clear from link text or context
- Multiple ways to locate content (navigation, search)
- Headings and labels describe topic or purpose

### Understandable

#### Readable (3.1)
- Language of page specified (lang attribute)
- Language of translated content specified
- OpenDyslexic font option for improved readability

#### Predictable (3.2)
- Navigation consistent across pages
- Components behave consistently
- No automatic context changes on focus

#### Input Assistance (3.3)
- Form validation with clear error messages
- Labels and instructions provided for inputs
- Error suggestions provided when possible

### Robust

#### Compatible (4.1)
- Valid HTML markup
- ARIA attributes used correctly
- Name, role, and value available for all UI components
- Status messages announced to screen readers

## Implemented Features

### 1. OpenDyslexic Font Toggle
**Location**: Accessibility Settings component
**Implementation**: 
- Checkbox control with proper label
- Preference saved in localStorage
- Applied via CSS class on body element
- ARIA described-by for additional context

### 2. ARIA Tags
**Coverage**: All interactive elements
**Examples**:
- `role="navigation"` on nav elements
- `role="main"` on main content area
- `role="contentinfo"` on footer
- `aria-label` on buttons and links
- `aria-describedby` for additional context
- `aria-live` for dynamic content updates
- `aria-expanded` for collapsible sections

### 3. Keyboard Navigation
**Features**:
- Tab navigation through all interactive elements
- Enter/Space activation for buttons
- Escape to close modals
- Arrow keys for component navigation
- Focus trap in modals
- Skip to main content link

**Utilities**: `src/utils/keyboardNavigation.js`

### 4. Screen Reader Support
**Features**:
- Semantic HTML structure
- ARIA landmarks
- Live regions for dynamic updates
- Hidden text for context (sr-only class)
- Proper heading hierarchy
- Form label associations

### 5. Pa11y Validation
**Configuration**: `.pa11yci.json`
**Standards**: WCAG2AA
**Runners**: axe, htmlcs

**Running Tests**:
```bash
npm run a11y
```

### 6. Additional Accessibility Features

#### Text Size Adjustment
- Four size options: small, medium, large, extra-large
- Applied globally via root element class
- Preference saved in localStorage

#### High Contrast Mode
- Toggle for increased contrast
- Applied via body class
- Preference saved in localStorage

#### Reduced Motion Support
- CSS media query for prefers-reduced-motion
- Animations disabled for users who prefer reduced motion

#### Focus Management
- Visible focus indicators (3px blue outline)
- Focus trap utilities for modals
- Logical focus order

## Testing Checklist

### Manual Testing

- [ ] Navigate entire site using only keyboard
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Verify all images have alt text
- [ ] Check color contrast ratios
- [ ] Test with browser zoom at 200%
- [ ] Verify form validation messages are announced
- [ ] Test high contrast mode
- [ ] Test OpenDyslexic font toggle
- [ ] Verify skip to main content link works
- [ ] Test with different text sizes

### Automated Testing

- [ ] Run Pa11y CI tests
- [ ] Validate HTML markup
- [ ] Check ARIA usage with browser dev tools
- [ ] Test with Lighthouse accessibility audit

### Screen Reader Testing

#### NVDA (Windows)
```
- Navigate with Tab/Shift+Tab
- Read with Down arrow
- Activate with Enter/Space
- Navigate landmarks with D
- Navigate headings with H
```

#### JAWS (Windows)
```
- Navigate with Tab/Shift+Tab
- Read with Down arrow
- Activate with Enter/Space
- Navigate landmarks with R
- Navigate headings with H
```

#### VoiceOver (macOS)
```
- Navigate with VO+Right/Left arrow
- Activate with VO+Space
- Navigate landmarks with VO+U
- Navigate headings with VO+Command+H
```

## Common Issues and Solutions

### Issue: Focus not visible
**Solution**: Added `:focus-visible` styles with 3px blue outline

### Issue: Screen reader not announcing dynamic content
**Solution**: Added `aria-live` regions with appropriate politeness levels

### Issue: Keyboard trap in modal
**Solution**: Implemented focus trap utility to cycle focus within modal

### Issue: Form errors not announced
**Solution**: Added `role="alert"` and `aria-live="polite"` to error messages

## Resources

- [WCAG 2.0 Guidelines](https://www.w3.org/WAI/WCAG20/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Resources](https://webaim.org/resources/)
- [Pa11y Documentation](https://pa11y.org/)
- [OpenDyslexic Font](https://opendyslexic.org/)

## Maintenance

### Adding New Components
1. Use semantic HTML
2. Add appropriate ARIA attributes
3. Ensure keyboard accessibility
4. Test with screen reader
5. Run Pa11y validation
6. Update this documentation

### Regular Audits
- Run Pa11y tests before each release
- Conduct manual keyboard testing
- Test with at least one screen reader
- Review new WCAG guidelines annually

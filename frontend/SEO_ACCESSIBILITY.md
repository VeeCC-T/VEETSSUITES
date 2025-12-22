# SEO and Accessibility Implementation

This document describes the SEO and accessibility features implemented in the VEETSSUITES frontend application.

## SEO Features

### Metadata System

The application uses Next.js 14's Metadata API for comprehensive SEO support:

#### Dynamic Metadata Generation
- **Location**: `frontend/lib/seo/metadata.ts`
- **Features**:
  - Dynamic title and description generation
  - Open Graph metadata for social sharing
  - Twitter Card metadata
  - Canonical URL management
  - Keywords management
  - Noindex support for private pages

#### Subsite-Specific Metadata
Each subsite has its own metadata generator:
- `generatePortfolioMetadata()` - Portfolio subsite
- `generatePharmxamMetadata()` - PHARMXAM subsite
- `generateHub3660Metadata()` - HUB3660 subsite
- `generateHealtheeMetadata()` - HEALTHEE subsite

#### Usage Example
```typescript
import { generatePharmxamMetadata } from '@/lib/seo';

export const metadata = generatePharmxamMetadata();
```

### Sitemap Generation

- **Location**: `frontend/app/sitemap.ts`
- **Features**:
  - Automatically generates sitemap.xml
  - Lists all public pages
  - Includes change frequency and priority
  - Accessible at `/sitemap.xml`

### Robots.txt

- **Location**: `frontend/app/robots.ts`
- **Features**:
  - Defines crawling rules for search engines
  - Disallows API routes and demo pages
  - References sitemap.xml
  - Accessible at `/robots.txt`

### Meta Tags Implemented

All pages include:
- Title tags (with site name suffix)
- Description meta tags
- Keywords meta tags
- Canonical URLs
- Open Graph tags (og:title, og:description, og:type, og:url, og:image, og:site_name)
- Twitter Card tags (twitter:card, twitter:title, twitter:description, twitter:image)
- Viewport meta tag
- Content-Type meta tag

## Accessibility Features

### WCAG 2.1 Level AA Compliance

The application implements comprehensive accessibility features to meet WCAG 2.1 Level AA standards:

#### Keyboard Navigation

1. **Focus Indicators**
   - All interactive elements have visible focus indicators
   - Custom focus styles defined in `globals.css`
   - 2px blue outline with 2px offset

2. **Skip to Main Content**
   - Skip link at the top of every page
   - Allows keyboard users to bypass navigation
   - Visible only when focused

3. **Keyboard Accessible Components**
   - All buttons support keyboard activation
   - Interactive cards support Enter and Space keys
   - Modal dialogs have focus trap
   - Dropdown menus support arrow key navigation

#### ARIA Labels and Roles

1. **Semantic HTML**
   - Proper heading hierarchy (h1 → h2 → h3)
   - Semantic elements (header, nav, main, footer, section, article)
   - Landmark roles for screen readers

2. **ARIA Attributes**
   - `aria-label` on interactive elements
   - `aria-labelledby` for sections
   - `aria-current="page"` for active navigation items
   - `aria-expanded` for expandable elements
   - `aria-haspopup` for dropdown menus
   - `aria-modal` for modal dialogs
   - `aria-busy` for loading states
   - `aria-hidden` for decorative elements

3. **Screen Reader Support**
   - `.sr-only` utility class for screen reader only content
   - Descriptive labels for all form inputs
   - Alternative text for images and icons
   - Hidden headings for section identification

#### Component Accessibility

1. **Button Component**
   - Loading state with aria-busy
   - Disabled state properly communicated
   - Optional aria-label support
   - Focus ring on keyboard focus

2. **Modal Component**
   - Focus trap implementation
   - Escape key to close
   - Focus management (auto-focus close button)
   - Backdrop click to close
   - Proper ARIA attributes

3. **Card Component**
   - Keyboard accessible when interactive
   - Proper role attribute
   - Focus indicator
   - Optional aria-label

4. **Navigation Component**
   - Proper navigation landmark
   - Active page indication
   - Mobile menu with proper ARIA
   - User menu with proper roles

### Accessibility Testing

#### Automated Testing
- **Tool**: jest-axe
- **Location**: `frontend/__tests__/accessibility.test.tsx`
- **Coverage**:
  - Home page
  - All UI components
  - Interactive elements
  - Modal dialogs

#### Running Tests
```bash
npm test -- accessibility.test.tsx
```

All tests verify WCAG 2.1 Level AA compliance using axe-core.

### Accessibility Utilities

**Location**: `frontend/lib/accessibility/`

Utility functions for keyboard navigation:
- `handleKeyboardActivation()` - Handle Enter/Space key activation
- `getFocusableElements()` - Get all focusable elements in a container
- `trapFocus()` - Trap focus within a container (for modals)
- `isKeyboardAccessible()` - Check if element is keyboard accessible

## Best Practices

### For Developers

1. **Always use semantic HTML**
   - Use proper heading hierarchy
   - Use semantic elements (header, nav, main, etc.)
   - Don't skip heading levels

2. **Provide text alternatives**
   - Add alt text to images
   - Use aria-label for icon buttons
   - Provide screen reader only text when needed

3. **Ensure keyboard accessibility**
   - All interactive elements must be keyboard accessible
   - Provide visible focus indicators
   - Implement logical tab order

4. **Test with automated tools**
   - Run accessibility tests before committing
   - Use browser DevTools accessibility audits
   - Test with screen readers when possible

5. **Use the provided utilities**
   - Import metadata generators for new pages
   - Use accessibility utilities for custom components
   - Follow existing component patterns

### Adding New Pages

When creating a new page:

1. **Add metadata**:
```typescript
import { generateMetadata } from '@/lib/seo';

export const metadata = generateMetadata({
  title: 'Page Title',
  description: 'Page description',
  keywords: ['keyword1', 'keyword2'],
});
```

2. **Use semantic HTML**:
```tsx
<main>
  <header>
    <h1>Page Title</h1>
  </header>
  <section aria-labelledby="section-heading">
    <h2 id="section-heading">Section Title</h2>
    {/* content */}
  </section>
</main>
```

3. **Add to sitemap** (if public):
Edit `frontend/app/sitemap.ts` to include the new page.

4. **Test accessibility**:
Add tests to `frontend/__tests__/accessibility.test.tsx`.

## Validation

### SEO Validation
- Use Google Search Console
- Check meta tags with browser DevTools
- Verify sitemap.xml is accessible
- Test social sharing previews

### Accessibility Validation
- Run automated tests: `npm test -- accessibility.test.tsx`
- Use Lighthouse in Chrome DevTools
- Test with keyboard navigation
- Test with screen readers (NVDA, JAWS, VoiceOver)
- Verify color contrast ratios

## Requirements Validated

This implementation validates the following requirements:

- **10.1**: 2xl rounded cards with soft shadows
- **10.2**: Clear navigation with visual indicators
- **10.3**: Responsive design
- **10.4**: WCAG 2.1 Level AA accessibility standards
- **10.5**: Visual feedback and focus indicators
- **11.1**: Semantic HTML with heading hierarchy
- **11.2**: Meta tags on all pages
- **11.3**: Open Graph and Twitter Card metadata
- **11.4**: Sitemap.xml generation

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Next.js Metadata API](https://nextjs.org/docs/app/building-your-application/optimizing/metadata)
- [jest-axe Documentation](https://github.com/nickcolley/jest-axe)
- [axe-core Rules](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)

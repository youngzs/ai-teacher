# AI Teaching Assistant System - Design System Documentation

## Overview

This design system provides a comprehensive set of design tokens, components, and guidelines specifically crafted for educational technology interfaces. It focuses on accessibility, usability, and the unique needs of both educators and students in programming education contexts.

## Design Principles

### 1. **Educational-First Design**
- Prioritize clarity and comprehension over aesthetics
- Support different learning styles and cognitive loads
- Design for sustained focus and concentration

### 2. **Accessibility by Default**
- WCAG 2.1 AA compliance minimum
- Support for screen readers and assistive technologies
- High contrast mode and reduced motion support
- Keyboard navigation optimization

### 3. **Teacher Efficiency**
- Minimize cognitive overhead for routine tasks
- Batch operations and quick actions
- Clear information hierarchy
- Contextual help and guidance

### 4. **Student Engagement**
- Progressive disclosure of complex information
- Clear feedback and progress indicators
- Encouraging and supportive visual language
- Gamification elements where appropriate

### 5. **Technical Context**
- Code-focused typography and syntax highlighting
- Developer-friendly interface patterns
- Support for multiple programming languages
- Integration with AI assistance features

## Color System

### Primary Colors (Educational Blue)
```css
--color-primary-50: #eff6ff   /* Backgrounds, subtle highlights */
--color-primary-100: #dbeafe  /* Light backgrounds */
--color-primary-200: #bfdbfe  /* Borders, dividers */
--color-primary-300: #93c5fd  /* Disabled states */
--color-primary-400: #60a5fa  /* Hover states */
--color-primary-500: #3b82f6  /* Default brand color */
--color-primary-600: #2563eb  /* Primary buttons, links */
--color-primary-700: #1d4ed8  /* Active states */
--color-primary-800: #1e40af  /* Dark backgrounds */
--color-primary-900: #1e3a8a  /* Text on light backgrounds */
```

### Semantic Colors

#### Success (Positive Feedback)
- Used for: Correct answers, successful submissions, achievements
- Primary: `#16a34a` (Green 600)
- Background: `#f0fdf4` (Green 50)

#### Warning (Attention Required)
- Used for: Pending reviews, approaching deadlines, suggestions
- Primary: `#d97706` (Amber 600)
- Background: `#fffbeb` (Amber 50)

#### Error (Critical Issues)
- Used for: Failed tests, errors, overdue assignments
- Primary: `#dc2626` (Red 600)
- Background: `#fef2f2` (Red 50)

#### AI Features
- Used for: AI-powered features, smart suggestions, automated feedback
- Primary: `#7c3aed` (Purple 600)
- Background: `#faf5ff` (Purple 50)

## Typography

### Font Families
- **Sans-serif**: Inter (UI text, headings)
- **Monospace**: Fira Code (code, data display)

### Type Scale
```css
--font-size-xs: 0.75rem    /* 12px - Captions, labels */
--font-size-sm: 0.875rem   /* 14px - Body text (small) */
--font-size-base: 1rem     /* 16px - Body text (default) */
--font-size-lg: 1.125rem   /* 18px - Subheadings */
--font-size-xl: 1.25rem    /* 20px - Headings */
--font-size-2xl: 1.5rem    /* 24px - Page titles */
--font-size-3xl: 1.875rem  /* 30px - Section titles */
--font-size-4xl: 2.25rem   /* 36px - Hero titles */
```

### Educational Typography Guidelines

#### Code Display
- Use `Fira Code` for all code content
- Minimum 14px font size for readability
- Line height: 1.5 for code blocks
- Syntax highlighting with semantic colors

#### Content Hierarchy
- H1: Page titles, main sections
- H2: Sub-sections, major components
- H3: Component titles, subsections
- Body: Use 16px minimum for sustained reading
- Captions: 12px for metadata, secondary info

## Spacing System

Based on 0.25rem (4px) increments for consistency:

```css
--spacing-1: 0.25rem   /* 4px */
--spacing-2: 0.5rem    /* 8px */
--spacing-3: 0.75rem   /* 12px */
--spacing-4: 1rem      /* 16px */
--spacing-5: 1.25rem   /* 20px */
--spacing-6: 1.5rem    /* 24px */
--spacing-8: 2rem      /* 32px */
--spacing-10: 2.5rem   /* 40px */
--spacing-12: 3rem     /* 48px */
--spacing-16: 4rem     /* 64px */
```

### Educational Spacing Guidelines
- **Cards**: 24px padding (spacing-6)
- **Form fields**: 16px spacing (spacing-4)
- **Section gaps**: 32px (spacing-8)
- **Page margins**: 24-48px based on screen size

## Component Library

### Cards
```css
/* Basic educational card */
.card {
  @apply bg-white rounded-lg border border-secondary-200 shadow-sm;
}

/* Interactive card (assignments, students) */
.card-interactive {
  @apply card transition-all duration-200 cursor-pointer;
  @apply hover:shadow-md hover:border-primary-300 hover:-translate-y-0.5;
}

/* Status cards */
.card-success { @apply bg-success-50 border-success-200 border-l-4 border-l-success-500; }
.card-warning { @apply bg-warning-50 border-warning-200 border-l-4 border-l-warning-500; }
.card-error { @apply bg-error-50 border-error-200 border-l-4 border-l-error-500; }
.card-ai { @apply bg-purple-50 border-purple-200 border-l-4 border-l-purple-500; }
```

### Buttons
```css
/* Primary educational button */
.btn-primary-educational {
  @apply bg-primary-600 hover:bg-primary-700 active:bg-primary-800;
  @apply text-white font-medium px-4 py-2 rounded-lg;
  @apply transition-colors duration-150;
  @apply focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2;
}

/* AI feature button */
.btn-ai-feature {
  @apply bg-purple-600 hover:bg-purple-700 text-white;
  @apply flex items-center px-4 py-2 rounded-lg;
  @apply transition-all duration-150;
}
```

### Badges and Status Indicators
```css
.badge {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
}

/* Difficulty badges */
.difficulty-easy { @apply badge bg-green-100 text-green-800; }
.difficulty-medium { @apply badge bg-yellow-100 text-yellow-800; }
.difficulty-hard { @apply badge bg-red-100 text-red-800; }

/* Status badges */
.status-active { @apply badge bg-green-100 text-green-800; }
.status-draft { @apply badge bg-yellow-100 text-yellow-800; }
.status-published { @apply badge bg-blue-100 text-blue-800; }
```

## Responsive Breakpoints

```css
/* Mobile First Approach */
--breakpoint-sm: 640px   /* Large phones */
--breakpoint-md: 768px   /* Tablets */
--breakpoint-lg: 1024px  /* Small desktops */
--breakpoint-xl: 1280px  /* Large desktops */
--breakpoint-2xl: 1536px /* Very large screens */
```

### Responsive Patterns

#### Dashboard Layouts
- **Mobile**: Single column, stacked cards
- **Tablet**: 2-column grid, collapsible sidebar
- **Desktop**: 3-4 column grid, persistent sidebar
- **Large**: Multi-panel layout with advanced features

#### Code Editor
- **Mobile**: Full-width, vertical tabs
- **Tablet**: Split view with collapsible panels
- **Desktop**: Multi-pane layout with results panel
- **Large**: Enhanced debugging and AI assistance panels

## Accessibility Features

### Focus Management
- 3px outline with 2px offset for focus indicators
- High contrast mode support
- Skip navigation links
- Focus trap for modals and dropdowns

### Screen Reader Support
- Semantic HTML structure
- ARIA labels and descriptions
- Live regions for dynamic content
- Screen reader only content classes

### Keyboard Navigation
- Tab order optimization
- Keyboard shortcuts for common actions
- Enhanced keyboard indicators
- Modal and dropdown navigation

### Color Accessibility
- WCAG AA contrast ratios (4.5:1 minimum)
- Color-blind friendly indicators with patterns/icons
- High contrast mode overrides
- Alternative text for color-coded information

## Theme System

### Light Theme (Default)
Optimized for prolonged reading and code review with comfortable contrast ratios.

### Dark Theme
Reduces eye strain during extended coding sessions, popular among developers.

### High Contrast Theme
Enhanced accessibility for users with visual impairments, meets WCAG AAA standards.

### Theme Implementation
```css
:root[data-theme="light"] { /* Light theme variables */ }
:root[data-theme="dark"] { /* Dark theme variables */ }
:root[data-theme="high-contrast"] { /* High contrast variables */ }
```

## Educational Patterns

### Assignment Interface
- **Problem Statement**: Clear typography hierarchy
- **Code Editor**: Syntax highlighting, error indicators
- **Test Results**: Color-coded with text alternatives
- **AI Feedback**: Distinguished visual treatment

### Dashboard Patterns
- **Stats Overview**: Icon + number + label format
- **Progress Indicators**: Visual + textual progress
- **Activity Feed**: Chronological, with clear categorization
- **Quick Actions**: Large touch targets, clear labels

### Feedback Display
- **Success Feedback**: Green accent, positive language
- **Improvement Areas**: Blue accent, constructive tone
- **Errors**: Red accent, clear guidance
- **AI Suggestions**: Purple accent, helpful recommendations

## Animation and Interactions

### Performance Considerations
- Respect `prefers-reduced-motion`
- GPU-accelerated transforms
- Minimal layout thrashing
- Efficient transitions (opacity, transform)

### Educational Animations
```css
/* Subtle progress animations */
.animate-progress { animation: progressFill 0.8s ease-out; }

/* Gentle attention grabbers */
.animate-bounce-subtle { animation: bounceSubtle 2s infinite; }

/* Smooth state transitions */
.transition-educational { 
  transition: background-color 0.2s, border-color 0.2s, 
              color 0.2s, box-shadow 0.2s; 
}
```

## Code Syntax Highlighting

### Color Scheme
```css
--code-bg: #1e293b        /* Dark background */
--code-text: #4ade80      /* Primary text (green) */
--code-keyword: #60a5fa   /* Keywords (blue) */
--code-string: #fbbf24    /* Strings (amber) */
--code-comment: #94a3b8   /* Comments (gray) */
--code-function: #c084fc  /* Functions (purple) */
--code-variable: #86efac  /* Variables (light green) */
--code-error: #f87171     /* Errors (red) */
```

### Language Support
- C: Structured highlighting for systems programming
- Python: Clear indentation and keyword highlighting
- Generic: Fallback highlighting for other languages

## Usage Guidelines

### Do's
✅ Use consistent spacing throughout interfaces
✅ Provide clear feedback for user actions
✅ Include alternative text for visual information
✅ Test with screen readers and keyboard navigation
✅ Use semantic colors (success = green, error = red)
✅ Include loading states for async operations

### Don'ts
❌ Use color alone to convey important information
❌ Create interfaces that require precise mouse control
❌ Override user's motion preferences
❌ Use animated GIFs or auto-playing videos
❌ Create touch targets smaller than 44x44px
❌ Use placeholder text as labels

## Implementation

### CSS Architecture
```
src/styles/
├── design-tokens.css    # Core design system variables
├── themes.css          # Theme-specific overrides
├── components.css      # Reusable component styles
├── utilities.css       # Utility classes
├── accessibility.css   # Accessibility enhancements
└── responsive.css      # Responsive design patterns
```

### Import Order
```css
@import './styles/design-tokens.css';
@import './styles/themes.css';
@import './styles/components.css';
@import './styles/utilities.css';
@import './styles/accessibility.css';
@import './styles/responsive.css';
```

## Testing and Validation

### Accessibility Testing
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Keyboard navigation testing
- Color contrast verification
- Focus management validation

### Responsive Testing
- Mobile device testing (iOS Safari, Chrome Mobile)
- Tablet testing (iPad, Android tablets)
- Desktop browser testing (Chrome, Firefox, Safari, Edge)
- Print layout verification

### Performance Testing
- Animation performance on low-end devices
- Loading performance on slow connections
- Memory usage with large datasets

## Maintenance and Evolution

### Version Control
- Semantic versioning for design system changes
- Migration guides for breaking changes
- Comprehensive changelog maintenance

### Documentation Updates
- Keep examples current with implementation
- Regular accessibility audit updates
- Performance benchmark updates
- New pattern documentation

### Feedback Integration
- User testing insights
- Developer experience improvements
- Accessibility expert reviews
- Educational effectiveness studies

---

This design system is living documentation that evolves with the needs of educators and students in programming education. Regular updates ensure continued effectiveness and accessibility compliance.
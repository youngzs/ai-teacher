# AI Teaching Assistant - Frontend Development Guide

## Project Overview

This is the React TypeScript frontend for the AI Teaching Assistant System. The application provides an intuitive interface for both teachers and students to interact with the AI-powered programming education platform.

## Tech Stack

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite 7
- **Routing**: React Router v7
- **State Management**: Zustand
- **Styling**: Tailwind CSS 4
- **UI Components**: Custom component library + Headless UI
- **Icons**: Heroicons + Lucide React
- **HTTP Client**: Native fetch API with custom wrapper

## Project Structure

```
src/
├── assets/           # Static assets (images, fonts, etc.)
├── components/       # React components
│   ├── common/      # Shared/common components
│   ├── layout/      # Layout components (Header, Sidebar, etc.)
│   └── ui/          # Reusable UI components
├── hooks/           # Custom React hooks
├── pages/           # Page components
├── routes/          # Routing configuration
├── services/        # API services and HTTP client
├── store/           # Zustand state management
├── types/           # TypeScript type definitions
└── utils/           # Utility functions and helpers
```

## Development Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration values.

3. **Start development server**:
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Component Architecture

### UI Components

Our custom UI component library is located in `src/components/ui/`. All components follow these principles:

- **Accessibility**: ARIA attributes and keyboard navigation
- **Customization**: Props for styling and behavior
- **Type Safety**: Full TypeScript support
- **Consistency**: Following design system patterns

#### Core Components:
- `Button` - Various button styles and states
- `Input` - Form inputs with validation
- `Card` - Content containers
- `Modal` - Dialog overlays
- `Table` - Data tables with sorting/pagination
- `Alert` - Status messages
- `Loading` - Loading states and skeletons
- `Form` - Form wrapper with state management

### State Management

We use **Zustand** for state management with these stores:

- **authStore** (`src/store/authStore.ts`): User authentication and profile
- **appStore** (`src/store/appStore.ts`): Global app state, theme, notifications

#### Usage Example:
```typescript
import { useAuthStore } from '@store/authStore';

const MyComponent = () => {
  const { user, login, logout } = useAuthStore();
  // Component logic
};
```

### Routing

Routes are configured in `src/routes/index.tsx` using React Router v7:

- **Public Routes**: Login, register (accessible when not authenticated)
- **Protected Routes**: Dashboard, profile (require authentication)
- **Role-based Routes**: Teacher and student specific pages

#### Route Protection:
```typescript
<ProtectedRoute requiredRole="teacher">
  <TeacherDashboard />
</ProtectedRoute>
```

## API Integration

API services are organized in `src/services/api.ts`:

### API Client
- Automatic token management
- Request/response interceptors
- Error handling
- Type-safe responses

### Custom Hooks
Use our custom API hooks for data fetching:

```typescript
import { useApi, useApiMutation } from '@hooks/useApi';
import { api } from '@services/api';

// Query hook
const { data, loading, error, execute } = useApi(api.course.getCourses);

// Mutation hook
const { mutate, loading } = useApiMutation(api.course.createCourse, {
  onSuccess: (data) => console.log('Course created:', data),
  onError: (error) => console.error('Failed:', error),
});
```

## Styling Guidelines

### Tailwind CSS

We use Tailwind CSS for styling with these conventions:

1. **Responsive Design**: Mobile-first approach
2. **Dark Mode**: Theme system support
3. **Component Classes**: Avoid repetition with component abstractions
4. **Design Tokens**: Consistent spacing, colors, and typography

### Class Utilities

We provide a `cn()` utility for conditional classes:

```typescript
import { cn } from '@utils';

const className = cn(
  'base-classes',
  variant === 'primary' && 'primary-styles',
  disabled && 'disabled-styles'
);
```

## Type System

### Core Types

All TypeScript types are defined in `src/types/index.ts`:

- **User Types**: User, UserRole, AuthState
- **Course Types**: Course, Assignment, Submission
- **UI Types**: Component props and state interfaces
- **API Types**: Request/response shapes

### Path Aliases

We use TypeScript path mapping for cleaner imports:

```typescript
import { Button } from '@components/ui';
import { useAuth } from '@hooks';
import { api } from '@services/api';
import type { User } from '@types';
```

## Performance Considerations

### Code Splitting

Vite automatically handles code splitting, but we also configure manual chunks:

```javascript
// vite.config.ts
rollupOptions: {
  output: {
    manualChunks: {
      vendor: ['react', 'react-dom'],
      router: ['react-router-dom'],
      ui: ['@headlessui/react', '@heroicons/react'],
    },
  },
},
```

### Optimization Tips

1. **Lazy Loading**: Use `React.lazy()` for page components
2. **Memoization**: Use `useMemo()` and `useCallback()` judiciously
3. **Bundle Analysis**: Run `npm run build` and analyze bundle sizes
4. **Image Optimization**: Use appropriate formats and sizes

## Testing Guidelines

### Testing Strategy

1. **Unit Tests**: Component logic and utility functions
2. **Integration Tests**: API integration and user workflows
3. **E2E Tests**: Critical user journeys

### Testing Tools

- **Jest**: Unit test runner
- **React Testing Library**: Component testing
- **Cypress**: End-to-end testing

## Build and Deployment

### Development Build
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Environment Variables

Configure these in your `.env` file:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=AI Teaching Assistant
VITE_ENABLE_DEVTOOLS=true
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure path aliases are configured in both `vite.config.ts` and `tsconfig.json`
2. **Build Failures**: Check TypeScript errors with `npm run type-check`
3. **Styling Issues**: Verify Tailwind CSS classes and purge settings

### Development Tips

1. **Hot Reload**: Vite provides fast HMR out of the box
2. **DevTools**: Use React DevTools browser extension
3. **TypeScript**: Enable strict mode for better type safety

## Contributing

### Code Style

1. **Formatting**: Use Prettier (configured in `.prettierrc`)
2. **Linting**: Follow ESLint rules (configured in `eslint.config.js`)
3. **TypeScript**: Use strict type checking
4. **Components**: Follow functional component patterns with hooks

### Git Workflow

1. Create feature branches from `main`
2. Use conventional commits
3. Ensure all tests pass before merging
4. Code review required for all PRs

### File Naming

- **Components**: PascalCase (`UserProfile.tsx`)
- **Hooks**: camelCase with `use` prefix (`useAuth.ts`)
- **Utilities**: camelCase (`formatDate.ts`)
- **Types**: PascalCase (`UserTypes.ts`)

## Resources

- [React Documentation](https://reactjs.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [React Router](https://reactrouter.com/)
- [Vite Guide](https://vitejs.dev/guide/)

## Support

For development questions or issues:
1. Check this documentation first
2. Review existing issues in the project repository
3. Create a new issue with detailed description and reproduction steps
4. Reach out to the development team on Slack
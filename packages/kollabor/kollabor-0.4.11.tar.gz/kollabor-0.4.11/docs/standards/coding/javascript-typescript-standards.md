# JavaScript/TypeScript Coding Standards

## Overview
This document establishes comprehensive coding standards for JavaScript and TypeScript development within AI-assisted development workflows, ensuring consistency, maintainability, and quality across all JavaScript/TypeScript projects.

## Core Principles

### 1. Type Safety First
- **TypeScript by Default**: All new projects use TypeScript
- **Strict Type Checking**: Enable strict mode in TypeScript configuration
- **Progressive Enhancement**: Gradually migrate JavaScript to TypeScript
- **Type Documentation**: Types serve as living documentation

### 2. Modern JavaScript Standards
- **ES2022+ Features**: Use latest JavaScript features appropriately
- **Async/Await**: Prefer async/await over Promises and callbacks
- **Module System**: Use ES6 modules consistently
- **Immutability**: Favor immutable patterns where appropriate

### 3. AI-Enhanced Development
- **Claude Code Integration**: Leverage AI for code generation and review
- **Automated Quality Checks**: AI-powered linting and formatting
- **Intelligent Refactoring**: AI-assisted code optimization
- **Documentation Generation**: AI-generated code documentation

## TypeScript Configuration Standards

### Base TypeScript Configuration
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "composite": false,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "removeComments": false,
    "importHelpers": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true
  },
  "include": [
    "src/**/*",
    "tests/**/*",
    "types/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "build"
  ]
}
```

### Project-Specific Configurations

#### React Project Configuration
```json
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "jsx": "react-jsx",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "types": ["react", "react-dom", "@testing-library/jest-dom"]
  },
  "include": [
    "src/**/*.tsx",
    "src/**/*.ts"
  ]
}
```

#### Node.js Project Configuration
```json
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "module": "CommonJS",
    "target": "ES2020",
    "lib": ["ES2020"],
    "types": ["node", "jest"],
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true
  },
  "include": [
    "src/**/*.ts",
    "scripts/**/*.ts"
  ]
}
```

## Code Structure and Organization

### File and Directory Naming
```typescript
// Directory structure
src/
├── components/           // React components
│   ├── ui/              // Reusable UI components
│   ├── forms/           // Form components
│   └── layouts/         // Layout components
├── services/            // Business logic and API services
├── utils/               // Utility functions
├── types/               // Type definitions
├── constants/           // Application constants
├── hooks/               // Custom React hooks (React projects)
└── tests/               // Test files

// File naming conventions
PascalCase:    Component.tsx, ServiceClass.ts
camelCase:     utilityFunction.ts, apiService.ts
kebab-case:    component-name.stories.tsx, test-utils.ts
UPPER_CASE:    CONSTANTS.ts, CONFIG.ts
```

### Import/Export Standards
```typescript
// Import order (enforced by ESLint)
// 1. Node modules
import React, { useState, useEffect } from 'react';
import { Router } from 'express';
import axios from 'axios';

// 2. Internal modules (absolute paths)
import { ApiService } from '@/services/ApiService';
import { UserTypes } from '@/types/User';

// 3. Relative imports
import { Button } from '../ui/Button';
import { validateEmail } from './validation';

// Export standards
// Named exports for utilities and multiple exports
export { validateEmail, validatePhone };
export type { ValidationResult };

// Default exports for single-purpose modules
export default class UserService {
  // Implementation
}
```

## Type Definitions and Interfaces

### Interface Design Standards
```typescript
// Interface naming: Use PascalCase with descriptive names
interface User {
  readonly id: string;
  email: string;
  name: string;
  createdAt: Date;
  updatedAt: Date;
}

// Use readonly for immutable properties
interface ApiResponse<T> {
  readonly data: T;
  readonly success: boolean;
  readonly message?: string;
  readonly errors?: ValidationError[];
}

// Generic constraints for better type safety
interface Repository<T extends { id: string }> {
  findById(id: string): Promise<T | null>;
  create(entity: Omit<T, 'id'>): Promise<T>;
  update(id: string, updates: Partial<T>): Promise<T>;
  delete(id: string): Promise<void>;
}

// Utility types for common patterns
type CreateUserRequest = Omit<User, 'id' | 'createdAt' | 'updatedAt'>;
type UpdateUserRequest = Partial<Pick<User, 'email' | 'name'>>;
type UserResponse = Pick<User, 'id' | 'email' | 'name'>;
```

### Union Types and Discriminated Unions
```typescript
// Simple union types
type Theme = 'light' | 'dark' | 'system';
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// Discriminated unions for complex state management
type LoadingState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: unknown }
  | { status: 'error'; error: string };

// Type guards for discriminated unions
function isSuccessState(state: LoadingState): state is Extract<LoadingState, { status: 'success' }> {
  return state.status === 'success';
}
```

## Function and Class Standards

### Function Declaration Standards
```typescript
// Prefer function declarations for top-level functions
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// Use arrow functions for callbacks and short functions
const processItems = (items: Item[]) => items.map(item => ({ ...item, processed: true }));

// Async function standards
async function fetchUserData(userId: string): Promise<User | null> {
  try {
    const response = await apiClient.get<User>(`/users/${userId}`);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch user data', { userId, error });
    return null;
  }
}

// Generic function with constraints
function createRepository<T extends { id: string }>(
  entityName: string
): Repository<T> {
  return new GenericRepository<T>(entityName);
}
```

### Class Design Standards
```typescript
// Class naming: PascalCase with descriptive names
class UserService {
  private readonly apiClient: ApiClient;
  private readonly cache: Map<string, User> = new Map();

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  // Public methods first
  public async getUser(id: string): Promise<User | null> {
    // Check cache first
    const cachedUser = this.cache.get(id);
    if (cachedUser) {
      return cachedUser;
    }

    // Fetch from API
    const user = await this.fetchUserFromApi(id);
    if (user) {
      this.cache.set(id, user);
    }

    return user;
  }

  // Private methods last
  private async fetchUserFromApi(id: string): Promise<User | null> {
    try {
      const response = await this.apiClient.get<User>(`/users/${id}`);
      return response.data;
    } catch (error) {
      this.handleError('fetchUserFromApi', error, { id });
      return null;
    }
  }

  private handleError(method: string, error: unknown, context?: Record<string, unknown>): void {
    logger.error(`UserService.${method} failed`, { error, context });
  }
}

// Abstract base classes for common patterns
abstract class BaseRepository<T extends { id: string }> {
  protected abstract entityName: string;

  public abstract findById(id: string): Promise<T | null>;
  public abstract create(entity: Omit<T, 'id'>): Promise<T>;
  
  protected validateEntity(entity: unknown): entity is T {
    // Common validation logic
    return typeof entity === 'object' && entity !== null && 'id' in entity;
  }
}
```

## Error Handling Standards

### Error Types and Hierarchy
```typescript
// Base error class
abstract class AppError extends Error {
  public abstract readonly code: string;
  public abstract readonly statusCode: number;
  public readonly timestamp: Date;

  constructor(message: string, public readonly context?: Record<string, unknown>) {
    super(message);
    this.name = this.constructor.name;
    this.timestamp = new Date();
    Error.captureStackTrace(this, this.constructor);
  }
}

// Specific error types
class ValidationError extends AppError {
  public readonly code = 'VALIDATION_ERROR';
  public readonly statusCode = 400;

  constructor(
    message: string,
    public readonly field: string,
    context?: Record<string, unknown>
  ) {
    super(message, { ...context, field });
  }
}

class NotFoundError extends AppError {
  public readonly code = 'NOT_FOUND';
  public readonly statusCode = 404;
}

class UnauthorizedError extends AppError {
  public readonly code = 'UNAUTHORIZED';
  public readonly statusCode = 401;
}

// Result type for error handling
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };

// Utility function for safe async operations
async function safeAsync<T>(
  operation: () => Promise<T>
): Promise<Result<T>> {
  try {
    const data = await operation();
    return { success: true, data };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error : new Error(String(error))
    };
  }
}
```

### Error Handling Patterns
```typescript
// Service layer error handling
class ApiService {
  public async fetchData<T>(url: string): Promise<Result<T, ApiError>> {
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        return {
          success: false,
          error: new ApiError(`HTTP ${response.status}: ${response.statusText}`, {
            url,
            status: response.status,
            statusText: response.statusText
          })
        };
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: new ApiError('Network error', { url, originalError: error })
      };
    }
  }
}

// Usage pattern
async function getUserData(id: string): Promise<User | null> {
  const result = await apiService.fetchData<User>(`/users/${id}`);
  
  if (!result.success) {
    logger.error('Failed to fetch user', { id, error: result.error });
    return null;
  }

  return result.data;
}
```

## Async Programming Standards

### Promise and Async/Await Patterns
```typescript
// Prefer async/await over .then()/.catch()
// Good
async function processUserData(userId: string): Promise<ProcessedUser | null> {
  try {
    const user = await fetchUser(userId);
    if (!user) return null;

    const profile = await fetchUserProfile(user.id);
    const preferences = await fetchUserPreferences(user.id);

    return {
      ...user,
      profile,
      preferences,
      processedAt: new Date()
    };
  } catch (error) {
    logger.error('Failed to process user data', { userId, error });
    return null;
  }
}

// Avoid
function processUserDataBad(userId: string): Promise<ProcessedUser | null> {
  return fetchUser(userId)
    .then(user => {
      if (!user) return null;
      return fetchUserProfile(user.id)
        .then(profile => {
          return fetchUserPreferences(user.id)
            .then(preferences => ({
              ...user,
              profile,
              preferences,
              processedAt: new Date()
            }));
        });
    })
    .catch(error => {
      logger.error('Failed to process user data', { userId, error });
      return null;
    });
}
```

### Concurrent Operations
```typescript
// Parallel execution for independent operations
async function loadDashboardData(userId: string): Promise<DashboardData> {
  // Execute all requests concurrently
  const [user, posts, notifications, analytics] = await Promise.all([
    fetchUser(userId),
    fetchUserPosts(userId),
    fetchNotifications(userId),
    fetchAnalytics(userId)
  ]);

  return {
    user,
    posts,
    notifications,
    analytics
  };
}

// Sequential execution when operations depend on each other
async function createUserWithProfile(userData: CreateUserRequest): Promise<User> {
  // Must be sequential - profile creation depends on user ID
  const user = await createUser(userData);
  const profile = await createProfile(user.id, userData.profileData);
  
  return {
    ...user,
    profile
  };
}

// Promise.allSettled for handling partial failures
async function syncMultipleServices(data: SyncData[]): Promise<SyncResult[]> {
  const promises = data.map(item => syncService(item));
  const results = await Promise.allSettled(promises);

  return results.map((result, index) => ({
    id: data[index].id,
    success: result.status === 'fulfilled',
    data: result.status === 'fulfilled' ? result.value : null,
    error: result.status === 'rejected' ? result.reason : null
  }));
}
```

## Testing Standards

### Unit Testing with Jest and TypeScript
```typescript
// Test file naming: *.test.ts or *.spec.ts
// utils/validation.test.ts

import { validateEmail, validatePassword, ValidationResult } from './validation';

describe('Email Validation', () => {
  it('should accept valid email addresses', () => {
    const validEmails = [
      'user@example.com',
      'test.user+tag@domain.co.uk',
      'user123@test-domain.com'
    ];

    validEmails.forEach(email => {
      const result = validateEmail(email);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  it('should reject invalid email addresses', () => {
    const invalidEmails = [
      'invalid-email',
      '@domain.com',
      'user@',
      'user space@domain.com'
    ];

    invalidEmails.forEach(email => {
      const result = validateEmail(email);
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  it('should provide specific error messages', () => {
    const result = validateEmail('invalid-email');
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Invalid email format');
  });
});

// Mock external dependencies
jest.mock('../services/ApiService');
const mockApiService = ApiService as jest.Mocked<typeof ApiService>;

describe('UserService', () => {
  let userService: UserService;

  beforeEach(() => {
    jest.clearAllMocks();
    userService = new UserService(mockApiService);
  });

  it('should fetch user from API when not in cache', async () => {
    const mockUser: User = {
      id: '123',
      email: 'test@example.com',
      name: 'Test User',
      createdAt: new Date(),
      updatedAt: new Date()
    };

    mockApiService.get.mockResolvedValue({ data: mockUser });

    const result = await userService.getUser('123');

    expect(result).toEqual(mockUser);
    expect(mockApiService.get).toHaveBeenCalledWith('/users/123');
  });
});
```

### Integration Testing
```typescript
// Integration test example
describe('User API Integration', () => {
  let app: Application;
  let testDb: TestDatabase;

  beforeAll(async () => {
    testDb = await TestDatabase.create();
    app = createApp({ database: testDb });
  });

  afterAll(async () => {
    await testDb.cleanup();
  });

  beforeEach(async () => {
    await testDb.reset();
  });

  it('should create and retrieve user', async () => {
    const userData = {
      email: 'test@example.com',
      name: 'Test User'
    };

    // Create user
    const createResponse = await request(app)
      .post('/api/users')
      .send(userData)
      .expect(201);

    expect(createResponse.body).toMatchObject({
      id: expect.any(String),
      email: userData.email,
      name: userData.name,
      createdAt: expect.any(String)
    });

    // Retrieve user
    const getResponse = await request(app)
      .get(`/api/users/${createResponse.body.id}`)
      .expect(200);

    expect(getResponse.body).toEqual(createResponse.body);
  });
});
```

## Performance and Optimization Standards

### Memory Management
```typescript
// Proper cleanup of resources
class EventManager {
  private listeners: Map<string, Function[]> = new Map();
  private timers: Set<NodeJS.Timeout> = new Set();

  public addEventListener(event: string, callback: Function): () => void {
    const listeners = this.listeners.get(event) || [];
    listeners.push(callback);
    this.listeners.set(event, listeners);

    // Return cleanup function
    return () => {
      const currentListeners = this.listeners.get(event) || [];
      const index = currentListeners.indexOf(callback);
      if (index > -1) {
        currentListeners.splice(index, 1);
        if (currentListeners.length === 0) {
          this.listeners.delete(event);
        }
      }
    };
  }

  public setTimeout(callback: Function, delay: number): NodeJS.Timeout {
    const timer = setTimeout(() => {
      this.timers.delete(timer);
      callback();
    }, delay);
    
    this.timers.add(timer);
    return timer;
  }

  public cleanup(): void {
    // Clear all listeners
    this.listeners.clear();
    
    // Clear all timers
    this.timers.forEach(timer => clearTimeout(timer));
    this.timers.clear();
  }
}
```

### Lazy Loading and Code Splitting
```typescript
// Dynamic imports for code splitting
class ModuleLoader {
  private loadedModules: Map<string, any> = new Map();

  public async loadModule<T>(moduleName: string): Promise<T> {
    if (this.loadedModules.has(moduleName)) {
      return this.loadedModules.get(moduleName);
    }

    let module: T;
    
    switch (moduleName) {
      case 'chart':
        module = await import('./modules/ChartModule');
        break;
      case 'analytics':
        module = await import('./modules/AnalyticsModule');
        break;
      default:
        throw new Error(`Unknown module: ${moduleName}`);
    }

    this.loadedModules.set(moduleName, module);
    return module;
  }
}

// React lazy loading
const LazyComponent = React.lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <LazyComponent />
    </Suspense>
  );
}
```

## Security Standards

### Input Validation and Sanitization
```typescript
// Input validation with Zod
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email('Invalid email format'),
  name: z.string().min(2, 'Name must be at least 2 characters').max(50, 'Name too long'),
  age: z.number().int().min(13, 'Must be at least 13 years old').max(120, 'Invalid age'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Password must contain uppercase, lowercase, and number')
});

type CreateUserRequest = z.infer<typeof CreateUserSchema>;

// Validation middleware
function validateInput<T>(schema: z.ZodSchema<T>) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      const validatedData = schema.parse(req.body);
      req.body = validatedData;
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: 'Validation failed',
          details: error.errors.map(err => ({
            field: err.path.join('.'),
            message: err.message
          }))
        });
      }
      next(error);
    }
  };
}
```

### Secure API Design
```typescript
// Secure service implementation
class SecureUserService {
  constructor(
    private readonly userRepository: UserRepository,
    private readonly encryptionService: EncryptionService,
    private readonly auditLogger: AuditLogger
  ) {}

  public async createUser(
    userData: CreateUserRequest,
    requestContext: RequestContext
  ): Promise<Result<User, ValidationError>> {
    // Audit log the attempt
    this.auditLogger.log('USER_CREATE_ATTEMPT', {
      email: userData.email,
      requestId: requestContext.requestId,
      userAgent: requestContext.userAgent,
      ip: requestContext.ip
    });

    try {
      // Hash password before storage
      const hashedPassword = await this.encryptionService.hashPassword(userData.password);
      
      // Create user with hashed password
      const user = await this.userRepository.create({
        ...userData,
        password: hashedPassword,
        createdBy: requestContext.userId
      });

      // Audit log success (without sensitive data)
      this.auditLogger.log('USER_CREATE_SUCCESS', {
        userId: user.id,
        email: user.email,
        requestId: requestContext.requestId
      });

      // Return user without password
      const { password, ...safeUser } = user;
      return { success: true, data: safeUser as User };

    } catch (error) {
      // Audit log failure
      this.auditLogger.log('USER_CREATE_FAILURE', {
        email: userData.email,
        error: error.message,
        requestId: requestContext.requestId
      });

      return {
        success: false,
        error: new ValidationError('Failed to create user', 'general')
      };
    }
  }
}
```

## AI-Enhanced Development Workflows

### Claude Code Integration Patterns
```typescript
// AI-assisted component generation prompt template
const COMPONENT_GENERATION_PROMPT = `
Generate a TypeScript React component with the following requirements:

Requirements:
- Component name: {componentName}
- Props interface: {propsInterface}
- Functionality: {functionality}
- Styling approach: {stylingApproach}

Standards to follow:
1. Use TypeScript with strict typing
2. Follow React functional component patterns
3. Include proper error handling
4. Add comprehensive JSDoc comments
5. Include accessibility attributes
6. Use semantic HTML elements
7. Implement proper event handling
8. Include loading and error states if applicable

Please generate:
1. The main component file
2. Props interface definition
3. Basic test file structure
4. Storybook story (if UI component)
`;

// AI-assisted code review checklist
const CODE_REVIEW_CHECKLIST = {
  typescript: [
    'All variables and functions have proper type annotations',
    'No use of `any` type without justification',
    'Interfaces are properly defined and used',
    'Generic types are used appropriately',
    'Type guards are implemented for runtime type checking'
  ],
  performance: [
    'Unnecessary re-renders are prevented',
    'Large objects are not recreated on each render',
    'Expensive computations are memoized',
    'Event handlers are properly memoized',
    'Bundle size impact is considered'
  ],
  security: [
    'User input is properly validated and sanitized',
    'XSS vulnerabilities are prevented',
    'Sensitive data is not logged',
    'API endpoints are properly secured',
    'CSRF protection is implemented where needed'
  ],
  accessibility: [
    'Semantic HTML elements are used',
    'ARIA attributes are properly implemented',
    'Keyboard navigation is supported',
    'Color contrast meets WCAG guidelines',
    'Screen reader compatibility is ensured'
  ]
};
```

### Automated Quality Assurance
```typescript
// AI-powered code analysis
class CodeQualityAnalyzer {
  constructor(private aiClient: AIClient) {}

  public async analyzeCode(filePath: string, code: string): Promise<QualityReport> {
    const prompt = `
    Analyze this TypeScript/JavaScript code for quality issues:

    File: ${filePath}
    Code:
    \`\`\`typescript
    ${code}
    \`\`\`

    Provide analysis for:
    1. Code complexity and maintainability
    2. Type safety and TypeScript usage
    3. Performance considerations
    4. Security vulnerabilities
    5. Best practice adherence
    6. Testing coverage gaps

    Rate each category 1-10 and provide specific improvement suggestions.
    `;

    const analysis = await this.aiClient.analyze(prompt);
    
    return {
      overallScore: analysis.overallScore,
      categories: {
        complexity: analysis.complexity,
        typeSafety: analysis.typeSafety,
        performance: analysis.performance,
        security: analysis.security,
        bestPractices: analysis.bestPractices,
        testability: analysis.testability
      },
      suggestions: analysis.improvements,
      criticalIssues: analysis.criticalIssues
    };
  }
}
```

## Tooling and Configuration

### ESLint Configuration
```json
{
  "extends": [
    "@typescript-eslint/recommended",
    "@typescript-eslint/recommended-requiring-type-checking",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module",
    "project": "./tsconfig.json"
  },
  "plugins": ["@typescript-eslint", "import", "security"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/prefer-const": "error",
    "@typescript-eslint/no-var-requires": "error",
    "import/order": ["error", {
      "groups": [["builtin", "external"], "internal", ["parent", "sibling"]],
      "newlines-between": "always"
    }],
    "security/detect-object-injection": "warn",
    "security/detect-non-literal-regexp": "warn"
  }
}
```

### Prettier Configuration
```json
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "quoteProps": "as-needed",
  "trailingComma": "es5",
  "bracketSpacing": true,
  "bracketSameLine": false,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

### Package.json Scripts
```json
{
  "scripts": {
    "dev": "vite dev",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint src --ext ts,tsx --fix",
    "type-check": "tsc --noEmit",
    "format": "prettier --write src/**/*.{ts,tsx}",
    "format:check": "prettier --check src/**/*.{ts,tsx}",
    "pre-commit": "lint-staged",
    "prepare": "husky install"
  }
}
```

## Documentation Standards

### JSDoc Standards
```typescript
/**
 * Represents a user in the system with comprehensive profile information.
 * 
 * @example
 * ```typescript
 * const user = new User({
 *   email: 'john@example.com',
 *   name: 'John Doe',
 *   role: 'admin'
 * });
 * 
 * await user.save();
 * ```
 */
class User {
  /**
   * Creates a new User instance.
   * 
   * @param userData - The user data for initialization
   * @throws {ValidationError} When user data is invalid
   * @throws {DatabaseError} When database operation fails
   */
  constructor(private userData: UserData) {
    this.validate(userData);
  }

  /**
   * Validates user email asynchronously against external service.
   * 
   * @param email - The email address to validate
   * @param options - Validation options
   * @param options.checkMx - Whether to check MX records
   * @param options.timeout - Timeout in milliseconds
   * @returns Promise resolving to validation result
   * 
   * @example
   * ```typescript
   * const result = await validateEmailAsync('test@example.com', {
   *   checkMx: true,
   *   timeout: 5000
   * });
   * 
   * if (result.isValid) {
   *   console.log('Email is valid');
   * }
   * ```
   * 
   * @since 2.1.0
   */
  public async validateEmailAsync(
    email: string,
    options: { checkMx?: boolean; timeout?: number } = {}
  ): Promise<ValidationResult> {
    // Implementation
  }
}
```

## Continuous Integration and Quality Gates

### Quality Gate Configuration
```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates

on: [push, pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Type checking
        run: npm run type-check
      
      - name: Linting
        run: npm run lint
      
      - name: Format checking
        run: npm run format:check
      
      - name: Unit tests
        run: npm run test:coverage
      
      - name: Security audit
        run: npm audit --audit-level=moderate
      
      - name: Bundle size check
        run: npm run build && npx bundlesize

  ai-code-review:
    needs: quality-check
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3
      - name: AI Code Review
        uses: ./.github/actions/ai-code-review
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Metrics and Monitoring

### Code Quality Metrics
```typescript
interface QualityMetrics {
  // Type safety metrics
  typeScriptCoverage: number;     // Percentage of code with explicit types
  anyTypeUsage: number;           // Count of 'any' type usage
  strictModeCompliance: boolean;  // TSConfig strict mode enabled

  // Code complexity metrics
  cyclomaticComplexity: number;   // Average cyclomatic complexity
  cognitiveComplexity: number;    // Average cognitive complexity
  linesOfCode: number;            // Total lines of code
  
  // Test metrics
  testCoverage: number;           // Test coverage percentage
  testCount: number;              // Total number of tests
  testPassRate: number;           // Percentage of passing tests

  // Performance metrics
  bundleSize: number;             // Bundle size in KB
  renderTime: number;             // Average render time (React)
  memoryUsage: number;            // Memory usage metrics

  // Security metrics
  vulnerabilityCount: number;     // Known vulnerabilities
  securityScore: number;          // Overall security score
  
  // Maintainability metrics
  documentationCoverage: number;  // JSDoc coverage percentage
  codeSmells: number;             // SonarQube code smells
  technicalDebt: string;          // Technical debt ratio
}
```

### Performance Benchmarks
```typescript
// Performance testing standards
describe('Performance Benchmarks', () => {
  it('should render component within performance budget', async () => {
    const startTime = performance.now();
    
    render(<ComplexComponent data={largeDataset} />);
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Performance budget: 16ms (60 FPS)
    expect(renderTime).toBeLessThan(16);
  });

  it('should have acceptable bundle size', () => {
    const bundleSize = getBundleSize();
    
    // Bundle size budget: 250KB gzipped
    expect(bundleSize.gzipped).toBeLessThan(250 * 1024);
  });
});
```

---

*These JavaScript/TypeScript coding standards ensure consistent, maintainable, and high-quality code while leveraging AI-assisted development practices for enhanced productivity and quality assurance.*
---
name: better-auth-integration
description: Production-ready authentication system using Better Auth with latest features. Includes OAuth providers, advanced RBAC, multi-tenant support, and security best practices.
category: authentication
version: 2.0.0
dependencies:
  - better-auth: "^1.3.0"
  - better-auth/adapters: prisma|drizzle|kysely|mongodb
  - better-auth/plugins: organization|oauth|two-factor|passkey
---

# Better Auth Integration Skill

## Purpose

Provides **cutting-edge authentication templates** and **expert integration guidance** using Better Auth. This skill analyzes your project architecture and implements a full-featured authentication system including:
- Email/password and OAuth authentication (Google, Apple, Facebook, X, etc.)
- Advanced OAuth token encryption and account linking
- Multi-factor authentication (2FA) support
- Role-Based Access Control (RBAC) with fine-grained permissions
- Multi-tenant architecture with organizations
- Session management with enhanced security
- Production-ready security configurations
- **🔒 Advanced Security**
  - OAuth token encryption at rest
  - Account linking across providers
  - Advanced rate limiting
  - Session management with auto-renewal
  - CSRF protection
  - IP-based security

- **🐍 FastAPI Integration**
  - Decoupled architecture support
  - JWT token generation for external backends
  - Python middleware templates
  - Stateless authentication flow


## What This Skill Provides

✅ **Automated Implementation Plan**: Analyzes project structure (framework, DB, backend) and provides a tailored integration strategy.
✅ **Latest Better Auth configuration templates**
✅ **Enhanced database schemas** (Prisma, Drizzle, Kysely, MongoDB)
✅ **Modern React/Vue/Svelte authentication clients**
✅ **Middleware for route protection with advanced features**
✅ **Fine-grained RBAC and permission utilities**
✅ **OAuth provider setup with token encryption**
✅ **2FA and passkey authentication templates**
✅ **Advanced security configurations**
✅ **Separate Backend Creation**: For static/SSR-incompatible sites, creates a dedicated Hono + Node.js backend.

## What This Skill Does NOT Provide

❌ Custom business logic implementation (use better-auth-specialist subagent)
❌ Database migration scripts execution (provides the scripts, does not run them)
❌ OAuth credential provisioning (you must provide Client IDs/Secrets)
❌ Production deployment without security review

## When to Use This Skill

Use this skill when:
- Building new applications with modern authentication requirements
- Migrating from older auth systems to Better Auth
- Implementing enterprise-grade security features
- Setting up multi-tenant SaaS applications
- Requiring advanced OAuth features like token encryption
- Needing 2FA or passkey authentication
- User wants personalized onboarding questions after signup
- Project uses Next.js, Remix, Astro, Vite, SvelteKit, Nuxt, or pure React

**How to use:**
```
Load the better-auth-integration skill and use the [template-name] for [framework] with [database-adapter]
OR
Simply ask: "Add Better-Auth to my project" to start the automated integrator flow.
```

## How This Skill Works (Step-by-Step Execution)

1. **Project Analysis Phase**
   - Detect framework (Next.js App Router, Pages Router, Remix, Astro, SvelteKit, etc.)
   - Determine if SSR/SSG/static
   - Check for existing backend (Node/Express, tRPC, Hono, etc.)
   - Detect existing database setup and ORM (Prisma, Drizzle, TypeORM, raw SQL, etc.)

2. **Database Strategy**
   - If a database is already configured → ask for connection string/credentials (only after explicit user confirmation)
   - If no database → ask user preference (PostgreSQL recommended) and guide creation (e.g., Supabase, Neon, Railway, PlanetScale)
   - Only after user says “yes, go ahead”, create required Better-Auth tables/schema automatically

3. **Backend Setup**
   - If project supports SSR/API routes → add Better-Auth directly inside the project
   - If static or incompatible → create separate backend repo/folder using Hono + Node.js/Express (deployable to Vercel, Railway, Fly.io, etc.)
   - Always use Drizzle ORM (Better-Auth’s preferred adapter) with PostgreSQL

4. **Better-Auth Core Implementation**
   - Install `better-auth` + `better-auth-ui` + required plugins (google, apple, facebook, twitter)
   - Configure env variables for all OAuth providers
   - Set up email/password + magic links as fallback
   - Add user metadata table/extension for background questionnaire answers

5. **Onboarding Flow**
   - After first successful sign-up → redirect to `/onboarding`
   - Multi-step form asking:
     - Years of programming experience
     - Primary languages/frameworks
     - Hardware (Mac/Windows/Linux, CPU, GPU, RAM)
     - Development focus (frontend/backend/full-stack/AI/ML/mobile)
   - Store answers in `user_metadata` table for future personalization

6. **UI Integration (Better-Auth-UI)**
   - Create `/sign-in`, `/sign-up` pages with `<AuthUI />`
   - Add header component with dynamic auth buttons:
     - Guest → “Sign In” | “Sign Up”
     - Logged in → Avatar + Dropdown with “Profile”, “Settings”, “Sign Out”
   - Fully responsive, accessible, dark mode ready

7. **Session Management & Protection**
   - Server-side session validation
   - `authClient` React hook for frontend state
   - Protected routes middleware (Next.js middleware or route guards)

## Output You Will Receive

After activation, I will deliver:

- Complete step-by-step implementation plan tailored to your exact project
- Exact terminal commands to run
- File-by-file code changes/additions
- `.env.example` with all required variables
- Database schema (Drizzle migrations)
- Separate backend repo link (if needed)
- Ready-to-copy onboarding questionnaire component
- Header component with conditional auth UI
- Fully working, production-ready authentication system

## Example Usage

**User says:**  
“I have a Next.js 14 App Router site using Prisma + PostgreSQL on Supabase. Add Better-Auth with Google, Apple, Facebook, X login and ask users about their dev experience after signup.”

**This Skill Instantly Activates → Delivers:**

- Confirmed DB usage (no new DB needed)
- Prisma → Drizzle migration plan (or dual-ORM strategy if preferred)
- `/src/auth` folder structure with full Better-Auth config
- All OAuth callbacks configured
- `/app/(auth)/sign-in/[[...better-auth]]/page.tsx` using `<AuthUI />`
- Header with dynamic auth state
- `/app/onboarding/page.tsx` with questionnaire
- Protected route example using middleware

**User says:**  
“My site is a static Astro + React site. Just add login with social providers.”

**This Skill Responds:**  
→ Creates separate `better-auth-backend/` folder (Hono + Node)  
→ Deploys in < 2 minutes to Vercel  
→ Adds minimal client `authClient` to Astro  
→ Injects header buttons + modal sign-in using Better-Auth-UI  
→ Full social login working on a 100% static frontend

## Activate This Skill By Saying

- “Add Better-Auth to my project”
- “Implement signup and login with Google/Apple/Facebook/X”
- “I want Better-Auth with onboarding questions”
- “Set up authentication for my [Next.js/Astro/Remix/etc.] site”

## Available Templates

### Configuration Templates

1. **Production Auth Config** (`config/production-auth-v2.template.ts`)
   - Latest Better Auth features
   - OAuth token encryption enabled
   - Account linking with email validation
   - Advanced security defaults

2. **Enterprise Auth Config** (`config/enterprise-auth.template.ts`)
   - Multi-tenant with organizations
   - Custom roles and permissions
   - 2FA enforcement options
   - Audit logging ready

3. **OAuth-First Config** (`config/oauth-first.template.ts`)
   - OAuth providers as primary auth
   - Account linking across providers
   - Encrypted token storage
   - Social login preferences

4. **B2B SaaS Config** (`config/b2b-saas.template.ts`)
   - Organization-based auth
   - Member invitations
   - Role hierarchy management
   - Team collaboration features

### Database Schema Templates

1. **Prisma Schema** (`schemas/prisma-v2.template.prisma`)
2. **Drizzle Schema** (`schemas/drizzle-v2.template.ts`)
3. **Kysely Schema** (`schemas/kysely-v2.template.ts`)
4. **MongoDB Schema** (`schemas/mongodb.template.ts`)

### Client-Side Templates

1. **React Auth Client** (`client/react-auth-client-v2.template.tsx`)
2. **Vue 3 Auth Client** (`client/vue3-auth-client.template.ts`)
3. **Svelte Auth Client** (`client/svelte-auth-client.template.ts`)
4. **TypeScript Auth Utilities** (`client/auth-utils.template.ts`)

### Component Templates

1. **Modern Sign In Form** (`components/SignInForm-v2.template.tsx`)
2. **Multi-Step Sign Up** (`components/SignUpFlow.template.tsx`)
3. **OAuth Provider Grid** (`components/OAuthProviderGrid.template.tsx`)
4. **2FA Setup Component** (`components/TwoFactorSetup.template.tsx`)
5. **Organization Manager** (`components/OrganizationManager.template.tsx`)
6. **Passkey Enrollment** (`components/PasskeyEnroll.template.tsx`)
7. **Session Security** (`components/SessionSecurity.template.tsx`)

### Middleware Templates

1. **Next.js App Router Middleware** (`middleware/nextjs-app-router.template.ts`)
2. **Advanced RBAC Middleware** (`middleware/rbac-gateway.template.ts`)
3. **Rate Limiting Middleware** (`middleware/rate-limiter.template.ts`)
4. **Audit Logging Middleware** (`middleware/audit-logger.template.ts`)

### Utility Templates

1. **Permission Engine** (`utils/permission-engine.template.ts`)
2. **Role Manager** (`utils/role-manager.template.ts`)
3. **Security Validator** (`utils/security-validator.template.ts`)
4. **OAuth Helper** (`utils/oauth-helper.template.ts`)

## Enhanced Features

### OAuth Token Encryption
- Automatic encryption of OAuth tokens at rest
- Secure token storage with customer-controlled encryption keys
- Token refresh without user intervention

### Account Linking
- Link multiple OAuth providers to single account
- Email verification for provider linking
- Prevent duplicate accounts with same email

### Advanced RBAC
- Hierarchical role system
- Resource-based permissions
- Time-bound role assignments
- Permission inheritance

### Multi-Tenancy
- Organization-based isolation
- Cross-organization roles
- Team-based access control
- Organization invitations

### Security Enhancements
- CSRF protection with custom tokens
- Advanced rate limiting per endpoint
- IP-based session validation
- Device fingerprinting

### 2FA Support
- TOTP (Time-based One-Time Password)
- Backup codes generation
- SMS and email 2FA
- Passkey (WebAuthn) support

---

## Quick Start Templates

### Template 1: Production Auth Configuration

**File**: `.claude/skills/better-auth-integration/config/production-auth-v2.template.ts`

```typescript
/**
 * Better Auth - Production-Ready Configuration
 *
 * Latest Features:
 * - OAuth token encryption
 * - Account linking across providers
 * - Enhanced security defaults
 * - Performance optimizations
 *
 * Setup:
 * 1. Copy to `lib/auth.ts`
 * 2. Configure environment variables
 * 3. Set up database with schema
 * 4. Configure OAuth providers
 */

import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { organization, twoFactor, passkey } from "better-auth/plugins";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export const auth = betterAuth({
  // ===========================================
  // DATABASE CONFIGURATION
  // ===========================================
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),

  // ===========================================
  // SECURITY: SECRET KEY (REQUIRED)
  // ===========================================
  secret: process.env.BETTER_AUTH_SECRET || process.env.AUTH_SECRET!,

  // ===========================================
  // BASE URL CONFIGURATION
  // ===========================================
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",

  // ===========================================
  // EMAIL & PASSWORD AUTHENTICATION
  // ===========================================
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,

    // Enhanced password validation
    passwordValidation: (password) => {
      const checks = {
        length: password.length >= 8 && password.length <= 128,
        upper: /[A-Z]/.test(password),
        lower: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
        noCommon: !password.toLowerCase().includes('password'),
        noUsername: false, // Will be checked against username/email
      };

      if (Object.values(checks).some(check => !check)) {
        return {
          valid: false,
          message: "Password must be 8-128 characters with uppercase, lowercase, number, and special character",
        };
      }

      return { valid: true };
    },

    sendEmailVerificationOnSignUp: true,
  },

  // ===========================================
  // OAUTH PROVIDERS WITH ENCRYPTION
  // ===========================================
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      scope: ["user:email"],
      // Optional: Custom redirect URI
      // redirectURI: "https://yourapp.com/auth/callback/github"
    },

    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      scope: ["openid", "email", "profile"],
    },

    discord: {
      clientId: process.env.DISCORD_CLIENT_ID!,
      clientSecret: process.env.DISCORD_CLIENT_SECRET!,
      scope: ["identify", "email"],
    },

    microsoft: {
      clientId: process.env.MICROSOFT_CLIENT_ID!,
      clientSecret: process.env.MICROSOFT_CLIENT_SECRET!,
      tenant: "common",
      scope: ["openid", "email", "profile"],
    },

    // Additional providers
    /*
    apple: {
      clientId: process.env.APPLE_CLIENT_ID!,
      clientSecret: process.env.APPLE_CLIENT_SECRET!,
    },

    twitter: {
      clientId: process.env.TWITTER_CLIENT_ID!,
      clientSecret: process.env.TWITTER_CLIENT_SECRET!,
    },

    facebook: {
      clientId: process.env.FACEBOOK_CLIENT_ID!,
      clientSecret: process.env.FACEBOOK_CLIENT_SECRET!,
    },
    */
  },

  // ===========================================
  // ACCOUNT MANAGEMENT WITH ENCRYPTION
  // ===========================================
  account: {
    // Model configuration (optional)
    modelName: "accounts",
    fields: {
      userId: "user_id",
    },

    // Encrypt OAuth tokens at rest (SECURITY: Production best practice)
    encryptOAuthTokens: true,

    // Store account in cookie for database-less flows
    storeAccountCookie: false, // Set true only for specific use cases

    // Account linking configuration
    accountLinking: {
      enabled: true,
      // Trusted providers for auto-linking
      trustedProviders: ["google", "github", "microsoft", "apple"],
      // Require same email for linking
      allowDifferentEmails: false,
    },
  },

  // ===========================================
  // ENHANCED SESSION MANAGEMENT
  // ===========================================
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
    // Additional session security
    sessionExpiration: {
      warning: 60 * 60 * 24, // Warn 1 day before expiration
    },
  },

  // ===========================================
  // ADVANCED SECURITY CONFIGURATION
  // ===========================================
  advanced: {
    // CSRF protection (NEVER disable in production)
    disableCSRFCheck: false,

    // Trusted origins
    trustedOrigins: [
      process.env.BETTER_AUTH_URL!,
      ...(process.env.NODE_ENV === "development"
        ? ["http://localhost:3000", "http://localhost:5173", "http://localhost:4173"]
        : []
      ),
    ],

    // Cookie security
    defaultCookieAttributes: {
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      httpOnly: true,
      // Optional: Domain for cross-subdomain cookies
      // domain: ".yourdomain.com",
    },

    // Cross-subdomain cookies
    crossSubDomainCookies: {
      enabled: false, // Enable if using subdomains
      // domain: ".yourdomain.com",
    },
  },

  // ===========================================
  // RATE LIMITING WITH FINE-GRAINED CONTROL
  // ===========================================
  rateLimit: {
    enabled: true,
    window: 60, // 1 minute window
    max: 10, // 10 requests per window

    // Endpoint-specific limits
    customRules: [
      {
        pathPattern: "/api/auth/sign-in",
        window: 60,
        max: 5, // Stricter for sign-in
      },
      {
        pathPattern: "/api/auth/sign-up",
        window: 300, // 5 minutes
        max: 3, // Prevent mass sign-ups
      },
      {
        pathPattern: "/api/auth/reset-password",
        window: 900, // 15 minutes
        max: 3, // Prevent spam
      },
      {
        pathPattern: "/api/auth/verify-email",
        window: 60,
        max: 10, // Allow more attempts for verification
      },
    ],

    // IP-based rate limiting
    ipBasedLimiting: true,

    // Custom storage for rate limits (Redis recommended for production)
    // storage: customRateLimitStorage,
  },

  // ===========================================
  // USER PROFILE CONFIGURATION
  // ===========================================
  user: {
    // Additional user fields
    additionalFields: {
      displayName: {
        type: "string",
        required: false,
      },
      avatar: {
        type: "string",
        required: false,
      },
      bio: {
        type: "string",
        required: false,
      },
      preferences: {
        type: "json",
        required: false,
      },
    },

    // User model configuration
    modelName: "users",
    fields: {
      email: "email_address",
      name: "full_name",
    },
  },

  // ===========================================
  // PLUGINS FOR ENTERPRISE FEATURES
  // ===========================================
  plugins: [
    // Organization plugin for multi-tenancy
    organization({
      enabled: true,
      organizationLimit: 5, // Max organizations per user
      allowUserToCreateOrganization: true,

      // Role definitions
      roles: [
        {
          role: "owner",
          permissions: ["*"], // Full access
        },
        {
          role: "admin",
          permissions: [
            "org:*",
            "member:*",
            "billing:*",
          ],
        },
        {
          role: "member",
          permissions: [
            "org:read",
            "content:*",
          ],
        },
      ],

      // Custom application roles
      customRoles: [
        {
          role: "moderator",
          label: "Content Moderator",
          permissions: [
            "content:moderate",
            "content:delete:any",
            "user:warn",
          ],
        },
        {
          role: "analyst",
          label: "Data Analyst",
          permissions: [
            "analytics:*",
            "reports:*",
            "data:read",
          ],
        },
      ],
    }),

    // Two-factor authentication
    twoFactor({
      // Require 2FA for specific roles
      requireTwoFactorFor: ["admin", "owner"],

      // 2FA configuration
      issuer: process.env.APP_NAME || "MyApp",

      // Backup codes
      backupCodes: {
        enabled: true,
        count: 10,
      },

      // 2FA methods
      methods: ["totp", "sms", "email"],
    }),

    // Passkey (WebAuthn) support
    passkey({
      enabled: true,
      // Passkey configuration
      rpName: process.env.APP_NAME || "MyApp",
      rpID: process.env.PASSKEY_RP_ID || "localhost",
      origin: process.env.PASSKEY_ORIGIN || "http://localhost:3000",
    }),
  ],

  // ===========================================
  // EMAIL SERVICE CONFIGURATION
  // ===========================================
  emailProvider: {
    type: "smtp",
    config: {
      host: process.env.SMTP_HOST!,
      port: parseInt(process.env.SMTP_PORT || "587"),
      secure: process.env.SMTP_SECURE === "true",
      auth: {
        user: process.env.SMTP_USER!,
        pass: process.env.SMTP_PASSWORD!,
      },
    },
    from: {
      name: process.env.EMAIL_FROM_NAME || "MyApp Team",
      email: process.env.EMAIL_FROM_ADDRESS || "noreply@myapp.com",
    },

    // Email templates (optional)
    templates: {
      "email-verification": {
        subject: "Verify your email",
        text: (data) => `Click here to verify: ${data.url}`,
        html: (data) => `<a href="${data.url}">Verify Email</a>`,
      },
      "password-reset": {
        subject: "Reset your password",
        text: (data) => `Click here to reset: ${data.url}`,
        html: (data) => `<a href="${data.url}">Reset Password</a>`,
      },
    },
  },

  // ===========================================
  // WEBHOOKS (Optional)
  // ===========================================
  webhooks: {
    // User events
    onUserCreated: async (user) => {
      console.log("User created:", user.id);
      // Trigger welcome email, analytics, etc.
    },

    onUserDeleted: async (user) => {
      console.log("User deleted:", user.id);
      // Cleanup user data, revoke access tokens, etc.
    },

    // Session events
    onSignIn: async (session) => {
      console.log("User signed in:", session.userId);
      // Track login analytics
    },

    onSignOut: async (session) => {
      console.log("User signed out:", session.userId);
      // Cleanup session-specific data
    },

    // Organization events
    onOrganizationCreated: async (org) => {
      console.log("Organization created:", org.id);
      // Initialize organization settings
    },
  },

  // ===========================================
  // CUSTOM HANDLERS (Optional)
  // ===========================================
  /*
  onRequest: (request) => {
    // Custom request handling
    console.log("Auth request:", request.url);
  },

  onResponse: (response) => {
    // Custom response handling
    console.log("Auth response:", response.status);
  },

  onError: (error, context) => {
    // Custom error handling
    console.error("Auth error:", error, context);
    // Send to monitoring service
  },
  */
});

// ===========================================
// TYPE EXPORTS FOR TYPE SAFETY
// ===========================================
export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.User;
export type Organization = typeof auth.$Infer.Organization;
```

### Template 2: React Auth Client

**File**: `.claude/skills/better-auth-integration/client/react-auth-client-v2.template.tsx`

```typescript
/**
 * React Auth Client with Enhanced Features
 *
 * Features:
 * - TypeScript integration
 * - Organization management
 * - 2FA support
 * - Passkey authentication
 * - Automatic session refresh
 * - Error boundaries
 *
 * Setup:
 * 1. Copy to `lib/auth-client.ts`
 * 2. Configure environment variables
 * 3. Use hooks in components
 */

import React, { createContext, useContext, useEffect, useState } from "react";
import { createAuthClient } from "better-auth/react";
import {
  organizationClient,
  twoFactorClient,
  passkeyClient
} from "better-auth/client";

// ===========================================
// AUTH CLIENT CONFIGURATION
// ===========================================
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000",

  // Fetch options
  fetchOptions: {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  },

  // Enable client plugins
  plugins: [
    organizationClient({
      organizationInvitationPage: "/invite",
    }),
    twoFactorClient({
      twoFactorPage: "/2fa",
    }),
    passkeyClient(),
  ],

  // Storage configuration
  storage: {
    // Use localStorage for persistence
    mode: "localStorage",
  },

  // Session configuration
  session: {
    // Auto-refresh session
    autoRefresh: true,
    // Refresh threshold (5 minutes before expiry)
    refreshThreshold: 5 * 60,
  },
});

// ===========================================
// EXPORT AUTH METHODS
// ===========================================
export const {
  // Authentication
  useSession,
  signIn,
  signUp,
  signOut,

  // User management
  useUser,
  updateUser,

  // Password management
  forgetPassword,
  resetPassword,
  changePassword,

  // Email verification
  sendVerificationEmail,
  verifyEmail,

  // Organizations
  useActiveOrganization,
  useOrganizations,
  createOrganization,
  updateOrganization,
  deleteOrganization,
  inviteMember,
  removeMember,
  updateMemberRole,

  // 2FA
  enableTwoFactor,
  disableTwoFactor,
  verifyTwoFactor,
  generateBackupCodes,

  // Passkeys
  createPasskey,
  deletePasskey,
  usePasskeys,

  // OAuth
  listConnectedAccounts,
  unlinkAccount,
} = authClient;

// ===========================================
// REACT CONTEXT PROVIDER
// ===========================================
interface AuthContextType {
  session: Session | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  signIn: typeof signIn;
  signUp: typeof signUp;
  signOut: typeof signOut;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: session, isPending, error } = useSession();
  const [refreshing, setRefreshing] = useState(false);

  // Session refresh handler
  const refresh = React.useCallback(async () => {
    if (refreshing) return;

    setRefreshing(true);
    try {
      await authClient.getSession({
        fetchOptions: {
          headers: { "Cache-Control": "no-cache" },
        },
      });
    } catch (err) {
      console.error("Failed to refresh session:", err);
    } finally {
      setRefreshing(false);
    }
  }, [refreshing]);

  // Auto-refresh on visibility change
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && session) {
        refresh();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [session, refresh]);

  // Periodic session refresh
  useEffect(() => {
    if (!session) return;

    const interval = setInterval(refresh, 5 * 60 * 1000); // 5 minutes
    return () => clearInterval(interval);
  }, [session, refresh]);

  const contextValue: AuthContextType = {
    session,
    user: session?.user || null,
    isLoading: isPending || refreshing,
    error: error?.message || null,

    signIn,
    signUp,
    signOut,
    refresh,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// ===========================================
// CUSTOM HOOKS
// ===========================================

/**
 * Use auth context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

/**
 * Check if user is authenticated
 */
export function useIsAuthenticated() {
  const { session, isLoading } = useAuth();
  return { isAuthenticated: !!session, isLoading };
}

/**
 * Require authentication (with redirect)
 */
export function useRequireAuth(redirectTo: string = "/signin") {
  const { isAuthenticated, isLoading } = useIsAuthenticated();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, router, redirectTo]);

  return { isAuthenticated, isLoading };
}

/**
 * Check user permissions
 */
export function usePermissions(permissions: string | string[]) {
  const { session } = useAuth();
  const [userPermissions, setUserPermissions] = useState<string[]>([]);

  useEffect(() => {
    if (!session?.user) {
      setUserPermissions([]);
      return;
    }

    // Get user permissions based on role
    const getPermissions = async () => {
      try {
        const response = await fetch("/api/auth/permissions", {
          credentials: "include",
        });
        const data = await response.json();
        setUserPermissions(data.permissions || []);
      } catch (err) {
        console.error("Failed to fetch permissions:", err);
        setUserPermissions([]);
      }
    };

    getPermissions();
  }, [session]);

  const requiredPermissions = Array.isArray(permissions) ? permissions : [permissions];
  const hasPermissions = requiredPermissions.every(p =>
    userPermissions.includes(p) || userPermissions.includes("*")
  );

  return { hasPermissions, permissions: userPermissions };
}

/**
 * Require specific permissions
 */
export function useRequirePermissions(
  permissions: string | string[],
  redirectTo: string = "/unauthorized"
) {
  const { hasPermissions, isLoading } = usePermissions(permissions);
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !hasPermissions) {
      router.push(redirectTo);
    }
  }, [hasPermissions, isLoading, router, redirectTo]);

  return { hasPermissions, isLoading };
}

/**
 * Organization management
 */
export function useOrganization(orgId?: string) {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchOrganization = async () => {
      try {
        const [orgData, membersData] = await Promise.all([
          fetch(`/api/organizations/${orgId || "current"}`, {
            credentials: "include",
          }),
          fetch(`/api/organizations/${orgId || "current"}/members`, {
            credentials: "include",
          }),
        ]);

        const org = await orgData.json();
        const memberList = await membersData.json();

        setOrganization(org);
        setMembers(memberList);
      } catch (err) {
        console.error("Failed to fetch organization:", err);
      } finally {
        setIsLoading(false);
      }
    };

    if (orgId || organization) {
      fetchOrganization();
    }
  }, [orgId, organization]);

  return { organization, members, isLoading };
}

/**
 * 2FA status
 */
export function useTwoFactor() {
  const [isEnabled, setIsEnabled] = useState(false);
  const [isVerified, setIsVerified] = useState(false);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);

  useEffect(() => {
    const fetch2FAStatus = async () => {
      try {
        const response = await fetch("/api/auth/2fa/status", {
          credentials: "include",
        });
        const data = await response.json();

        setIsEnabled(data.enabled);
        setIsVerified(data.verified);
      } catch (err) {
        console.error("Failed to fetch 2FA status:", err);
      }
    };

    fetch2FAStatus();
  }, []);

  const enable = async () => {
    const result = await enableTwoFactor();
    if (result.data) {
      setIsEnabled(true);
      if (result.data.backupCodes) {
        setBackupCodes(result.data.backupCodes);
      }
    }
    return result;
  };

  const disable = async () => {
    const result = await disableTwoFactor();
    if (result.data) {
      setIsEnabled(false);
      setIsVerified(false);
      setBackupCodes([]);
    }
    return result;
  };

  return {
    isEnabled,
    isVerified,
    backupCodes,
    enable,
    disable,
    generateBackupCodes,
  };
}

/**
 * Passkey management
 */
export function usePasskeyAuth() {
  const { data: passkeys, isLoading } = usePasskeys();
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // Check if WebAuthn is supported
    setIsSupported(!!window.PublicKeyCredential);
  }, []);

  const addPasskey = async (name: string) => {
    return await createPasskey({
      name,
      options: {
        authenticatorSelection: {
          userVerification: "required",
          residentKey: "preferred",
        },
      },
    });
  };

  const removePasskey = async (passkeyId: string) => {
    return await deletePasskey(passkeyId);
  };

  return {
    passkeys: passkeys || [],
    isLoading,
    isSupported,
    addPasskey,
    removePasskey,
  };
}

// ===========================================
// UTILITY FUNCTIONS
// ===========================================

/**
 * Format user display name
 */
export function formatUserName(user: User): string {
  if (user.name) return user.name;
  if (user.displayName) return user.displayName;
  return user.email.split("@")[0];
}

/**
 * Get user initials
 */
export function getUserInitials(user: User): string {
  const name = formatUserName(user);
  return name
    .split(" ")
    .map(word => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

/**
 * Validate session activity
 */
export function isSessionActive(session: Session | null): boolean {
  if (!session) return false;

  const now = new Date();
  const expires = new Date(session.expiresAt);

  // Check if session expires within 5 minutes
  const fiveMinutesFromNow = new Date(now.getTime() + 5 * 60 * 1000);
  return expires > fiveMinutesFromNow;
}

// ===========================================
// TYPE EXPORTS
// ===========================================
export type Session = Awaited<ReturnType<typeof useSession>>["data"];
export type User = NonNullable<Session>["user"];
export type Organization = Awaited<ReturnType<typeof useOrganizations>>["data"]?.[0];
export type Member = Awaited<ReturnType<typeof removeMember>>["data"];
```

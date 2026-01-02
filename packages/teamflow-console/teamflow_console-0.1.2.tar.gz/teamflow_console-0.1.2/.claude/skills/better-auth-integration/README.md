# Better Auth Integration

A comprehensive authentication system for modern applications using Better Auth with the latest features including OAuth token encryption, 2FA support, and multi-tenancy.

## 🚀 Features

- **🔐 Complete Authentication**
  - Email/password authentication with enhanced security
  - OAuth providers (GitHub, Google, Discord, Microsoft, Apple)
  - Passkey (WebAuthn) support
  - Two-factor authentication (TOTP, SMS, Email)
  - Magic link authentication

- **🏢 Multi-Tenancy**
  - Organization-based isolation
  - Role-based access control (RBAC)
  - Team collaboration features
  - Member invitations

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

- **🎯 Developer Experience**
  - TypeScript support
  - React hooks and components
  - Built-in form components
  - Permission engine
  - Middleware for route protection
  - Database adapters (Prisma, Drizzle, Kysely, MongoDB)

## 📋 Quick Start

### 1. Installation

```bash
# Install Better Auth and dependencies
npm install better-auth@latest

# Install adapters based on your database
npm install @better-auth/prisma-adapter
# or
npm install @better-auth/drizzle-adapter
# or
npm install @better-auth/kysely-adapter
# or
npm install @better-auth/mongodb-adapter

# Install client libraries
npm install better-auth/react
```

### 2. Set Up Database

Choose your database adapter and copy the appropriate schema:

- **Prisma**: Copy `.claude/skills/better-auth-integration/schemas/prisma-v2.template.prisma`
- **Drizzle**: Copy `.claude/skills/better-auth-integration/schemas/drizzle-v2.template.ts`
- **Kysely**: Copy `.claude/skills/better-auth-integration/schemas/kysely-v2.template.ts`
- **MongoDB**: Copy `.claude/skills/better-auth-integration/schemas/mongodb.template.ts`

Run migrations for your chosen database.

### 3. Configure Authentication

Copy `.claude/skills/better-auth-integration/config/production-auth-v2.template.ts` to `lib/auth.ts` and configure:

```typescript
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { prisma } from "./prisma";

export const auth = betterAuth({
  database: prismaAdapter(prisma, { provider: "postgresql" }),
  secret: process.env.BETTER_AUTH_SECRET!,
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
  },
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
  // ... more configuration
});
```

### 4. Set Up Environment Variables

Create `.env.local`:

```env
# Core Auth
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000

# Database
DATABASE_URL=your-database-url

# OAuth Providers
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email (optional)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password
```

### 5. Set Up API Routes

Create `app/api/auth/[...all]/route.ts`:

```typescript
import { auth } from "@/lib/auth";

export const { GET, POST } = auth.handler;
```

### 6. Set Up Client

Copy `.claude/skills/better-auth-integration/client/react-auth-client-v2.template.tsx` to `lib/auth-client.ts`.

Wrap your app with `AuthProvider` in `app/layout.tsx`:

```tsx
import { AuthProvider } from "@/lib/auth-client";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
```

### 7. Add Authentication Components

Copy components from `.claude/skills/better-auth-integration/components/` to your components folder:

```tsx
import { SignInForm } from "@/components/SignInForm-v2";

export default function SignInPage() {
  return <SignInForm redirectTo="/dashboard" />;
}
```


### 8. FastAPI Backend Integration

For projects using a Python FastAPI backend separate from the Next.js frontend, use the JWT integration pattern.

1.  **Read the Guide**: `.claude/skills/better-auth-integration/FASTAPI_INTEGRATION.md`
2.  **Configure Frontend**: Use `config/jwt-auth.template.ts`
3.  **Configure Backend**: Copy `.claude/skills/better-auth-integration/templates/fastapi/security.template.py` to your FastAPI project (e.g., `app/core/security.py`).
4.  **Protect Routes**:

```python
from fastapi import APIRouter, Depends
from app.core.security import get_current_user, User

router = APIRouter()

@router.get("/my-tasks")
def get_tasks(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "tasks": []}
```

## 📁 Project Structure

```
.claude/skills/better-auth-integration/
├── SKILL.md                  # Skill documentation
├── README.md                  # This file
├── config/                    # Authentication configurations
│   └── production-auth-v2.template.ts
├── schemas/                   # Database schemas
│   ├── prisma-v2.template.prisma
│   ├── drizzle-v2.template.ts
│   ├── kysely-v2.template.ts
│   └── mongodb.template.ts
├── client/                    # Client-side utilities
│   └── react-auth-client-v2.template.tsx
├── components/                # React components
│   ├── SignInForm-v2.template.tsx
│   ├── TwoFactorSetup.template.tsx
│   └── ... (more components)
├── middleware/                # Server middleware
│   └── nextjs-app-router.template.ts
├── utils/                     # Utility functions
│   └── permission-engine.template.ts
└── templates/                 # Additional templates
```

## 🔧 Available Templates

### Configuration Templates
- **Production Auth Config**: Full-featured auth with all security options
- **Enterprise Auth Config**: Multi-tenant with advanced RBAC
- **OAuth-First Config**: Social login focused
- **B2B SaaS Config**: Organization-first auth

### Database Schemas
- **Prisma**: Full schema with relations and indexes
- **Drizzle**: Type-safe SQL schema
- **Kysely**: Query builder schema
- **MongoDB**: NoSQL schema with Mongoose

### Client Templates
- **React Auth Client**: Hooks and context provider
- **Vue 3 Auth Client**: Composition API integration
- **Svelte Auth Client**: Svelte store-based auth

### Component Templates
- **Sign In Form**: Modern login with OAuth
- **Sign Up Flow**: Multi-step registration
- **2FA Setup**: TOTP configuration
- **Organization Manager**: Team management UI
- **Passkey Enrollment**: WebAuthn setup

### Middleware Templates
- **Next.js App Router**: Route protection
- **RBAC Gateway**: Role-based access
- **Rate Limiter**: API protection
- **Audit Logger**: Security tracking

### Utility Templates
- **Permission Engine**: Advanced RBAC
- **Role Manager**: Role hierarchy
- **Security Validator**: Input validation
- **OAuth Helper**: Provider utilities

## 🎨 Using Components

### Sign In Form

```tsx
import { SignInForm } from "@/components/SignInForm-v2";

<SignInForm
  redirectTo="/dashboard"
  showSocialProviders={true}
  showPasskeyOption={true}
/>
```

### Two-Factor Authentication Setup

```tsx
import { TwoFactorSetup } from "@/components/TwoFactorSetup";

<TwoFactorSetup
  onSuccess={() => console.log("2FA enabled")}
  onCancel={() => console.log("Cancelled")}
/>
```

### Organization Management

```tsx
import { OrganizationManager } from "@/components/OrganizationManager";

<OrganizationManager
  organizationId="org-123"
  onMemberInvite={(email) => console.log("Invited:", email)}
/>
```

## 🔐 Permission System

Use the permission engine for fine-grained access control:

```typescript
import { can, require } from "@/lib/permission-engine";

// Check permission
if (await can(userId, "content:delete", { resourceId: "post-123" })) {
  // User can delete the post
}

// Require permission (throws if not allowed)
await require(userId, "billing:update");

// Resource-based check
if (await canAccessResource(userId, "organization", "update", "org-123")) {
  // User can update organization
}
```

## 🛡️ Security Best Practices

1. **Environment Variables**
   - Never commit secrets to version control
   - Use different secrets for dev/staging/prod
   - Rotate secrets regularly

2. **OAuth Configuration**
   - Enable token encryption for production
   - Configure proper callback URLs
   - Use minimal scopes

3. **Session Management**
   - Set appropriate expiration times
   - Enable secure cookies in production
   - Configure proper same-site settings

4. **Rate Limiting**
   - Implement endpoint-specific limits
   - Use Redis for distributed rate limiting
   - Monitor for abuse patterns

5. **2FA Enforcement**
   - Require 2FA for sensitive roles
   - Provide backup codes
   - Support multiple 2FA methods

## 🔧 Advanced Configuration

### Custom OAuth Provider

```typescript
import { genericOAuth } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    genericOAuth({
      config: [
        {
          providerId: "custom-sso",
          clientId: process.env.SSO_CLIENT_ID!,
          clientSecret: process.env.SSO_CLIENT_SECRET!,
          authorizationUrl: "https://sso.example.com/authorize",
          tokenUrl: "https://sso.example.com/token",
          userInfoUrl: "https://sso.example.com/user",
          scope: ["openid", "profile", "email"],
        },
      ],
    }),
  ],
});
```

### Custom Permission Rules

```typescript
import { permissionEngine } from "@/lib/permission-engine";

// Add custom permission with conditions
permissionEngine.addPermission({
  id: "content:publish",
  name: "Publish content",
  conditions: [
    {
      type: "time",
      operator: "between",
      value: {
        start: "09:00",
        end: "17:00",
      },
    },
  ],
});
```

### Custom Webhooks

```typescript
export const auth = betterAuth({
  webhooks: {
    onUserCreated: async (user) => {
      // Send welcome email
      // Track analytics
      // Provision resources
    },
    onSignIn: async (session) => {
      // Update last login
      // Check for suspicious activity
    },
  },
});
```

## 🐛 Troubleshooting

### Common Issues

1. **Session Not Persisting**
   - Check cookie configuration
   - Verify CORS settings
   - Ensure same-site attributes

2. **OAuth Callbacks Failing**
   - Verify callback URLs match
   - Check client credentials
   - Ensure HTTPS in production

3. **2FA Not Working**
   - Verify server time sync
   - Check TOTP secret storage
   - Test with multiple authenticator apps

4. **Database Connection Issues**
   - Verify connection string
   - Check database permissions
   - Ensure schema exists

### Debug Mode

Enable debug logging:

```typescript
export const auth = betterAuth({
  // ... other config
  advanced: {
    // Enable debug mode (development only)
    disableCSRFCheck: process.env.NODE_ENV === "development",
  },
});
```

## 📚 Additional Resources

- [Better Auth Documentation](https://better-auth.com/docs)
- [OAuth Provider Setup Guides](https://better-auth.com/docs/providers)
- [Security Best Practices](https://better-auth.com/docs/security)
- [Migration Guide](https://better-auth.com/docs/migration)

## 🤝 Contributing

This skill is maintained with ❤️ by the community. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This skill is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you need help:

1. Check the [documentation](https://better-auth.com/docs)
2. Search existing [issues](https://github.com/better-auth/better-auth/issues)
3. Create a new issue with details
4. Join our [Discord community](https://discord.gg/better-auth)

---

Built with [Better Auth](https://better-auth.com) - The most comprehensive auth library for TypeScript.

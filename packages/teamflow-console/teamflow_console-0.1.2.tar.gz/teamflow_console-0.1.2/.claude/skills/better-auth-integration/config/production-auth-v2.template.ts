/**
 * Better Auth v2 - Production-Ready Configuration
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
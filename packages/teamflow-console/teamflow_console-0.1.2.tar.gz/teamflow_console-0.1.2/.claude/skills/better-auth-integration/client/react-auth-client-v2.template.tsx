/**
 * React Auth Client v2 with Enhanced Features
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
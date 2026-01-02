/**
 * Better Auth v2 - Kysely Database Schema
 *
 * Features:
 * - OAuth token encryption fields
 * - Account linking support
 * - Organization multi-tenancy
 * - 2FA and passkey support
 * - Enhanced security fields
 *
 * Setup:
 * 1. Copy to your schema file
 * 2. Run migration to create tables
 * 3. Use with Kysely for type-safe queries
 */

import { ColumnType, Generated, Insertable, Selectable, Updateable } from 'kysely';

// ===========================================
// TABLE INTERFACES
// ===========================================

export interface Database {
  users: UsersTable;
  accounts: AccountsTable;
  sessions: SessionsTable;
  verificationTokens: VerificationTokensTable;
  passkeys: PasskeysTable;
  organizations: OrganizationsTable;
  organizationMembers: OrganizationMembersTable;
  invitations: InvitationsTable;
  auditLogs: AuditLogsTable;
  apiKeys: ApiKeysTable;
  oauthConsent: OAuthConsentTable;
}

// ===========================================
// USERS TABLE
// ===========================================
export interface UsersTable {
  id: Generated<string>;
  email: string;
  emailVerified: boolean;
  name: string | null;
  image: string | null;

  // Enhanced profile
  displayName: string | null;
  bio: string | null;
  avatar: string | null;
  preferences: unknown | null; // JSON

  // RBAC
  role: string;

  // Security
  lastLoginAt: Date | null;
  loginAttempts: number;
  lockedUntil: Date | null;

  // 2FA
  twoFactorEnabled: boolean;
  twoFactorSecret: string | null;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export type User = Selectable<UsersTable>;
export type NewUser = Insertable<UsersTable>;
export type UserUpdate = Updateable<UsersTable>;

// ===========================================
// ACCOUNTS TABLE
// ===========================================
export interface AccountsTable {
  id: Generated<string>;
  userId: string;

  // Account type
  type: string;
  provider: string;
  providerAccountId: string;

  // OAuth tokens (encrypted)
  refreshToken: string | null;
  accessToken: string | null;
  expiresAt: number | null;
  tokenType: string | null;
  scope: string | null;
  idToken: string | null;
  sessionState: string | null;
  refreshTokenExpiresAt: number | null;

  // Account linking
  email: string | null;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export type Account = Selectable<AccountsTable>;
export type NewAccount = Insertable<AccountsTable>;
export type AccountUpdate = Updateable<AccountsTable>;

// ===========================================
// SESSIONS TABLE
// ===========================================
export interface SessionsTable {
  id: Generated<string>;
  sessionToken: string;
  userId: string;
  expires: Date;

  // Security metadata
  ipAddress: string | null;
  userAgent: string | null;
  deviceFingerprint: string | null;

  // Session type
  type: string | null;

  // 2FA
  twoFactorVerified: boolean;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
  lastActiveAt: Date;
}

export type Session = Selectable<SessionsTable>;
export type NewSession = Insertable<SessionsTable>;
export type SessionUpdate = Updateable<SessionsTable>;

// ===========================================
// VERIFICATION TOKENS TABLE
// ===========================================
export interface VerificationTokensTable {
  identifier: string;
  token: string;
  expires: Date;
  type: string | null; // "email_verification" | "password_reset" | "2fa" | "magic_link"
  metadata: unknown | null; // JSON
  createdAt: Date;
}

export type VerificationToken = Selectable<VerificationTokensTable>;
export type NewVerificationToken = Insertable<VerificationTokensTable>;

// ===========================================
// PASSKEYS TABLE
// ===========================================
export interface PasskeysTable {
  id: Generated<string>;
  userId: string;

  // Passkey data
  credentialId: string;
  publicKey: string;
  counter: string; // BigInt as string

  // Metadata
  name: string | null;
  deviceType: string | null;
  transports: string[] | null;
  backupEligible: boolean;
  backupState: boolean;

  // Timestamps
  createdAt: Date;
  lastUsedAt: Date | null;
}

export type Passkey = Selectable<PasskeysTable>;
export type NewPasskey = Insertable<PasskeysTable>;
export type PasskeyUpdate = Updateable<PasskeysTable>;

// ===========================================
// ORGANIZATIONS TABLE
// ===========================================
export interface OrganizationsTable {
  id: Generated<string>;
  name: string;
  slug: string;
  description: string | null;
  logo: string | null;
  domain: string | null;
  settings: unknown | null; // JSON

  // Subscription
  plan: string;
  planExpires: Date | null;

  // Owner
  ownerId: string;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export type Organization = Selectable<OrganizationsTable>;
export type NewOrganization = Insertable<OrganizationsTable>;
export type OrganizationUpdate = Updateable<OrganizationsTable>;

// ===========================================
// ORGANIZATION MEMBERS TABLE
// ===========================================
export interface OrganizationMembersTable {
  id: Generated<string>;
  organizationId: string;
  userId: string;

  // Role and status
  role: string;
  status: string | null;

  // Custom permissions
  permissions: string[] | null;

  // Metadata
  invitedBy: string | null;
  joinedAt: Date;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export type OrganizationMember = Selectable<OrganizationMembersTable>;
export type NewOrganizationMember = Insertable<OrganizationMembersTable>;
export type OrganizationMemberUpdate = Updateable<OrganizationMembersTable>;

// ===========================================
// INVITATIONS TABLE
// ===========================================
export interface InvitationsTable {
  id: Generated<string>;
  organizationId: string;
  email: string;
  role: string;

  // Invitation details
  token: string;
  invitedBy: string | null;

  // Status
  status: string | null;
  acceptedBy: string | null;

  // Timing
  expiresAt: Date;
  acceptedAt: Date | null;

  // Metadata
  message: string | null;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export type Invitation = Selectable<InvitationsTable>;
export type NewInvitation = Insertable<InvitationsTable>;
export type InvitationUpdate = Updateable<InvitationsTable>;

// ===========================================
// AUDIT LOGS TABLE
// ===========================================
export interface AuditLogsTable {
  id: Generated<string>;

  // Actor
  userId: string | null;
  organizationId: string | null;

  // Action
  action: string;
  resourceType: string | null;
  resourceId: string | null;

  // Request metadata
  ipAddress: string | null;
  userAgent: string | null;
  requestId: string | null;

  // Data
  metadata: unknown | null; // JSON
  oldValues: unknown | null; // JSON
  newValues: unknown | null; // JSON

  // Status
  status: string | null;
  errorMessage: string | null;

  // Timestamp
  createdAt: Date;
}

export type AuditLog = Selectable<AuditLogsTable>;
export type NewAuditLog = Insertable<AuditLogsTable>;

// ===========================================
// API KEYS TABLE (Optional)
// ===========================================
export interface ApiKeysTable {
  id: Generated<string>;
  userId: string;
  name: string;

  // Key details
  keyHash: string;
  keyPrefix: string;

  // Permissions
  permissions: string[] | null;

  // Rate limiting
  rateLimit: number | null;

  // Status
  isActive: boolean;
  lastUsedAt: Date | null;

  // Expiration
  expiresAt: Date | null;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export type ApiKey = Selectable<ApiKeysTable>;
export type NewApiKey = Insertable<ApiKeysTable>;
export type ApiKeyUpdate = Updateable<ApiKeysTable>;

// ===========================================
// OAUTH CONSENT TABLE (Optional)
// ===========================================
export interface OAuthConsentTable {
  id: Generated<string>;
  userId: string;
  clientId: string;

  // Granted scopes
  scopes: string[];

  // Status
  active: boolean;

  // Timing
  createdAt: Date;
  expiresAt: Date | null;
  revokedAt: Date | null;

  // Metadata
  metadata: unknown | null; // JSON
}

export type OAuthConsent = Selectable<OAuthConsentTable>;
export type NewOAuthConsent = Insertable<OAuthConsentTable>;
export type OAuthConsentUpdate = Updateable<OAuthConsentTable>;

// ===========================================
// SQL MIGRATION TEMPLATE
// ===========================================
export const migrationSQL = `
-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),
  email TEXT NOT NULL UNIQUE,
  email_verified BOOLEAN DEFAULT false NOT NULL,
  name TEXT,
  image TEXT,

  -- Enhanced profile
  display_name TEXT,
  bio TEXT,
  avatar TEXT,
  preferences JSONB,

  -- RBAC
  role TEXT DEFAULT 'user' NOT NULL,

  -- Security
  last_login_at TIMESTAMP,
  login_attempts INTEGER DEFAULT 0 NOT NULL,
  locked_until TIMESTAMP,

  -- 2FA
  two_factor_enabled BOOLEAN DEFAULT false NOT NULL,
  two_factor_secret TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  deleted_at TIMESTAMP
);

-- Create accounts table
CREATE TABLE IF NOT EXISTS accounts (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- Account type
  type TEXT NOT NULL,
  provider TEXT NOT NULL,
  provider_account_id TEXT NOT NULL,

  -- OAuth tokens (encrypted)
  refresh_token TEXT,
  access_token TEXT,
  expires_at INTEGER,
  token_type TEXT,
  scope TEXT,
  id_token TEXT,
  session_state TEXT,
  refresh_token_expires_at INTEGER,

  -- Account linking
  email TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

  -- Constraints
  UNIQUE(provider, provider_account_id),
  UNIQUE(user_id, provider)
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),
  session_token TEXT NOT NULL UNIQUE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires TIMESTAMP NOT NULL,

  -- Security metadata
  ip_address TEXT,
  user_agent TEXT,
  device_fingerprint TEXT,

  -- Session type
  type TEXT DEFAULT 'web',

  -- 2FA
  two_factor_verified BOOLEAN DEFAULT false NOT NULL,

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create verification_tokens table
CREATE TABLE IF NOT EXISTS verification_tokens (
  identifier TEXT NOT NULL,
  token TEXT NOT NULL UNIQUE,
  expires TIMESTAMP NOT NULL,
  type TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

  -- Constraint
  UNIQUE(identifier, token)
);

-- Create passkeys table
CREATE TABLE IF NOT EXISTS passkeys (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- Passkey data
  credential_id TEXT NOT NULL UNIQUE,
  public_key TEXT NOT NULL,
  counter TEXT NOT NULL, -- BigInt

  -- Metadata
  name TEXT,
  device_type TEXT,
  transports TEXT[],
  backup_eligible BOOLEAN DEFAULT false NOT NULL,
  backup_state BOOLEAN DEFAULT false NOT NULL,

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  last_used_at TIMESTAMP
);

-- Create organizations table
CREATE TABLE IF NOT EXISTS organizations (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  description TEXT,
  logo TEXT,
  domain TEXT,
  settings JSONB,

  -- Subscription
  plan TEXT DEFAULT 'free' NOT NULL,
  plan_expires TIMESTAMP,

  -- Owner
  owner_id TEXT NOT NULL REFERENCES users(id),

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create organization_members table
CREATE TABLE IF NOT EXISTS organization_members (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),
  organization_id TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- Role and status
  role TEXT DEFAULT 'member' NOT NULL,
  status TEXT DEFAULT 'active',

  -- Custom permissions
  permissions TEXT[],

  -- Metadata
  invited_by TEXT REFERENCES users(id),
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

  -- Constraint
  UNIQUE(organization_id, user_id)
);

-- Create invitations table
CREATE TABLE IF NOT EXISTS invitations (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),
  organization_id TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  role TEXT DEFAULT 'member' NOT NULL,

  -- Invitation details
  token TEXT NOT NULL UNIQUE,
  invited_by TEXT REFERENCES users(id),

  -- Status
  status TEXT DEFAULT 'pending',
  accepted_by TEXT REFERENCES users(id),

  -- Timing
  expires_at TIMESTAMP NOT NULL,
  accepted_at TIMESTAMP,

  -- Metadata
  message TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),

  -- Actor
  user_id TEXT REFERENCES users(id),
  organization_id TEXT REFERENCES organizations(id),

  -- Action
  action TEXT NOT NULL,
  resource_type TEXT,
  resource_id TEXT,

  -- Request metadata
  ip_address TEXT,
  user_agent TEXT,
  request_id TEXT,

  -- Data
  metadata JSONB,
  old_values JSONB,
  new_values JSONB,

  -- Status
  status TEXT DEFAULT 'success',
  error_message TEXT,

  -- Timestamp
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create api_keys table (Optional)
CREATE TABLE IF NOT EXISTS api_keys (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,

  -- Key details
  key_hash TEXT NOT NULL UNIQUE,
  key_prefix TEXT NOT NULL,

  -- Permissions
  permissions TEXT[],

  -- Rate limiting
  rate_limit INTEGER,

  -- Status
  is_active BOOLEAN DEFAULT true NOT NULL,
  last_used_at TIMESTAMP,

  -- Expiration
  expires_at TIMESTAMP,

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create oauth_consent table (Optional)
CREATE TABLE IF NOT EXISTS oauth_consent (
  id TEXT PRIMARY KEY DEFAULT generate_object_id(),
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  client_id TEXT NOT NULL,

  -- Granted scopes
  scopes TEXT[] NOT NULL,

  -- Status
  active BOOLEAN DEFAULT true NOT NULL,

  -- Timing
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  expires_at TIMESTAMP,
  revoked_at TIMESTAMP,

  -- Metadata
  metadata JSONB,

  -- Constraint
  UNIQUE(user_id, client_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_last_login_at ON users(last_login_at);

CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_email ON accounts(email);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires);
CREATE INDEX IF NOT EXISTS idx_sessions_session_token ON sessions(session_token);

CREATE INDEX IF NOT EXISTS idx_verification_tokens_expires ON verification_tokens(expires);

CREATE INDEX IF NOT EXISTS idx_passkeys_user_id ON passkeys(user_id);
CREATE INDEX IF NOT EXISTS idx_passkeys_credential_id ON passkeys(credential_id);

CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_organizations_owner_id ON organizations(owner_id);

CREATE INDEX IF NOT EXISTS idx_organization_members_user_id ON organization_members(user_id);
CREATE INDEX IF NOT EXISTS idx_organization_members_org_id ON organization_members(organization_id);
CREATE INDEX IF NOT EXISTS idx_organization_members_role ON organization_members(role);

CREATE INDEX IF NOT EXISTS idx_invitations_email ON invitations(email);
CREATE INDEX IF NOT EXISTS idx_invitations_token ON invitations(token);
CREATE INDEX IF NOT EXISTS idx_invitations_org_id ON invitations(organization_id);
CREATE INDEX IF NOT EXISTS idx_invitations_expires_at ON invitations(expires_at);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org_id ON audit_logs(organization_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_status ON audit_logs(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_prefix ON api_keys(key_prefix);

CREATE INDEX IF NOT EXISTS idx_oauth_consent_client_id ON oauth_consent(client_id);
`;
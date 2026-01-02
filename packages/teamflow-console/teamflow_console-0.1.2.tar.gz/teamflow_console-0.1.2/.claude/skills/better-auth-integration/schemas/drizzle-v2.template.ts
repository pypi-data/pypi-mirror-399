/**
 * Better Auth v2 - Drizzle Database Schema
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
 * 2. Run: drizzle-kit generate
 * 3. Run: drizzle-kit migrate
 */

import {
  pgTable,
  text,
  timestamp,
  boolean,
  integer,
  bigint,
  jsonb,
  unique,
  index,
} from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

// ===========================================
// USERS TABLE
// ===========================================
export const users = pgTable("users", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),

  // Core authentication
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified").default(false).notNull(),
  name: text("name"),
  image: text("image"),

  // Enhanced profile
  displayName: text("display_name"),
  bio: text("bio"),
  avatar: text("avatar"),
  preferences: jsonb("preferences"),

  // RBAC
  role: text("role").default("user").notNull(),

  // Security
  lastLoginAt: timestamp("last_login_at"),
  loginAttempts: integer("login_attempts").default(0).notNull(),
  lockedUntil: timestamp("locked_until"),

  // 2FA
  twoFactorEnabled: boolean("two_factor_enabled").default(false).notNull(),
  twoFactorSecret: text("two_factor_secret"),

  // Timestamps
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
  deletedAt: timestamp("deleted_at"),
}, (table) => ({
  emailIdx: index("users_email_idx").on(table.email),
  roleIdx: index("users_role_idx").on(table.role),
  createdAtIdx: index("users_created_at_idx").on(table.createdAt),
  lastLoginAtIdx: index("users_last_login_at_idx").on(table.lastLoginAt),
}));

// ===========================================
// ACCOUNTS TABLE
// ===========================================
export const accounts = pgTable("accounts", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  userId: text("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),

  // Account type
  type: text("type").notNull(),
  provider: text("provider").notNull(),
  providerAccountId: text("provider_account_id").notNull(),

  // OAuth tokens (encrypted)
  refreshToken: text("refresh_token"),
  accessToken: text("access_token"),
  expiresAt: integer("expires_at"),
  tokenType: text("token_type"),
  scope: text("scope"),
  idToken: text("id_token"),
  sessionState: text("session_state"),
  refreshTokenExpiresAt: integer("refresh_token_expires_at"),

  // Account linking
  email: text("email"),

  // Timestamps
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
}, (table) => ({
  providerAccountIdx: unique("accounts_provider_account_id_idx").on(table.provider, table.providerAccountId),
  userProviderIdx: unique("accounts_user_provider_idx").on(table.userId, table.provider),
  userIdIdx: index("accounts_user_id_idx").on(table.userId),
  emailIdx: index("accounts_email_idx").on(table.email),
}));

// ===========================================
// SESSIONS TABLE
// ===========================================
export const sessions = pgTable("sessions", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  sessionToken: text("session_token").notNull().unique(),
  userId: text("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  expires: timestamp("expires").notNull(),

  // Security metadata
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  deviceFingerprint: text("device_fingerprint"),

  // Session type
  type: text("type").default("web"),

  // 2FA
  twoFactorVerified: boolean("two_factor_verified").default(false).notNull(),

  // Timestamps
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
  lastActiveAt: timestamp("last_active_at").defaultNow().notNull(),
}, (table) => ({
  userIdIdx: index("sessions_user_id_idx").on(table.userId),
  expiresIdx: index("sessions_expires_idx").on(table.expires),
  sessionTokenIdx: index("sessions_session_token_idx").on(table.sessionToken),
}));

// ===========================================
// VERIFICATION TOKENS TABLE
// ===========================================
export const verificationTokens = pgTable("verification_tokens", {
  identifier: text("identifier").notNull(),
  token: text("token").notNull().unique(),
  expires: timestamp("expires").notNull(),
  type: text("type"), // "email_verification" | "password_reset" | "2fa" | "magic_link"
  metadata: jsonb("metadata"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
}, (table) => ({
  identifierTokenIdx: unique("verification_tokens_identifier_token_idx").on(table.identifier, table.token),
  expiresIdx: index("verification_tokens_expires_idx").on(table.expires),
}));

// ===========================================
// PASSKEYS TABLE
// ===========================================
export const passkeys = pgTable("passkeys", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  userId: text("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),

  // Passkey data
  credentialId: text("credential_id").notNull().unique(),
  publicKey: text("public_key").notNull(),
  counter: bigint("counter", { mode: "bigint" }).notNull(),

  // Metadata
  name: text("name"),
  deviceType: text("device_type"),
  transports: text("transports").array(),
  backupEligible: boolean("backup_eligible").default(false).notNull(),
  backupState: boolean("backup_state").default(false).notNull(),

  // Timestamps
  createdAt: timestamp("created_at").defaultNow().notNull(),
  lastUsedAt: timestamp("last_used_at"),
}, (table) => ({
  userIdIdx: index("passkeys_user_id_idx").on(table.userId),
  credentialIdIdx: index("passkeys_credential_id_idx").on(table.credentialId),
}));

// ===========================================
// ORGANIZATIONS TABLE
// ===========================================
export const organizations = pgTable("organizations", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  name: text("name").notNull(),
  slug: text("slug").notNull().unique(),
  description: text("description"),
  logo: text("logo"),
  domain: text("domain"),
  settings: jsonb("settings"),

  // Subscription
  plan: text("plan").default("free").notNull(),
  planExpires: timestamp("plan_expires"),

  // Owner
  ownerId: text("owner_id").notNull().references(() => users.id),

  // Timestamps
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
}, (table) => ({
  slugIdx: index("organizations_slug_idx").on(table.slug),
  ownerIdIdx: index("organizations_owner_id_idx").on(table.ownerId),
}));

// ===========================================
// ORGANIZATION MEMBERS TABLE
// ===========================================
export const organizationMembers = pgTable("organization_members", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  organizationId: text("organization_id").notNull().references(() => organizations.id, { onDelete: "cascade" }),
  userId: text("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),

  // Role and status
  role: text("role").default("member").notNull(),
  status: text("status").default("active").notNull(),

  // Custom permissions
  permissions: text("permissions").array(),

  // Metadata
  invitedBy: text("invited_by").references(() => users.id),
  joinedAt: timestamp("joined_at").defaultNow().notNull(),

  // Timestamps
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
}, (table) => ({
  orgUserIdx: unique("organization_members_org_user_idx").on(table.organizationId, table.userId),
  userIdIdx: index("organization_members_user_id_idx").on(table.userId),
  orgIdIdx: index("organization_members_org_id_idx").on(table.organizationId),
  roleIdx: index("organization_members_role_idx").on(table.role),
}));

// ===========================================
// INVITATIONS TABLE
// ===========================================
export const invitations = pgTable("invitations", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  organizationId: text("organization_id").notNull().references(() => organizations.id, { onDelete: "cascade" }),
  email: text("email").notNull(),
  role: text("role").default("member").notNull(),

  // Invitation details
  token: text("token").notNull().unique(),
  invitedBy: text("invited_by").references(() => users.id),

  // Status
  status: text("status").default("pending").notNull(),
  acceptedBy: text("accepted_by").references(() => users.id),

  // Timing
  expiresAt: timestamp("expires_at").notNull(),
  acceptedAt: timestamp("accepted_at"),

  // Metadata
  message: text("message"),

  // Timestamps
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
}, (table) => ({
  emailIdx: index("invitations_email_idx").on(table.email),
  tokenIdx: index("invitations_token_idx").on(table.token),
  orgIdIdx: index("invitations_org_id_idx").on(table.organizationId),
  expiresAtIdx: index("invitations_expires_at_idx").on(table.expiresAt),
}));

// ===========================================
// AUDIT LOGS TABLE
// ===========================================
export const auditLogs = pgTable("audit_logs", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),

  // Actor
  userId: text("user_id").references(() => users.id),
  organizationId: text("organization_id").references(() => organizations.id),

  // Action
  action: text("action").notNull(),
  resourceType: text("resource_type"),
  resourceId: text("resource_id"),

  // Request metadata
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  requestId: text("request_id"),

  // Data
  metadata: jsonb("metadata"),
  oldValues: jsonb("old_values"),
  newValues: jsonb("new_values"),

  // Status
  status: text("status").default("success").notNull(),
  errorMessage: text("error_message"),

  // Timestamp
  createdAt: timestamp("created_at").defaultNow().notNull(),
}, (table) => ({
  userIdIdx: index("audit_logs_user_id_idx").on(table.userId),
  orgIdIdx: index("audit_logs_org_id_idx").on(table.organizationId),
  actionIdx: index("audit_logs_action_idx").on(table.action),
  resourceTypeIdx: index("audit_logs_resource_type_idx").on(table.resourceType),
  statusIdx: index("audit_logs_status_idx").on(table.status),
  createdAtIdx: index("audit_logs_created_at_idx").on(table.createdAt),
}));

// ===========================================
// API KEYS TABLE (Optional)
// ===========================================
export const apiKeys = pgTable("api_keys", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  userId: text("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  name: text("name").notNull(),

  // Key details
  keyHash: text("key_hash").notNull().unique(),
  keyPrefix: text("key_prefix").notNull(),

  // Permissions
  permissions: text("permissions").array(),

  // Rate limiting
  rateLimit: integer("rate_limit"),

  // Status
  isActive: boolean("is_active").default(true).notNull(),
  lastUsedAt: timestamp("last_used_at"),

  // Expiration
  expiresAt: timestamp("expires_at"),

  // Timestamps
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
}, (table) => ({
  userIdIdx: index("api_keys_user_id_idx").on(table.userId),
  keyHashIdx: index("api_keys_key_hash_idx").on(table.keyHash),
  keyPrefixIdx: index("api_keys_key_prefix_idx").on(table.keyPrefix),
}));

// ===========================================
// OAUTH CONSENT TABLE (Optional)
// ===========================================
export const oauthConsent = pgTable("oauth_consent", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  userId: text("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  clientId: text("client_id").notNull(),

  // Granted scopes
  scopes: text("scopes").array().notNull(),

  // Status
  active: boolean("active").default(true).notNull(),

  // Timing
  createdAt: timestamp("created_at").defaultNow().notNull(),
  expiresAt: timestamp("expires_at"),
  revokedAt: timestamp("revoked_at"),

  // Metadata
  metadata: jsonb("metadata"),
}, (table) => ({
  userClientIdx: unique("oauth_consent_user_client_idx").on(table.userId, table.clientId),
  clientIdIdx: index("oauth_consent_client_id_idx").on(table.clientId),
}));

// ===========================================
// RELATIONS
// ===========================================
export const usersRelations = relations(users, ({ many }) => ({
  accounts: many(accounts),
  sessions: many(sessions),
  organizationMembers: many(organizationMembers),
  passkeys: many(passkeys),
  auditLogs: many(auditLogs),
  apiKeys: many(apiKeys),
  oauthConsent: many(oauthConsent),
  invitedOrganizations: many(organizations, { relationName: "owner" }),
  sentInvitations: many(invitations, { relationName: "inviter" }),
}));

export const accountsRelations = relations(accounts, ({ one }) => ({
  user: one(users, {
    fields: [accounts.userId],
    references: [users.id],
  }),
}));

export const sessionsRelations = relations(sessions, ({ one }) => ({
  user: one(users, {
    fields: [sessions.userId],
    references: [users.id],
  }),
}));

export const passkeysRelations = relations(passkeys, ({ one }) => ({
  user: one(users, {
    fields: [passkeys.userId],
    references: [users.id],
  }),
}));

export const organizationsRelations = relations(organizations, ({ one, many }) => ({
  members: many(organizationMembers),
  invitations: many(invitations),
  owner: one(users, {
    fields: [organizations.ownerId],
    references: [users.id],
    relationName: "owner",
  }),
}));

export const organizationMembersRelations = relations(organizationMembers, ({ one }) => ({
  user: one(users, {
    fields: [organizationMembers.userId],
    references: [users.id],
  }),
  organization: one(organizations, {
    fields: [organizationMembers.organizationId],
    references: [organizations.id],
  }),
  inviter: one(users, {
    fields: [organizationMembers.invitedBy],
    references: [users.id],
  }),
}));

export const invitationsRelations = relations(invitations, ({ one }) => ({
  organization: one(organizations, {
    fields: [invitations.organizationId],
    references: [organizations.id],
  }),
  inviter: one(users, {
    fields: [invitations.invitedBy],
    references: [users.id],
    relationName: "inviter",
  }),
  acceptedByUser: one(users, {
    fields: [invitations.acceptedBy],
    references: [users.id],
  }),
}));

export const auditLogsRelations = relations(auditLogs, ({ one }) => ({
  user: one(users, {
    fields: [auditLogs.userId],
    references: [users.id],
  }),
  organization: one(organizations, {
    fields: [auditLogs.organizationId],
    references: [organizations.id],
  }),
}));

export const apiKeysRelations = relations(apiKeys, ({ one }) => ({
  user: one(users, {
    fields: [apiKeys.userId],
    references: [users.id],
  }),
}));

export const oauthConsentRelations = relations(oauthConsent, ({ one }) => ({
  user: one(users, {
    fields: [oauthConsent.userId],
    references: [users.id],
  }),
}));

// ===========================================
// TYPES
// ===========================================
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type Account = typeof accounts.$inferSelect;
export type NewAccount = typeof accounts.$inferInsert;
export type Session = typeof sessions.$inferSelect;
export type NewSession = typeof sessions.$inferInsert;
export type Passkey = typeof passkeys.$inferSelect;
export type NewPasskey = typeof passkeys.$inferInsert;
export type Organization = typeof organizations.$inferSelect;
export type NewOrganization = typeof organizations.$inferInsert;
export type OrganizationMember = typeof organizationMembers.$inferSelect;
export type NewOrganizationMember = typeof organizationMembers.$inferInsert;
export type Invitation = typeof invitations.$inferSelect;
export type NewInvitation = typeof invitations.$inferInsert;
export type AuditLog = typeof auditLogs.$inferSelect;
export type NewAuditLog = typeof auditLogs.$inferInsert;
export type ApiKey = typeof apiKeys.$inferSelect;
export type NewApiKey = typeof apiKeys.$inferInsert;
export type OAuthConsent = typeof oauthConsent.$inferSelect;
export type NewOAuthConsent = typeof oauthConsent.$inferInsert;
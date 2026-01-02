/**
 * Better Auth v2 - MongoDB Schema
 *
 * Features:
 * - OAuth token encryption fields
 * - Account linking support
 * - Organization multi-tenancy
 * - 2FA and passkey support
 * - Enhanced security fields
 *
 * Setup:
 * 1. Copy to your models file
 * 2. Use with MongoDB adapter for Better Auth
 * 3. Create indexes for performance
 */

import { Schema, model, Document, Types } from 'mongoose';

// ===========================================
// INTERFACES
// ===========================================
export interface IUser extends Document {
  // Core authentication
  email: string;
  emailVerified: boolean;
  name?: string;
  image?: string;

  // Enhanced profile
  displayName?: string;
  bio?: string;
  avatar?: string;
  preferences?: Record<string, any>;

  // RBAC
  role: string;

  // Security
  lastLoginAt?: Date;
  loginAttempts: number;
  lockedUntil?: Date;

  // 2FA
  twoFactorEnabled: boolean;
  twoFactorSecret?: string;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
  deletedAt?: Date;
}

export interface IAccount extends Document {
  userId: Types.ObjectId;

  // Account type
  type: string;
  provider: string;
  providerAccountId: string;

  // OAuth tokens (encrypted)
  refreshToken?: string;
  accessToken?: string;
  expiresAt?: number;
  tokenType?: string;
  scope?: string;
  idToken?: string;
  sessionState?: string;
  refreshTokenExpiresAt?: number;

  // Account linking
  email?: string;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export interface ISession extends Document {
  sessionToken: string;
  userId: Types.ObjectId;
  expires: Date;

  // Security metadata
  ipAddress?: string;
  userAgent?: string;
  deviceFingerprint?: string;

  // Session type
  type?: string;

  // 2FA
  twoFactorVerified: boolean;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
  lastActiveAt: Date;
}

export interface IVerificationToken extends Document {
  identifier: string;
  token: string;
  expires: Date;
  type?: string; // "email_verification" | "password_reset" | "2fa" | "magic_link"
  metadata?: Record<string, any>;
  createdAt: Date;
}

export interface IPasskey extends Document {
  userId: Types.ObjectId;

  // Passkey data
  credentialId: string;
  publicKey: string;
  counter: string; // BigInt as string

  // Metadata
  name?: string;
  deviceType?: string;
  transports?: string[];
  backupEligible: boolean;
  backupState: boolean;

  // Timestamps
  createdAt: Date;
  lastUsedAt?: Date;
}

export interface IOrganization extends Document {
  name: string;
  slug: string;
  description?: string;
  logo?: string;
  domain?: string;
  settings?: Record<string, any>;

  // Subscription
  plan: string;
  planExpires?: Date;

  // Owner
  ownerId: Types.ObjectId;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export interface IOrganizationMember extends Document {
  organizationId: Types.ObjectId;
  userId: Types.ObjectId;

  // Role and status
  role: string;
  status?: string;

  // Custom permissions
  permissions?: string[];

  // Metadata
  invitedBy?: Types.ObjectId;
  joinedAt: Date;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export interface IInvitation extends Document {
  organizationId: Types.ObjectId;
  email: string;
  role: string;

  // Invitation details
  token: string;
  invitedBy?: Types.ObjectId;

  // Status
  status?: string;
  acceptedBy?: Types.ObjectId;

  // Timing
  expiresAt: Date;
  acceptedAt?: Date;

  // Metadata
  message?: string;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export interface IAuditLog extends Document {
  // Actor
  userId?: Types.ObjectId;
  organizationId?: Types.ObjectId;

  // Action
  action: string;
  resourceType?: string;
  resourceId?: string;

  // Request metadata
  ipAddress?: string;
  userAgent?: string;
  requestId?: string;

  // Data
  metadata?: Record<string, any>;
  oldValues?: Record<string, any>;
  newValues?: Record<string, any>;

  // Status
  status?: string;
  errorMessage?: string;

  // Timestamp
  createdAt: Date;
}

export interface IApiKey extends Document {
  userId: Types.ObjectId;
  name: string;

  // Key details
  keyHash: string;
  keyPrefix: string;

  // Permissions
  permissions?: string[];

  // Rate limiting
  rateLimit?: number;

  // Status
  isActive: boolean;
  lastUsedAt?: Date;

  // Expiration
  expiresAt?: Date;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export interface IOAuthConsent extends Document {
  userId: Types.ObjectId;
  clientId: string;

  // Granted scopes
  scopes: string[];

  // Status
  active: boolean;

  // Timing
  createdAt: Date;
  expiresAt?: Date;
  revokedAt?: Date;

  // Metadata
  metadata?: Record<string, any>;
}

// ===========================================
// SCHEMAS
// ===========================================

// User Schema
const UserSchema = new Schema<IUser>({
  // Core authentication
  email: { type: String, required: true, unique: true, lowercase: true, trim: true },
  emailVerified: { type: Boolean, default: false },
  name: { type: String, trim: true },
  image: { type: String },

  // Enhanced profile
  displayName: { type: String, trim: true },
  bio: { type: String },
  avatar: { type: String },
  preferences: { type: Schema.Types.Mixed },

  // RBAC
  role: { type: String, default: 'user', required: true },

  // Security
  lastLoginAt: { type: Date },
  loginAttempts: { type: Number, default: 0 },
  lockedUntil: { type: Date },

  // 2FA
  twoFactorEnabled: { type: Boolean, default: false },
  twoFactorSecret: { type: String },

  // Soft delete
  deletedAt: { type: Date },
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      delete ret.twoFactorSecret;
      delete ret.loginAttempts;
      delete ret.lockedUntil;
      delete ret.deletedAt;
      return ret;
    }
  }
});

// Account Schema
const AccountSchema = new Schema<IAccount>({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },

  // Account type
  type: { type: String, required: true },
  provider: { type: String, required: true },
  providerAccountId: { type: String, required: true },

  // OAuth tokens (encrypted)
  refreshToken: { type: String },
  accessToken: { type: String },
  expiresAt: { type: Number },
  tokenType: { type: String },
  scope: { type: String },
  idToken: { type: String },
  sessionState: { type: String },
  refreshTokenExpiresAt: { type: Number },

  // Account linking
  email: { type: String, lowercase: true, trim: true },
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      // Don't expose tokens in JSON
      delete ret.refreshToken;
      delete ret.accessToken;
      delete ret.idToken;
      return ret;
    }
  }
});

// Session Schema
const SessionSchema = new Schema<ISession>({
  sessionToken: { type: String, required: true, unique: true },
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  expires: { type: Date, required: true },

  // Security metadata
  ipAddress: { type: String },
  userAgent: { type: String },
  deviceFingerprint: { type: String },

  // Session type
  type: { type: String, default: 'web' },

  // 2FA
  twoFactorVerified: { type: Boolean, default: false },
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      // Don't expose session token in JSON
      delete ret.sessionToken;
      return ret;
    }
  }
});

// Verification Token Schema
const VerificationTokenSchema = new Schema<IVerificationToken>({
  identifier: { type: String, required: true },
  token: { type: String, required: true, unique: true },
  expires: { type: Date, required: true },
  type: { type: String }, // "email_verification" | "password_reset" | "2fa" | "magic_link"
  metadata: { type: Schema.Types.Mixed },
  createdAt: { type: Date, default: Date.now }
}, {
  toJSON: {
    transform: function(doc, ret) {
      // Don't expose tokens in JSON
      delete ret.token;
      return ret;
    }
  }
});

// Passkey Schema
const PasskeySchema = new Schema<IPasskey>({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },

  // Passkey data
  credentialId: { type: String, required: true, unique: true },
  publicKey: { type: String, required: true },
  counter: { type: String, required: true },

  // Metadata
  name: { type: String, trim: true },
  deviceType: { type: String },
  transports: [{ type: String }],
  backupEligible: { type: Boolean, default: false },
  backupState: { type: Boolean, default: false },

  // Timestamps
  lastUsedAt: { type: Date },
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      // Don't expose public key in JSON
      delete ret.publicKey;
      return ret;
    }
  }
});

// Organization Schema
const OrganizationSchema = new Schema<IOrganization>({
  name: { type: String, required: true, trim: true },
  slug: { type: String, required: true, unique: true, lowercase: true },
  description: { type: String },
  logo: { type: String },
  domain: { type: String, lowercase: true },
  settings: { type: Schema.Types.Mixed },

  // Subscription
  plan: { type: String, default: 'free', required: true },
  planExpires: { type: Date },

  // Owner
  ownerId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
}, {
  timestamps: true
});

// Organization Member Schema
const OrganizationMemberSchema = new Schema<IOrganizationMember>({
  organizationId: { type: Schema.Types.ObjectId, ref: 'Organization', required: true },
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },

  // Role and status
  role: { type: String, default: 'member', required: true },
  status: { type: String, default: 'active' },

  // Custom permissions
  permissions: [{ type: String }],

  // Metadata
  invitedBy: { type: Schema.Types.ObjectId, ref: 'User' },
  joinedAt: { type: Date, default: Date.now },
}, {
  timestamps: true
});

// Invitation Schema
const InvitationSchema = new Schema<IInvitation>({
  organizationId: { type: Schema.Types.ObjectId, ref: 'Organization', required: true },
  email: { type: String, required: true, lowercase: true, trim: true },
  role: { type: String, default: 'member', required: true },

  // Invitation details
  token: { type: String, required: true, unique: true },
  invitedBy: { type: Schema.Types.ObjectId, ref: 'User' },

  // Status
  status: { type: String, default: 'pending' },
  acceptedBy: { type: Schema.Types.ObjectId, ref: 'User' },

  // Timing
  expiresAt: { type: Date, required: true },
  acceptedAt: { type: Date },

  // Metadata
  message: { type: String },
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      // Don't expose invitation token in JSON
      delete ret.token;
      return ret;
    }
  }
});

// Audit Log Schema
const AuditLogSchema = new Schema<IAuditLog>({
  // Actor
  userId: { type: Schema.Types.ObjectId, ref: 'User' },
  organizationId: { type: Schema.Types.ObjectId, ref: 'Organization' },

  // Action
  action: { type: String, required: true },
  resourceType: { type: String },
  resourceId: { type: String },

  // Request metadata
  ipAddress: { type: String },
  userAgent: { type: String },
  requestId: { type: String },

  // Data
  metadata: { type: Schema.Types.Mixed },
  oldValues: { type: Schema.Types.Mixed },
  newValues: { type: Schema.Types.Mixed },

  // Status
  status: { type: String, default: 'success' },
  errorMessage: { type: String },
}, {
  timestamps: { createdAt: true, updatedAt: false }
});

// API Key Schema
const ApiKeySchema = new Schema<IApiKey>({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  name: { type: String, required: true, trim: true },

  // Key details
  keyHash: { type: String, required: true, unique: true },
  keyPrefix: { type: String, required: true },

  // Permissions
  permissions: [{ type: String }],

  // Rate limiting
  rateLimit: { type: Number },

  // Status
  isActive: { type: Boolean, default: true },
  lastUsedAt: { type: Date },

  // Expiration
  expiresAt: { type: Date },
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      // Don't expose key hash in JSON
      delete ret.keyHash;
      return ret;
    }
  }
});

// OAuth Consent Schema
const OAuthConsentSchema = new Schema<IOAuthConsent>({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  clientId: { type: String, required: true },

  // Granted scopes
  scopes: [{ type: String, required: true }],

  // Status
  active: { type: Boolean, default: true },

  // Timing
  expiresAt: { type: Date },
  revokedAt: { type: Date },

  // Metadata
  metadata: { type: Schema.Types.Mixed },
}, {
  timestamps: true
});

// ===========================================
// INDEXES
// ===========================================

// User indexes
UserSchema.index({ email: 1 });
UserSchema.index({ role: 1 });
UserSchema.index({ createdAt: -1 });
UserSchema.index({ lastLoginAt: -1 });
UserSchema.index({ deletedAt: 1 }); // For soft delete queries

// Account indexes
AccountSchema.index({ userId: 1 });
AccountSchema.index({ provider: 1, providerAccountId: 1 });
AccountSchema.index({ userId: 1, provider: 1 }, { unique: true });
AccountSchema.index({ email: 1 });

// Session indexes
SessionSchema.index({ userId: 1 });
SessionSchema.index({ expires: 1 });
SessionSchema.index({ sessionToken: 1 });
SessionSchema.index({ userId: 1, twoFactorVerified: 1 });

// Verification Token indexes
VerificationTokenSchema.index({ identifier: 1, token: 1 }, { unique: true });
VerificationTokenSchema.index({ expires: 1 });
VerificationTokenSchema.index({ token: 1 });

// Passkey indexes
PasskeySchema.index({ userId: 1 });
PasskeySchema.index({ credentialId: 1 });

// Organization indexes
OrganizationSchema.index({ slug: 1 });
OrganizationSchema.index({ ownerId: 1 });
OrganizationSchema.index({ domain: 1 });

// Organization Member indexes
OrganizationMemberSchema.index({ userId: 1 });
OrganizationMemberSchema.index({ organizationId: 1 });
OrganizationMemberSchema.index({ organizationId: 1, userId: 1 }, { unique: true });
OrganizationMemberSchema.index({ role: 1 });

// Invitation indexes
InvitationSchema.index({ email: 1 });
InvitationSchema.index({ token: 1 });
InvitationSchema.index({ organizationId: 1 });
InvitationSchema.index({ expiresAt: 1 });
InvitationSchema.index({ status: 1 });

// Audit Log indexes
AuditLogSchema.index({ userId: 1 });
AuditLogSchema.index({ organizationId: 1 });
AuditLogSchema.index({ action: 1 });
AuditLogSchema.index({ resourceType: 1 });
AuditLogSchema.index({ status: 1 });
AuditLogSchema.index({ createdAt: -1 });
AuditLogSchema.index({ userId: 1, createdAt: -1 });

// API Key indexes
ApiKeySchema.index({ userId: 1 });
ApiKeySchema.index({ keyHash: 1 });
ApiKeySchema.index({ keyPrefix: 1 });
ApiKeySchema.index({ isActive: 1 });

// OAuth Consent indexes
OAuthConsentSchema.index({ userId: 1, clientId: 1 }, { unique: true });
OAuthConsentSchema.index({ clientId: 1 });
OAuthConsentSchema.index({ active: 1 });

// ===========================================
// MODELS
// ===========================================

export const User = model<IUser>('User', UserSchema);
export const Account = model<IAccount>('Account', AccountSchema);
export const Session = model<ISession>('Session', SessionSchema);
export const VerificationToken = model<IVerificationToken>('VerificationToken', VerificationTokenSchema);
export const Passkey = model<IPasskey>('Passkey', PasskeySchema);
export const Organization = model<IOrganization>('Organization', OrganizationSchema);
export const OrganizationMember = model<IOrganizationMember>('OrganizationMember', OrganizationMemberSchema);
export const Invitation = model<IInvitation>('Invitation', InvitationSchema);
export const AuditLog = model<IAuditLog>('AuditLog', AuditLogSchema);
export const ApiKey = model<IApiKey>('ApiKey', ApiKeySchema);
export const OAuthConsent = model<IOAuthConsent>('OAuthConsent', OAuthConsentSchema);

// ===========================================
// MONGODB ADAPTER CONFIGURATION
// ===========================================

export const mongoDBAdapterConfig = {
  // Model mappings
  collections: {
    users: User.collection.name,
    accounts: Account.collection.name,
    sessions: Session.collection.name,
    verificationTokens: VerificationToken.collection.name,
    passkeys: Passkey.collection.name,
  },

  // Field mappings (if needed)
  fieldMappings: {
    users: {
      id: '_id',
      email: 'email',
      emailVerified: 'emailVerified',
      name: 'name',
      image: 'image',
      role: 'role',
      createdAt: 'createdAt',
      updatedAt: 'updatedAt',
    },
    accounts: {
      id: '_id',
      userId: 'userId',
      type: 'type',
      provider: 'provider',
      providerAccountId: 'providerAccountId',
      refreshToken: 'refreshToken',
      accessToken: 'accessToken',
      expiresAt: 'expiresAt',
      tokenType: 'tokenType',
      scope: 'scope',
      idToken: 'idToken',
      createdAt: 'createdAt',
      updatedAt: 'updatedAt',
    },
    sessions: {
      id: '_id',
      sessionToken: 'sessionToken',
      userId: 'userId',
      expires: 'expires',
      createdAt: 'createdAt',
      updatedAt: 'updatedAt',
    },
    verificationTokens: {
      identifier: 'identifier',
      token: 'token',
      expires: 'expires',
      createdAt: 'createdAt',
    },
    passkeys: {
      id: '_id',
      userId: 'userId',
      credentialId: 'credentialId',
      publicKey: 'publicKey',
      counter: 'counter',
      createdAt: 'createdAt',
    },
  },
};
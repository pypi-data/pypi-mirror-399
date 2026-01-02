/**
 * Permission Engine for Better Auth v2
 *
 * Features:
 * - Hierarchical role-based permissions
 * - Resource-based access control
 * - Time-bound permissions
 * - Permission inheritance
 * - Custom permission rules
 * - Organization-scoped permissions
 *
 * Setup:
 * 1. Copy to `lib/permissions.ts`
 * 2. Use with permission checks in your app
 */

// ===========================================
// TYPES
// ===========================================

export interface Permission {
  id: string;
  name: string;
  description?: string;
  resource?: string;
  action?: string;
  conditions?: PermissionCondition[];
}

export interface PermissionCondition {
  type: "time" | "ip" | "attribute" | "custom";
  operator: "eq" | "ne" | "gt" | "gte" | "lt" | "lte" | "in" | "nin" | "contains";
  value: any;
  attribute?: string;
}

export interface Role {
  id: string;
  name: string;
  permissions: string[];
  inherits?: string[]; // Parent roles for inheritance
  conditions?: PermissionCondition[];
}

export interface UserPermission {
  userId: string;
  permissions: string[];
  roles: string[];
  organizationId?: string;
  expiresAt?: Date;
  metadata?: Record<string, any>;
}

// ===========================================
// DEFAULT PERMISSIONS
// ===========================================

export const DEFAULT_PERMISSIONS: Permission[] = [
  // User management
  { id: "user:read", name: "Read user profile" },
  { id: "user:update", name: "Update own profile" },
  { id: "user:read:any", name: "Read any user profile" },
  { id: "user:update:any", name: "Update any user profile" },
  { id: "user:delete", name: "Delete users" },
  { id: "user:create", name: "Create users" },

  // Organization management
  { id: "org:read", name: "Read organization" },
  { id: "org:update", name: "Update organization" },
  { id: "org:delete", name: "Delete organization" },
  { id: "org:create", name: "Create organization" },

  // Member management
  { id: "member:invite", name: "Invite members" },
  { id: "member:remove", name: "Remove members" },
  { id: "member:update:role", name: "Update member roles" },

  // Content management
  { id: "content:read", name: "Read content" },
  { id: "content:create", name: "Create content" },
  { id: "content:update:own", name: "Update own content" },
  { id: "content:update:any", name: "Update any content" },
  { id: "content:delete:own", name: "Delete own content" },
  { id: "content:delete:any", name: "Delete any content" },
  { id: "content:publish", name: "Publish content" },
  { id: "content:moderate", name: "Moderate content" },

  // Analytics and reports
  { id: "analytics:read", name: "View analytics" },
  { id: "analytics:export", name: "Export analytics" },
  { id: "reports:create", name: "Create reports" },
  { id: "reports:read", name: "Read reports" },

  // Billing and subscriptions
  { id: "billing:read", name: "View billing information" },
  { id: "billing:update", name: "Update billing information" },
  { id: "subscription:manage", name: "Manage subscriptions" },

  // API and integrations
  { id: "api:create", name: "Create API keys" },
  { id: "api:read", name: "Read API keys" },
  { id: "api:update", name: "Update API keys" },
  { id: "api:delete", name: "Delete API keys" },
  { id: "integration:manage", name: "Manage integrations" },

  // Security settings
  { id: "security:read", name: "View security settings" },
  { id: "security:update", name: "Update security settings" },
  { id: "security:audit", name: "View audit logs" },

  // Wildcard permissions
  { id: "*", name: "All permissions" },
  { id: "user:*", name: "All user permissions" },
  { id: "content:*", name: "All content permissions" },
  { id: "org:*", name: "All organization permissions" },
];

// ===========================================
// DEFAULT ROLES
// ===========================================

export const DEFAULT_ROLES: Role[] = [
  {
    id: "owner",
    name: "Owner",
    permissions: ["*"],
    description: "Full access to everything",
  },
  {
    id: "admin",
    name: "Administrator",
    permissions: [
      "user:*",
      "org:*",
      "member:*",
      "billing:*",
      "security:*",
      "analytics:*",
      "api:*",
      "integration:*",
    ],
    inherits: [],
  },
  {
    id: "moderator",
    name: "Moderator",
    permissions: [
      "content:read",
      "content:moderate",
      "content:delete:any",
      "user:read:any",
      "user:warn",
    ],
    inherits: [],
  },
  {
    id: "editor",
    name: "Editor",
    permissions: [
      "content:*",
      "user:read",
      "user:update",
    ],
    inherits: [],
  },
  {
    id: "member",
    name: "Member",
    permissions: [
      "content:read",
      "content:create",
      "content:update:own",
      "content:delete:own",
      "user:read",
      "user:update",
    ],
    inherits: [],
  },
  {
    id: "viewer",
    name: "Viewer",
    permissions: [
      "content:read",
      "user:read",
    ],
    inherits: [],
  },
];

// ===========================================
// PERMISSION ENGINE CLASS
// ===========================================

export class PermissionEngine {
  private permissions: Map<string, Permission> = new Map();
  private roles: Map<string, Role> = new Map();
  private userCache: Map<string, UserPermission> = new Map();
  private cacheTimeout = 5 * 60 * 1000; // 5 minutes

  constructor(
    permissions: Permission[] = DEFAULT_PERMISSIONS,
    roles: Role[] = DEFAULT_ROLES
  ) {
    this.initializeMaps(permissions, roles);
  }

  // ===========================================
  // INITIALIZATION
  // ===========================================
  private initializeMaps(
    permissions: Permission[],
    roles: Role[]
  ): void {
    // Initialize permissions map
    permissions.forEach((permission) => {
      this.permissions.set(permission.id, permission);
    });

    // Initialize roles map with inheritance
    roles.forEach((role) => {
      const resolvedRole = this.resolveRoleInheritance(role);
      this.roles.set(role.id, resolvedRole);
    });
  }

  private resolveRoleInheritance(role: Role): Role {
    if (!role.inherits || role.inherits.length === 0) {
      return role;
    }

    const inheritedPermissions = new Set<string>(role.permissions);
    const visited = new Set<string>();

    const collectInheritedPermissions = (roleId: string) => {
      if (visited.has(roleId)) return;
      visited.add(roleId);

      const parentRole = this.roles.get(roleId);
      if (parentRole) {
        parentRole.permissions.forEach((perm) => {
          inheritedPermissions.add(perm);
        });
        if (parentRole.inherits) {
          parentRole.inherits.forEach(collectInheritedPermissions);
        }
      }
    };

    role.inherits.forEach(collectInheritedPermissions);

    return {
      ...role,
      permissions: Array.from(inheritedPermissions),
    };
  }

  // ===========================================
  // USER PERMISSION MANAGEMENT
  // ===========================================

  /**
   * Get user permissions with caching
   */
  async getUserPermissions(userId: string): Promise<UserPermission> {
    const cached = this.userCache.get(userId);
    if (cached && Date.now() - cached.metadata?.cachedAt < this.cacheTimeout) {
      return cached;
    }

    // In a real app, fetch from database
    const userPermission = await this.fetchUserPermissions(userId);
    userPermission.metadata = {
      ...userPermission.metadata,
      cachedAt: Date.now(),
    };

    this.userCache.set(userId, userPermission);
    return userPermission;
  }

  /**
   * Fetch user permissions from database
   */
  private async fetchUserPermissions(userId: string): Promise<UserPermission> {
    // This would typically fetch from your database
    // For now, return a default structure
    return {
      userId,
      permissions: [],
      roles: ["member"],
    };
  }

  /**
   * Check if user has a specific permission
   */
  async hasPermission(
    userId: string,
    permission: string,
    context?: {
      resourceId?: string;
      organizationId?: string;
      userId?: string;
      [key: string]: any;
    }
  ): Promise<boolean> {
    const userPerm = await this.getUserPermissions(userId);

    // Check cache expiration
    if (userPerm.expiresAt && userPerm.expiresAt < new Date()) {
      return false;
    }

    // Organization-scoped check
    if (context?.organizationId && userPerm.organizationId) {
      if (userPerm.organizationId !== context.organizationId) {
        // Check if user has cross-org permissions
        const hasCrossOrgPermission = userPerm.permissions.includes("org:cross-access");
        if (!hasCrossOrgPermission) {
          return false;
        }
      }
    }

    // Check for wildcard permission
    if (userPerm.permissions.includes("*")) {
      return true;
    }

    // Check for exact permission match
    if (userPerm.permissions.includes(permission)) {
      // Verify additional conditions if any
      return await this.verifyPermissionConditions(
        userId,
        permission,
        context
      );
    }

    // Check for wildcard matches (e.g., "user:*" matches "user:read")
    const userWildcards = userPerm.permissions.filter((p) => p.endsWith("*"));
    for (const wildcard of userWildcards) {
      const prefix = wildcard.slice(0, -1);
      if (permission.startsWith(prefix)) {
        return await this.verifyPermissionConditions(
          userId,
          permission,
          context
        );
      }
    }

    // Check role-based permissions
    for (const roleId of userPerm.roles) {
      const role = this.roles.get(roleId);
      if (role) {
        if (role.permissions.includes("*")) {
          return true;
        }

        if (role.permissions.includes(permission)) {
          return await this.verifyPermissionConditions(
            userId,
            permission,
            context,
            role.conditions
          );
        }

        // Check role wildcards
        const roleWildcards = role.permissions.filter((p) => p.endsWith("*"));
        for (const wildcard of roleWildcards) {
          const prefix = wildcard.slice(0, -1);
          if (permission.startsWith(prefix)) {
            return await this.verifyPermissionConditions(
              userId,
              permission,
              context,
              role.conditions
            );
          }
        }
      }
    }

    return false;
  }

  /**
   * Verify permission conditions
   */
  private async verifyPermissionConditions(
    userId: string,
    permission: string,
    context?: any,
    roleConditions?: PermissionCondition[]
  ): Promise<boolean> {
    const permissionData = this.permissions.get(permission);
    const conditions = [...(permissionData?.conditions || []), ...(roleConditions || [])];

    if (conditions.length === 0) {
      return true;
    }

    for (const condition of conditions) {
      const result = await this.evaluateCondition(condition, context, userId);
      if (!result) {
        return false;
      }
    }

    return true;
  }

  /**
   * Evaluate a single condition
   */
  private async evaluateCondition(
    condition: PermissionCondition,
    context?: any,
    userId?: string
  ): Promise<boolean> {
    switch (condition.type) {
      case "time":
        return this.evaluateTimeCondition(condition);
      case "attribute":
        return this.evaluateAttributeCondition(condition, context);
      case "custom":
        return this.evaluateCustomCondition(condition, context, userId);
      default:
        return true;
    }
  }

  private evaluateTimeCondition(condition: PermissionCondition): boolean {
    const now = new Date();
    const startTime = new Date(condition.value.start);
    const endTime = new Date(condition.value.end);

    return now >= startTime && now <= endTime;
  }

  private evaluateAttributeCondition(
    condition: PermissionCondition,
    context?: any
  ): boolean {
    if (!context || !condition.attribute) {
      return false;
    }

    const attributeValue = context[condition.attribute];

    switch (condition.operator) {
      case "eq":
        return attributeValue === condition.value;
      case "ne":
        return attributeValue !== condition.value;
      case "gt":
        return attributeValue > condition.value;
      case "gte":
        return attributeValue >= condition.value;
      case "lt":
        return attributeValue < condition.value;
      case "lte":
        return attributeValue <= condition.value;
      case "in":
        return condition.value.includes(attributeValue);
      case "nin":
        return !condition.value.includes(attributeValue);
      case "contains":
        return String(attributeValue).includes(condition.value);
      default:
        return false;
    }
  }

  private async evaluateCustomCondition(
    condition: PermissionCondition,
    context?: any,
    userId?: string
  ): Promise<boolean> {
    // Implement custom condition logic here
    // This could call external services or implement complex business rules
    return true;
  }

  // ===========================================
  // ROLE MANAGEMENT
  // ===========================================

  /**
   * Add a new role
   */
  addRole(role: Role): void {
    const resolvedRole = this.resolveRoleInheritance(role);
    this.roles.set(role.id, resolvedRole);
    this.clearUserCache();
  }

  /**
   * Update an existing role
   */
  updateRole(roleId: string, updates: Partial<Role>): void {
    const existing = this.roles.get(roleId);
    if (existing) {
      const updated = { ...existing, ...updates };
      const resolved = this.resolveRoleInheritance(updated);
      this.roles.set(roleId, resolved);
      this.clearUserCache();
    }
  }

  /**
   * Remove a role
   */
  removeRole(roleId: string): void {
    this.roles.delete(roleId);
    this.clearUserCache();
  }

  /**
   * Get all roles
   */
  getRoles(): Role[] {
    return Array.from(this.roles.values());
  }

  /**
   * Get a specific role
   */
  getRole(roleId: string): Role | undefined {
    return this.roles.get(roleId);
  }

  // ===========================================
  // PERMISSION MANAGEMENT
  // ===========================================

  /**
   * Add a new permission
   */
  addPermission(permission: Permission): void {
    this.permissions.set(permission.id, permission);
    this.clearUserCache();
  }

  /**
   * Get all permissions
   */
  getPermissions(): Permission[] {
    return Array.from(this.permissions.values());
  }

  /**
   * Get a specific permission
   */
  getPermission(permissionId: string): Permission | undefined {
    return this.permissions.get(permissionId);
  }

  // ===========================================
  // UTILITY METHODS
  // ===========================================

  /**
   * Clear user permission cache
   */
  clearUserCache(): void {
    this.userCache.clear();
  }

  /**
   * Grant temporary permission to user
   */
  async grantTemporaryPermission(
    userId: string,
    permission: string,
    expiresAt: Date,
    organizationId?: string
  ): Promise<void> {
    // This would update the database
    // For now, just update cache
    const userPerm = await this.getUserPermissions(userId);
    if (!userPerm.permissions.includes(permission)) {
      userPerm.permissions.push(permission);
      userPerm.expiresAt = expiresAt;
      userPerm.organizationId = organizationId;
      this.userCache.set(userId, userPerm);
    }
  }

  /**
   * Revoke permission from user
   */
  async revokePermission(userId: string, permission: string): Promise<void> {
    // This would update the database
    // For now, just update cache
    const userPerm = await this.getUserPermissions(userId);
    userPerm.permissions = userPerm.permissions.filter((p) => p !== permission);
    this.userCache.set(userId, userPerm);
  }

  /**
   * Assign role to user
   */
  async assignRole(userId: string, roleId: string): Promise<void> {
    // This would update the database
    // For now, just update cache
    const userPerm = await this.getUserPermissions(userId);
    if (!userPerm.roles.includes(roleId)) {
      userPerm.roles.push(roleId);
      this.userCache.set(userId, userPerm);
    }
  }

  /**
   * Remove role from user
   */
  async removeRole(userId: string, roleId: string): Promise<void> {
    // This would update the database
    // For now, just update cache
    const userPerm = await this.getUserPermissions(userId);
    userPerm.roles = userPerm.roles.filter((r) => r !== roleId);
    this.userCache.set(userId, userPerm);
  }
}

// ===========================================
// CREATE INSTANCE
// ===========================================

export const permissionEngine = new PermissionEngine();

// ===========================================
// HELPER FUNCTIONS
// ===========================================

/**
 * Check if user has permission (convenience function)
 */
export async function can(
  userId: string,
  permission: string,
  context?: any
): Promise<boolean> {
  return permissionEngine.hasPermission(userId, permission, context);
}

/**
 * Require permission (throws if not allowed)
 */
export async function require(
  userId: string,
  permission: string,
  context?: any
): Promise<void> {
  const hasPermission = await can(userId, permission, context);
  if (!hasPermission) {
    throw new Error(`Permission denied: ${permission}`);
  }
}

/**
 * Get user's effective permissions
 */
export async function getUserEffectivePermissions(userId: string): Promise<string[]> {
  const userPerm = await permissionEngine.getUserPermissions(userId);
  const effectivePermissions = new Set<string>(userPerm.permissions);

  // Add role permissions
  for (const roleId of userPerm.roles) {
    const role = permissionEngine.getRole(roleId);
    if (role) {
      role.permissions.forEach((perm) => {
        effectivePermissions.add(perm);
      });
    }
  }

  return Array.from(effectivePermissions);
}

/**
 * Check if user can access resource
 */
export async function canAccessResource(
  userId: string,
  resourceType: string,
  action: string,
  resourceId?: string,
  organizationId?: string
): Promise<boolean> {
  const permission = resourceType === "*" ? "*" : `${resourceType}:${action}`;

  return can(userId, permission, {
    resourceType,
    action,
    resourceId,
    organizationId,
  });
}
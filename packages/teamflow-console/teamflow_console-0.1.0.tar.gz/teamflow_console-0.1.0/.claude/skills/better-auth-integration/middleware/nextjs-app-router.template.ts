/**
 * Next.js App Router Middleware v2
 *
 * Features:
 * - Authentication protection
 * - Role-based access control (RBAC)
 * - Organization context
 * - 2FA requirement enforcement
 * - Session validation
 * - Custom redirect logic
 * - API route protection
 *
 * Setup:
 * 1. Copy to `middleware.ts` in root
 * 2. Adjust protected routes as needed
 * 3. Configure custom middleware options
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

// ===========================================
// CONFIGURATION
// ===========================================

// Public routes that don't require authentication
const publicRoutes = [
  "/",
  "/signin",
  "/signup",
  "/forgot-password",
  "/reset-password",
  "/api/auth",
  "/api/webhook",
  "/docs",
  "/privacy",
  "/terms",
  "/about",
  "/pricing",
];

// API routes that require special handling
const apiRoutes = [
  "/api/auth",
  "/api/webhook",
  "/api/health",
];

// Routes that require 2FA (in addition to authentication)
const twoFactorRequiredRoutes = [
  "/settings/security",
  "/settings/billing",
  "/admin",
  "/api/keys",
];

// Routes that require specific roles
const roleBasedRoutes = {
  "/admin": ["admin", "owner"],
  "/settings/billing": ["admin", "owner"],
  "/settings/users": ["admin", "owner", "moderator"],
  "/analytics": ["admin", "owner", "analyst"],
};

// Routes that require organization membership
const organizationRoutes = [
  "/dashboard",
  "/projects",
  "/team",
  "/settings/organization",
];

// ===========================================
// MIDDLEWARE HELPER FUNCTIONS
// ===========================================

/**
 * Check if a path is public
 */
function isPublicPath(pathname: string): boolean {
  // Check exact matches
  if (publicRoutes.includes(pathname)) return true;

  // Check if path starts with any public route
  return publicRoutes.some((route) => {
    if (route.endsWith("*")) {
      return pathname.startsWith(route.slice(0, -1));
    }
    return pathname.startsWith(route);
  });
}

/**
 * Check if path is an API route
 */
function isApiPath(pathname: string): boolean {
  return apiRoutes.some((route) => pathname.startsWith(route));
}

/**
 * Get role requirements for a path
 */
function getRequiredRole(pathname: string): string[] | null {
  for (const [route, roles] of Object.entries(roleBasedRoutes)) {
    if (pathname.startsWith(route)) {
      return roles;
    }
  }
  return null;
}

/**
 * Get session and validate it
 */
async function validateSession(request: NextRequest) {
  try {
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session) {
      return { session: null, error: "No session found" };
    }

    // Check if session is expired
    if (session.session.expiresAt < new Date()) {
      return { session: null, error: "Session expired" };
    }

    return { session, error: null };
  } catch (error) {
    console.error("Session validation error:", error);
    return { session: null, error: "Failed to validate session" };
  }
}

/**
 * Check if 2FA is required and verified
 */
function checkTwoFactorRequirement(
  session: any,
  pathname: string
): { required: boolean; verified: boolean } {
  const isRequired = twoFactorRequiredRoutes.some((route) =>
    pathname.startsWith(route)
  );

  if (!isRequired) {
    return { required: false, verified: true };
  }

  const isVerified = session.user.twoFactorVerified || false;
  return { required: true, verified: isVerified };
}

/**
 * Check user role permissions
 */
function checkRolePermissions(
  session: any,
  pathname: string
): { required: boolean; hasPermission: boolean } {
  const requiredRoles = getRequiredRole(pathname);

  if (!requiredRoles) {
    return { required: false, hasPermission: true };
  }

  const userRole = session.user.role;
  const hasPermission = requiredRoles.includes(userRole) || userRole === "owner";

  return { required: true, hasPermission };
}

/**
 * Check organization membership
 */
async function checkOrganizationMembership(
  session: any,
  request: NextRequest
): Promise<{ required: boolean; hasMembership: boolean }> {
  const pathname = request.nextUrl.pathname;
  const isRequired = organizationRoutes.some((route) =>
    pathname.startsWith(route)
  );

  if (!isRequired) {
    return { required: false, hasMembership: true };
  }

  // For simplicity, we'll assume authenticated users have access
  // In a real app, you might check specific organization membership
  return { required: true, hasMembership: true };
}

/**
 * Create redirect response
 */
function createRedirectResponse(
  request: NextRequest,
  destination: string,
  reason: string
): NextResponse {
  const url = request.nextUrl.clone();
  url.pathname = destination;

  // Add query parameter with reason
  url.searchParams.set("redirected", reason);

  // Store original path for redirect after login
  if (!url.searchParams.has("callbackUrl")) {
    url.searchParams.set("callbackUrl", request.nextUrl.pathname);
  }

  const response = NextResponse.redirect(url);

  // Clear cookies if unauthorized
  if (reason === "unauthorized") {
    response.cookies.delete("better-auth.session_token");
  }

  return response;
}

// ===========================================
// MAIN MIDDLEWARE FUNCTION
// ===========================================
export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip middleware for static files and Next.js internals
  if (
    pathname.includes("/_next") ||
    pathname.includes("/_vercel") ||
    pathname.includes("/static") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  // Check if path is public
  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  // Special handling for API routes
  if (isApiPath(pathname)) {
    const { session } = await validateSession(request);

    // Some API routes might be public
    if (
      pathname.startsWith("/api/auth") ||
      pathname.startsWith("/api/webhook") ||
      pathname.startsWith("/api/health")
    ) {
      return NextResponse.next();
    }

    // All other API routes require authentication
    if (!session) {
      return new NextResponse(
        JSON.stringify({ error: "Authentication required" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    // Add user context to request headers
    const response = NextResponse.next();
    response.headers.set("x-user-id", session.user.id);
    response.headers.set("x-user-role", session.user.role);

    return response;
  }

  // Validate session
  const { session, error } = await validateSession(request);

  if (!session) {
    return createRedirectResponse(request, "/signin", "no_session");
  }

  // Check 2FA requirement
  const { required: twoFactorRequired, verified: twoFactorVerified } =
    checkTwoFactorRequirement(session, pathname);

  if (twoFactorRequired && !twoFactorVerified) {
    return createRedirectResponse(request, "/2fa", "2fa_required");
  }

  // Check role permissions
  const { required: roleRequired, hasPermission: rolePermission } =
    checkRolePermissions(session, pathname);

  if (roleRequired && !rolePermission) {
    return createRedirectResponse(request, "/unauthorized", "insufficient_role");
  }

  // Check organization membership
  const { required: orgRequired, hasMembership: orgMembership } =
    await checkOrganizationMembership(session, request);

  if (orgRequired && !orgMembership) {
    return createRedirectResponse(
      request,
      "/no-organization",
      "no_organization"
    );
  }

  // Add security headers
  const response = NextResponse.next();

  // Rate limiting headers
  response.headers.set("X-RateLimit-Limit", "100");
  response.headers.set("X-RateLimit-Remaining", "99");

  // Security headers
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-XSS-Protection", "1; mode=block");
  response.headers.set(
    "Strict-Transport-Security",
    "max-age=31536000; includeSubDomains"
  );

  // Add user context to headers for use in server components
  response.headers.set("x-user-id", session.user.id);
  response.headers.set("x-user-email", session.user.email);
  response.headers.set("x-user-role", session.user.role);

  // Check if user is an admin for admin routes
  if (pathname.startsWith("/admin")) {
    response.headers.set("x-is-admin", "true");
  }

  return response;
}

// ===========================================
// CONFIGURATION EXPORT
// ===========================================
export const config = {
  // Match all paths except for static files and API routes that don't need middleware
  matcher: [
    "/((?!_next|_vercel|static|.*\\..*).*)",
  ],
};
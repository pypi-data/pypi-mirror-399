/**
 * Modern Sign In Form Component v2
 *
 * Features:
 * - Email/password authentication
 * - Social OAuth providers
 * - 2FA support
 * - Passkey authentication
 * - Error handling with user feedback
 * - Loading states
 * - Remember me option
 * - Password visibility toggle
 *
 * Setup:
 *   <SignInForm redirectTo="/dashboard" />
 */

"use client";

import React, { useState, useEffect } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Loader2, AlertCircle } from "lucide-react";

interface SignInFormProps {
  redirectTo?: string;
  showSocialProviders?: boolean;
  socialProviders?: Array<"github" | "google" | "discord" | "microsoft" | "apple">;
  showPasskeyOption?: boolean;
  className?: string;
}

export function SignInForm({
  redirectTo = "/dashboard",
  showSocialProviders = true,
  socialProviders = ["github", "google", "discord", "microsoft"],
  showPasskeyOption = true,
  className = "",
}: SignInFormProps) {
  // Form state
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);

  // UI state
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [twoFactorRequired, setTwoFactorRequired] = useState(false);

  // Passkey state
  const [passkeySupported, setPasskeySupported] = useState(false);

  const router = useRouter();

  // Check passkey support on mount
  useEffect(() => {
    setPasskeySupported(!!window.PublicKeyCredential);
  }, []);

  // ===========================================
  // EMAIL/PASSWORD SIGN IN
  // ===========================================
  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const result = await authClient.signIn.email({
        email,
        password,
        rememberMe,
      }, {
        onSuccess: () => {
          setSuccess("Signing in successfully...");
          setTimeout(() => {
            router.push(redirectTo);
          }, 500);
        },
        onError: (ctx) => {
          // Handle 2FA requirement
          if (ctx.error.code === "TWO_FACTOR_REQUIRED") {
            setTwoFactorRequired(true);
            setError("Please enter your 2FA code");
          } else if (ctx.error.code === "INVALID_CREDENTIALS") {
            setError("Invalid email or password");
          } else if (ctx.error.code === "EMAIL_NOT_VERIFIED") {
            setError("Please verify your email before signing in");
          } else {
            setError(ctx.error.message || "Failed to sign in");
          }
        },
      });
    } catch (err) {
      setError("An unexpected error occurred. Please try again.");
      console.error("Sign in error:", err);
    } finally {
      setLoading(false);
    }
  };

  // ===========================================
  // TWO FACTOR VERIFICATION
  // ===========================================
  const handleTwoFactorSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const code = (e.target as HTMLFormElement).code.value;

    try {
      const result = await authClient.twoFactor.verifyTwoFactor({
        code,
      });

      if (result.error) {
        setError("Invalid 2FA code. Please try again.");
      } else {
        setSuccess("2FA verified successfully");
        setTimeout(() => {
          router.push(redirectTo);
        }, 500);
      }
    } catch (err) {
      setError("Failed to verify 2FA code");
      console.error("2FA error:", err);
    } finally {
      setLoading(false);
    }
  };

  // ===========================================
  // SOCIAL OAUTH SIGN IN
  // ===========================================
  const handleSocialSignIn = async (
    provider: "github" | "google" | "discord" | "microsoft" | "apple"
  ) => {
    try {
      await authClient.signIn.social({
        provider,
        callbackURL: redirectTo,
      });
    } catch (err) {
      setError(`Failed to sign in with ${provider}`);
      console.error(`${provider} sign in error:`, err);
    }
  };

  // ===========================================
  // PASSKEY AUTHENTICATION
  // ===========================================
  const handlePasskeySignIn = async () => {
    if (!passkeySupported) return;

    setLoading(true);
    setError("");

    try {
      const result = await authClient.passkey.signIn();
      if (result.error) {
        setError(result.error.message || "Failed to sign in with passkey");
      } else {
        setSuccess("Signing in with passkey...");
        setTimeout(() => {
          router.push(redirectTo);
        }, 500);
      }
    } catch (err) {
      setError("Failed to use passkey for authentication");
      console.error("Passkey sign in error:", err);
    } finally {
      setLoading(false);
    }
  };

  // ===========================================
  // PROVIDER CONFIGURATION
  // ===========================================
  const providerConfig = {
    github: {
      name: "GitHub",
      icon: "🐙",
      bgColor: "bg-gray-900 hover:bg-gray-800",
    },
    google: {
      name: "Google",
      icon: "🔍",
      bgColor: "bg-blue-600 hover:bg-blue-700",
    },
    discord: {
      name: "Discord",
      icon: "💬",
      bgColor: "bg-indigo-600 hover:bg-indigo-700",
    },
    microsoft: {
      name: "Microsoft",
      icon: "Ⓜ️",
      bgColor: "bg-blue-500 hover:bg-blue-600",
    },
    apple: {
      name: "Apple",
      icon: "🍎",
      bgColor: "bg-gray-800 hover:bg-gray-900",
    },
  };

  // ===========================================
  // RENDER TWO FACTOR FORM
  // ===========================================
  if (twoFactorRequired) {
    return (
      <div className={`w-full max-w-md mx-auto ${className}`}>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-center mb-6">Two-Factor Authentication</h2>

          {success && (
            <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
              {success}
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          <form onSubmit={handleTwoFactorSubmit} className="space-y-4">
            <div>
              <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1">
                Authentication Code
              </label>
              <input
                id="code"
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter 6-digit code"
                required
                autoFocus
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading && <Loader2 className="inline-block w-4 h-4 mr-2 animate-spin" />}
              Verify Code
            </button>
          </form>

          <div className="mt-4 text-center">
            <button
              onClick={() => setTwoFactorRequired(false)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Back to sign in
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ===========================================
  // RENDER MAIN FORM
  // ===========================================
  return (
    <div className={`w-full max-w-md mx-auto ${className}`}>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-center mb-6">Sign In</h2>
        <p className="text-gray-600 text-center mb-6">
          Welcome back! Sign in to your account.
        </p>

        {/* Success Message */}
        {success && (
          <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
            {success}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Passkey Option */}
        {showPasskeyOption && passkeySupported && (
          <button
            onClick={handlePasskeySignIn}
            disabled={loading}
            className="w-full mb-4 bg-gray-900 text-white py-3 px-4 rounded-md hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <span>🔑</span>
            )}
            Sign in with Passkey
          </button>
        )}

        {/* Divider */}
        {showPasskeyOption && passkeySupported && showSocialProviders && (
          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>
        )}

        {/* Social Providers */}
        {showSocialProviders && (
          <div className="grid grid-cols-2 gap-3 mb-6">
            {socialProviders.map((provider) => {
              const config = providerConfig[provider];
              return (
                <button
                  key={provider}
                  onClick={() => handleSocialSignIn(provider)}
                  disabled={loading}
                  className={`${config.bgColor} text-white py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors`}
                >
                  <span className="text-xl">{config.icon}</span>
                  <span className="text-sm font-medium">{config.name}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Email/Password Form */}
        <form onSubmit={handleEmailSignIn} className="space-y-4">
          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              disabled={loading}
              autoComplete="email"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={loading}
                autoComplete="current-password"
                className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
                className="absolute inset-y-0 right-0 px-3 py-2 text-gray-500 hover:text-gray-700 focus:outline-none"
              >
                {showPassword ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* Remember Me */}
          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={loading}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
              />
              <span className="ml-2 text-sm text-gray-600">Remember me</span>
            </label>
            <a
              href="/forgot-password"
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Forgot password?
            </a>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading && <Loader2 className="inline-block w-4 h-4 mr-2 animate-spin" />}
            Sign In
          </button>
        </form>

        {/* Sign Up Link */}
        <p className="mt-6 text-center text-sm text-gray-600">
          Don't have an account?{" "}
          <a
            href="/signup"
            className="font-medium text-blue-600 hover:text-blue-800"
          >
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}
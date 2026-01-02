/**
 * Two-Factor Authentication Setup Component
 *
 * Features:
 * - TOTP (Time-based One-Time Password) setup
 * - Backup codes generation and display
 * - QR code display for easy scanning
 * - Test verification
 * - Enable/disable 2FA
 * - Recovery options
 *
 * Setup:
 *   <TwoFactorSetup onSuccess={() => {}} />
 */

"use client";

import React, { useState, useEffect } from "react";
import { authClient } from "@/lib/auth-client";
import { QRCodeSVG } from "qrcode.react";
import {
  Shield,
  Copy,
  Check,
  AlertCircle,
  Smartphone,
  Key,
  Loader2,
  Eye,
  EyeOff,
} from "lucide-react";

interface TwoFactorSetupProps {
  onSuccess?: () => void;
  onCancel?: () => void;
  className?: string;
}

export function TwoFactorSetup({
  onSuccess,
  onCancel,
  className = "",
}: TwoFactorSetupProps) {
  const [step, setStep] = useState<"check" | "setup" | "verify" | "backup"> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Setup data
  const [secret, setSecret] = useState("");
  const [qrCodeUrl, setQrCodeUrl] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  // Form inputs
  const [verificationCode, setVerificationCode] = useState("");

  useEffect(() => {
    checkCurrentStatus();
  }, []);

  // ===========================================
  // CHECK CURRENT 2FA STATUS
  // ===========================================
  const checkCurrentStatus = async () => {
    try {
      const response = await fetch("/api/auth/2fa/status", {
        credentials: "include",
      });
      const data = await response.json();

      if (data.enabled) {
        setStep("check");
      } else {
        initiateSetup();
      }
    } catch (err) {
      setError("Failed to check 2FA status");
      console.error("2FA status error:", err);
    }
  };

  // ===========================================
  // INITIATE 2FA SETUP
  // ===========================================
  const initiateSetup = async () => {
    setIsLoading(true);
    setError("");

    try {
      const result = await authClient.twoFactor.enableTwoFactor({
        password: prompt("Please enter your password to enable 2FA:") || "",
      });

      if (result.error) {
        setError(result.error.message || "Failed to enable 2FA");
      } else if (result.data) {
        setSecret(result.data.secret || "");
        setQrCodeUrl(result.data.qrCode || "");
        setBackupCodes(result.data.backupCodes || []);
        setStep("setup");
      }
    } catch (err) {
      setError("An unexpected error occurred");
      console.error("2FA setup error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // ===========================================
  // VERIFY TOTP CODE
  // ===========================================
  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const result = await authClient.twoFactor.verifyTwoFactor({
        code: verificationCode,
      });

      if (result.error) {
        setError("Invalid code. Please try again.");
      } else {
        setSuccess("2FA has been successfully enabled!");
        setStep("backup");
        onSuccess?.();
      }
    } catch (err) {
      setError("Failed to verify code");
      console.error("2FA verification error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // ===========================================
  // DISABLE 2FA
  // ===========================================
  const handleDisable2FA = async () => {
    const password = prompt("Please enter your password to disable 2FA:");
    if (!password) return;

    setIsLoading(true);
    setError("");

    try {
      const result = await authClient.twoFactor.disableTwoFactor({
        password,
      });

      if (result.error) {
        setError(result.error.message || "Failed to disable 2FA");
      } else {
        setSuccess("2FA has been disabled");
        setTimeout(() => {
          onSuccess?.();
        }, 1000);
      }
    } catch (err) {
      setError("Failed to disable 2FA");
      console.error("2FA disable error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // ===========================================
  // COPY TO CLIPBOARD
  // ===========================================
  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setSuccess(`${type} copied to clipboard!`);
      setTimeout(() => setSuccess(""), 2000);
    } catch (err) {
      setError("Failed to copy to clipboard");
    }
  };

  // ===========================================
  // DOWNLOAD BACKUP CODES
  // ===========================================
  const downloadBackupCodes = () => {
    const content = `Your 2FA Backup Codes\nKeep these codes in a safe place. Each code can only be used once.\n\n${backupCodes.join(
      "\n"
    )}`;

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "2fa-backup-codes.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // ===========================================
  // RENDER CHECK STATUS
  // ===========================================
  if (step === "check") {
    return (
      <div className={`max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg ${className}`}>
        <div className="text-center">
          <Shield className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">2FA is Enabled</h2>
          <p className="text-gray-600 mb-6">
            Your account is protected with two-factor authentication.
          </p>

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

          <button
            onClick={handleDisable2FA}
            disabled={isLoading}
            className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 mb-3"
          >
            {isLoading && <Loader2 className="inline-block w-4 h-4 mr-2 animate-spin" />}
            Disable 2FA
          </button>

          {onCancel && (
            <button
              onClick={onCancel}
              className="w-full bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Close
            </button>
          )}
        </div>
      </div>
    );
  }

  // ===========================================
  // RENDER SETUP STEP
  // ===========================================
  if (step === "setup") {
    return (
      <div className={`max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg ${className}`}>
        <h2 className="text-2xl font-bold mb-4">Set Up Two-Factor Authentication</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        <div className="space-y-6">
          {/* Step 1: QR Code */}
          <div>
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <Smartphone className="w-5 h-5" />
              Step 1: Scan QR Code
            </h3>
            <p className="text-sm text-gray-600 mb-3">
              Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
            </p>
            {qrCodeUrl && (
              <div className="flex justify-center p-4 bg-gray-50 rounded">
                <QRCodeSVG value={qrCodeUrl} size={200} />
              </div>
            )}
          </div>

          {/* Step 2: Manual Entry */}
          <div>
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <Key className="w-5 h-5" />
              Step 2: Manual Entry
            </h3>
            <p className="text-sm text-gray-600 mb-3">
              Or enter this code manually in your authenticator app:
            </p>
            <div className="relative">
              <input
                type="text"
                value={secret}
                readOnly
                className="w-full px-3 py-2 pr-10 bg-gray-50 border border-gray-300 rounded font-mono text-sm"
              />
              <button
                onClick={() => copyToClipboard(secret, "Secret key")}
                className="absolute inset-y-0 right-0 px-3 py-2 text-gray-500 hover:text-gray-700"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Step 3: Verify */}
          <div>
            <h3 className="font-semibold mb-2">Step 3: Verify Code</h3>
            <p className="text-sm text-gray-600 mb-3">
              Enter the 6-digit code from your authenticator app:
            </p>
            <form onSubmit={handleVerifyCode}>
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={6}
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="000000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-center text-xl tracking-widest"
                required
              />
              <button
                type="submit"
                disabled={isLoading || verificationCode.length !== 6}
                className="w-full mt-3 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading && <Loader2 className="inline-block w-4 h-4 mr-2 animate-spin" />}
                Verify & Enable 2FA
              </button>
            </form>
          </div>
        </div>

        {onCancel && (
          <button
            onClick={onCancel}
            className="w-full mt-4 bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancel
          </button>
        )}
      </div>
    );
  }

  // ===========================================
  // RENDER BACKUP CODES
  // ===========================================
  if (step === "backup") {
    return (
      <div className={`max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg ${className}`}>
        <div className="text-center mb-6">
          <Check className="w-12 h-12 text-green-500 mx-auto mb-2" />
          <h2 className="text-2xl font-bold">2FA Enabled Successfully!</h2>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
            <h3 className="font-semibold text-yellow-800 mb-2">Important!</h3>
            <p className="text-sm text-yellow-700">
              Save these backup codes in a secure location. You can use them to access your account if you lose your authenticator device.
            </p>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold">Backup Codes</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowBackupCodes(!showBackupCodes)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  {showBackupCodes ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
                <button
                  onClick={() => copyToClipboard(backupCodes.join("\n"), "Backup codes")}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div className="space-y-1">
              {backupCodes.map((code, index) => (
                <div
                  key={index}
                  className="px-3 py-1 bg-gray-50 rounded font-mono text-sm"
                >
                  {showBackupCodes ? code : "••••••••"}
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={downloadBackupCodes}
            className="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Download Backup Codes
          </button>
        </div>

        {onCancel && (
          <button
            onClick={onCancel}
            className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Finish
          </button>
        )}
      </div>
    );
  }

  // ===========================================
  // LOADING STATE
  // ===========================================
  return (
    <div className={`max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg ${className}`}>
      <div className="text-center">
        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
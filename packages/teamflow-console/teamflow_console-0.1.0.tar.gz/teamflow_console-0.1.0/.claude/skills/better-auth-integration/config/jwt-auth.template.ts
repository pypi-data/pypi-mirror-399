import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { jwt } from "better-auth/plugins";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  
  secret: process.env.BETTER_AUTH_SECRET!,
  
  plugins: [
    jwt({
      secret: process.env.BETTER_AUTH_SECRET!,
      // Optional: Configure token expiration
      expirationTime: "7d", 
    })
  ],
  
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
  },
  
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    // Add other providers as needed
  },
});

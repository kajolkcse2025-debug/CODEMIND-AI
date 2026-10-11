import { zodResolver } from "@hookform/resolvers/zod";
import { MailCheck } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { fieldAria } from "@/components/ui/field-aria";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/features/auth/auth-context";
import { AuthLayout } from "@/features/auth/AuthLayout";
import { authErrorMessage } from "@/features/auth/firebaseErrors";
import { forgotPasswordSchema, type ForgotPasswordValues } from "@/features/auth/schemas";

export function ForgotPasswordPage() {
  const { sendPasswordReset, firebaseConfigured } = useAuth();
  const [sent, setSent] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordValues>({ resolver: zodResolver(forgotPasswordSchema) });

  async function onSubmit(values: ForgotPasswordValues) {
    setFormError(null);
    try {
      await sendPasswordReset(values.email);
      setSent(true);
    } catch (error) {
      const code =
        error && typeof error === "object" && "code" in error
          ? String((error as { code: unknown }).code)
          : "";
      // Never reveal whether an address has an account (prevents e-mail enumeration).
      if (code === "auth/user-not-found" || code === "auth/invalid-email") setSent(true);
      else setFormError(authErrorMessage(error));
    }
  }

  return (
    <AuthLayout
      title="Reset your password"
      description="Enter your email and we will send a reset link."
      footer={
        <Link to="/login" className="text-primary hover:underline">
          Back to sign in
        </Link>
      }
    >
      {sent ? (
        <div role="status" className="flex gap-3 rounded-md border bg-card p-4 text-sm">
          <MailCheck className="mt-0.5 size-5 shrink-0 text-success" aria-hidden="true" />
          <p>If an account exists for that email, a reset link is on its way. Check your inbox.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
          <FormField label="Email" htmlFor="email" error={errors.email?.message}>
            <Input
              type="email"
              autoComplete="email"
              {...fieldAria("email", errors.email?.message)}
              {...register("email")}
            />
          </FormField>
          {formError ? (
            <p role="alert" className="text-sm text-danger">
              {formError}
            </p>
          ) : null}
          <Button type="submit" className="w-full" disabled={isSubmitting || !firebaseConfigured}>
            {isSubmitting ? "Sending…" : "Send reset link"}
          </Button>
        </form>
      )}
    </AuthLayout>
  );
}

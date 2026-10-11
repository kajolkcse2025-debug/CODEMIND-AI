import { zodResolver } from "@hookform/resolvers/zod";
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
import { GoogleButton } from "@/features/auth/GoogleButton";
import { registerSchema, type RegisterValues } from "@/features/auth/schemas";

export function RegisterPage() {
  const { registerWithEmail, firebaseConfigured } = useAuth();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterValues>({ resolver: zodResolver(registerSchema) });

  async function onSubmit(values: RegisterValues) {
    setFormError(null);
    try {
      await registerWithEmail(values.email, values.password);
    } catch (error) {
      setFormError(authErrorMessage(error));
    }
  }

  return (
    <AuthLayout
      title="Create your account"
      description="Set up your profile in a couple of minutes."
      footer={
        <>
          Already have an account?{" "}
          <Link to="/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <FormField label="Email" htmlFor="email" error={errors.email?.message}>
          <Input
            type="email"
            autoComplete="email"
            {...fieldAria("email", errors.email?.message)}
            {...register("email")}
          />
        </FormField>
        <FormField
          label="Password"
          htmlFor="password"
          error={errors.password?.message}
          hint="At least 8 characters."
        >
          <Input
            type="password"
            autoComplete="new-password"
            {...fieldAria("password", errors.password?.message, true)}
            {...register("password")}
          />
        </FormField>
        <FormField
          label="Confirm password"
          htmlFor="confirmPassword"
          error={errors.confirmPassword?.message}
        >
          <Input
            type="password"
            autoComplete="new-password"
            {...fieldAria("confirmPassword", errors.confirmPassword?.message)}
            {...register("confirmPassword")}
          />
        </FormField>
        {formError ? (
          <p role="alert" className="text-sm text-danger">
            {formError}
          </p>
        ) : null}
        <Button type="submit" className="w-full" disabled={isSubmitting || !firebaseConfigured}>
          {isSubmitting ? "Creating account…" : "Create account"}
        </Button>
      </form>
      <div className="my-5 flex items-center gap-3 text-xs text-muted-foreground">
        <span className="h-px flex-1 bg-border" /> or <span className="h-px flex-1 bg-border" />
      </div>
      <GoogleButton onError={setFormError} />
    </AuthLayout>
  );
}

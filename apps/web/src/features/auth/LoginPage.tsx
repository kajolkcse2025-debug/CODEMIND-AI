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
import { loginSchema, type LoginValues } from "@/features/auth/schemas";

export function LoginPage() {
  const { signInWithEmail, firebaseConfigured } = useAuth();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: LoginValues) {
    setFormError(null);
    try {
      await signInWithEmail(values.email, values.password);
      // PublicOnly redirects once the auth state changes.
    } catch (error) {
      setFormError(authErrorMessage(error));
    }
  }

  return (
    <AuthLayout
      title="Sign in"
      description="Welcome back. Pick up where you left off."
      footer={
        <>
          New to CodeMind?{" "}
          <Link to="/register" className="text-primary hover:underline">
            Create an account
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
        <FormField label="Password" htmlFor="password" error={errors.password?.message}>
          <Input
            type="password"
            autoComplete="current-password"
            {...fieldAria("password", errors.password?.message)}
            {...register("password")}
          />
        </FormField>
        <div className="text-right text-sm">
          <Link to="/forgot-password" className="text-muted-foreground hover:text-foreground">
            Forgot password?
          </Link>
        </div>
        {formError ? (
          <p role="alert" className="text-sm text-danger">
            {formError}
          </p>
        ) : null}
        <Button type="submit" className="w-full" disabled={isSubmitting || !firebaseConfigured}>
          {isSubmitting ? "Signing in…" : "Sign in"}
        </Button>
      </form>
      <div className="my-5 flex items-center gap-3 text-xs text-muted-foreground">
        <span className="h-px flex-1 bg-border" /> or <span className="h-px flex-1 bg-border" />
      </div>
      <GoogleButton onError={setFormError} />
    </AuthLayout>
  );
}

import js from "@eslint/js";
import prettier from "eslint-config-prettier";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist", "node_modules", "coverage"] },
  {
    files: ["**/*.{ts,tsx}"],
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    languageOptions: { ecmaVersion: 2022, globals: globals.browser },
    plugins: { "react-hooks": reactHooks, "react-refresh": reactRefresh },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
      "@typescript-eslint/consistent-type-imports": "error",
      "@typescript-eslint/no-explicit-any": "error",
      // Server state goes through the API client and TanStack Query, never ad-hoc fetch().
      "no-restricted-globals": [
        "error",
        { name: "fetch", message: "Use the API client in src/lib/api." },
      ],
    },
  },
  {
    // The API client is the one place allowed to call fetch directly.
    files: ["src/lib/api/client.ts", "src/**/*.test.{ts,tsx}"],
    rules: { "no-restricted-globals": "off" },
  },
  prettier,
);

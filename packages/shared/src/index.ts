/** Types generated from the backend's OpenAPI schema. Regenerate with `npm run gen:api`. */
import type { components } from "./api";

export type { components, paths } from "./api";

type Schemas = components["schemas"];

export type ProfileIn = Schemas["ProfileIn"];
export type ProfileOut = Schemas["ProfileOut"];
export type UserOut = Schemas["UserOut"];
export type MeResponse = Schemas["MeResponse"];
export type ErrorResponse = Schemas["ErrorResponse"];

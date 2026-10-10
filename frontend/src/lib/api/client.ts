import createClient from "openapi-fetch";

import type { paths } from "./generated";

const baseUrl =
  process.env.NEXT_PUBLIC_PARITY_API_URL ?? "http://127.0.0.1:8000";

export const apiClient = createClient<paths>({ baseUrl });

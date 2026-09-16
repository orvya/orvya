export type OrvyaApiError = {
  erro: {
    code: string;
    mensagem: string;
    field: string | null;
    operation_id: string;
    retryable: boolean;
  };
};

let csrfToken: string | null = null;

export function setCsrfToken(token: string | null): void {
  csrfToken = token;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");

  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (csrfToken && !["GET", "HEAD", "OPTIONS"].includes(method)) {
    headers.set("X-Orvya-CSRF", csrfToken);
  }

  const response = await fetch(`/api/v1${path}`, {
    ...init,
    method,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const body = (await response.json()) as OrvyaApiError;
    throw body;
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

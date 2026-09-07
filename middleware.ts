// Edge gate for the CelestJux editors.
//
// This runs before the CDN cache on every request, so it covers the art
// (sprites/pack.png, sprites/char-atlas.js) and not just the HTML. A password
// screen drawn in the page would not — the assets have their own URLs.
//
// The password lives in the EDITOR_PASSWORD environment variable and is never
// shipped to the browser. No default: a deployment without it refuses to serve
// rather than quietly opening the door.

export const config = {
  matcher: '/((?!_vercel/).*)',
};

const COOKIE = 'cjx';
const MAX_AGE = 60 * 60 * 24 * 30; // 30 days

async function token(password: string): Promise<string> {
  const bytes = new TextEncoder().encode('cjx:' + password);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function cookieValue(header: string | null, name: string): string | null {
  if (!header) return null;
  for (const part of header.split(';')) {
    const eq = part.indexOf('=');
    if (eq === -1) continue;
    if (part.slice(0, eq).trim() === name) return part.slice(eq + 1).trim();
  }
  return null;
}

function gate(message: string | null, status: number): Response {
  const note = message
    ? `<p class="err">${message}</p>`
    : `<p class="sub">Ask abang for the password.</p>`;
  return new Response(
    `<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>CelestJux Editors</title>
<style>
  :root { color-scheme: dark; }
  body { margin:0; min-height:100vh; display:grid; place-items:center;
         background:#14161c; color:#e8e6e3;
         font:15px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }
  form { width:min(92vw,340px); text-align:center; }
  h1 { margin:0 0 4px; font-size:22px; font-weight:600; letter-spacing:.2px; }
  .sub, .err { margin:0 0 22px; font-size:13px; }
  .sub { color:#8b8f9a; }
  .err { color:#e2645f; }
  input { width:100%; box-sizing:border-box; padding:11px 13px; margin-bottom:10px;
          background:#1d2029; color:#e8e6e3; border:1px solid #2f333f; border-radius:8px;
          font:inherit; }
  input:focus { outline:none; border-color:#6a8cff; }
  button { width:100%; padding:11px; border:0; border-radius:8px; cursor:pointer;
           background:#6a8cff; color:#0f1116; font:inherit; font-weight:600; }
  button:hover { background:#7d9bff; }
</style>
<form method="POST" action="/__gate">
  <h1>CelestJux Editors</h1>
  ${note}
  <input type="password" name="password" placeholder="password" autofocus autocomplete="current-password">
  <button type="submit">Enter</button>
</form>`,
    {
      status,
      headers: {
        'content-type': 'text/html; charset=utf-8',
        'cache-control': 'no-store',
        'x-robots-tag': 'noindex, nofollow',
      },
    },
  );
}

export default async function middleware(request: Request) {
  const password = process.env.EDITOR_PASSWORD;
  if (!password) {
    return new Response(
      'EDITOR_PASSWORD is not set on this deployment. Set it in the Vercel project ' +
        'environment variables and redeploy.',
      { status: 500, headers: { 'content-type': 'text/plain; charset=utf-8' } },
    );
  }

  const expected = await token(password);
  const url = new URL(request.url);

  if (url.pathname === '/__gate') {
    if (request.method !== 'POST') return gate(null, 405);
    const form = await request.formData();
    const given = String(form.get('password') ?? '');
    if ((await token(given)) !== expected) return gate('Wrong password.', 401);
    return new Response(null, {
      status: 303,
      headers: {
        location: '/',
        'cache-control': 'no-store',
        'set-cookie':
          `${COOKIE}=${expected}; Path=/; Max-Age=${MAX_AGE}; ` +
          'HttpOnly; Secure; SameSite=Lax',
      },
    });
  }

  if (cookieValue(request.headers.get('cookie'), COOKIE) === expected) return;

  return gate(null, 401);
}

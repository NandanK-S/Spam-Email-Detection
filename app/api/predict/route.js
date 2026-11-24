const BACKEND = process.env.BACKEND_URL || "http://127.0.0.1:8000";
const MAX_EMAIL_LENGTH = 50000;

export async function POST(request) {
  try {
    const body = await request.json();

    if (body?.text && typeof body.text === "string" && body.text.length > MAX_EMAIL_LENGTH) {
      return Response.json(
        { detail: `Email text exceeds maximum allowed length of ${MAX_EMAIL_LENGTH} characters` },
        { status: 400 }
      );
    }

    const res = await fetch(`${BACKEND}/api/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10000),
    });

    const data = await res.json();
    return Response.json(data, { status: res.status });
  } catch (err) {
    if (err.name === "TimeoutError") {
      return Response.json(
        { error: "Backend request timed out (service unresponsive)" },
        { status: 504 }
      );
    }
    return Response.json(
      { error: "Backend server offline (connection refused at 127.0.0.1:8000)" },
      { status: 503 }
    );
  }
}

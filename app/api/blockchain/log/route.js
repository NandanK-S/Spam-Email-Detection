const BACKEND = process.env.BACKEND_URL || "http://127.0.0.1:8000";

export async function GET() {
  try {
    const res = await fetch(`${BACKEND}/api/blockchain/log`, {
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

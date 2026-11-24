const BACKEND = process.env.BACKEND_URL || "http://127.0.0.1:8000";

export async function POST(request) {
  try {
    const body = await request.json();

    const res = await fetch(`${BACKEND}/api/blockchain/verify`, {
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

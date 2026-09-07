const BACKEND = process.env.BACKEND_URL || "http://127.0.0.1:8000";

export async function GET() {
  const res = await fetch(`${BACKEND}/api/models/comparison`);
  const data = await res.json();
  return Response.json(data, { status: res.status });
}

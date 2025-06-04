import { NextResponse } from "next/server";

export async function GET(){
  try {
    const res = await fetch('http://api_backend:8000')
    const data = await res.json()
    console.log(data)
  } catch(error){
    console.log(error)
  }
  return NextResponse.json({message: "Custom message from Next"})
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const res = await fetch('http://api_backend:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    console.log(data)
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch backend' + error }, { status: 500 });
  }
}
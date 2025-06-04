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
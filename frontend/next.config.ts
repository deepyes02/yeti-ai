import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  async rewrites(){
    return [
      {
        source: '/api/:path*',
        destination: 'http://api_backend:8000/:path*'
      }
    ]
  }
};

export default nextConfig;

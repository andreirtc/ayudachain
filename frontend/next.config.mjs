/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  devIndicators: false,
  distDir: process.env.AYUDACHAIN_BUILD_DIR || ".next",
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;

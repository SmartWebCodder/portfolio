/** @type {import('next').NextConfig} */
const nextConfig = {
  // The site is entirely static, so it exports to plain files and Caddy serves
  // them directly: no Node process to keep alive on the VPS.
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: false },
};
export default nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  basePath: process.env.NODE_ENV === 'production' ? '/rag7' : '',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/rag7/' : '',
  output: 'export',
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig

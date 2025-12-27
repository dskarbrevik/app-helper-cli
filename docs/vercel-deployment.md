# Vercel Deployment Guide

Detailed guide for deploying your Next.js frontend to Vercel.

## Overview

Vercel is the platform built by the creators of Next.js, offering seamless deployment, automatic HTTPS, and global CDN. This guide covers:
- Deploying from GitHub repository
- Configuring environment variables
- Custom domains and preview deployments
- Performance monitoring
- Troubleshooting common issues

## Prerequisites

- GitHub account with your frontend repository
- Vercel account (sign up at [vercel.com](https://vercel.com))
- Frontend code based on `hello-world-fe` template
- Backend deployed and accessible (Railway URL)
- Supabase project configured

## Create Frontend Repository

### Use GitHub Template

1. Visit [hello-world-fe repository](https://github.com/your-org/hello-world-fe)
2. Click **Use this template** → **Create a new repository**
3. Configure:
   - **Owner:** Your GitHub username or organization
   - **Repository name:** `your-app-fe` (or your chosen name)
   - **Visibility:** Private (recommended) or Public
4. Click **Create repository**

### Clone and Configure Locally

```bash
git clone https://github.com/your-username/your-app-fe.git
cd your-app-fe

# Configure environment with dh
dh setup

# Test locally
npm run dev
# Visit http://localhost:3000
```

## Deploy to Vercel

### Import Project

1. **Sign in to Vercel**
   - Visit [vercel.com](https://vercel.com)
   - Click **Login** → **Continue with GitHub**
   - Authorize Vercel to access your repositories

2. **Create New Project**
   - From Vercel Dashboard, click **Add New** → **Project**
   - Find your `your-app-fe` repository
   - Click **Import**

3. **Configure Project**
   
   Vercel auto-detects Next.js:
   - **Framework Preset:** Next.js
   - **Root Directory:** `./` (default)
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)

   Keep defaults unless you have custom setup.

### Environment Variables

**Critical:** Add these before deploying:

| Variable | Value | Where to Get |
|----------|-------|--------------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://xxx.supabase.co` | Supabase → Settings → API |
| `NEXT_PUBLIC_SUPABASE_KEY` | `eyJhbG...` (anon key) | Supabase → Settings → API |
| `NEXT_PUBLIC_API_URL` | `https://your-app-be.up.railway.app` | Railway dashboard |

**Add variables:**

1. In the import screen, scroll to **Environment Variables**
2. Click **Add** for each variable:
   - **Key:** `NEXT_PUBLIC_SUPABASE_URL`
   - **Value:** Your Supabase URL
   - **Environments:** Production, Preview, Development (select all)
3. Repeat for remaining variables

**⚠️ Important:** 
- Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser
- Never put secret keys here (like Supabase service_role key)
- Always use the anon/public key for frontend

### Deploy

1. Click **Deploy**
2. Vercel builds your project (~2-3 minutes)
3. Watch build logs in real-time
4. On success, you'll see your live URL: `your-app.vercel.app`

### Verify Deployment

Test your deployed application:

```bash
# Visit your Vercel URL
open https://your-app.vercel.app

# Test signup/login flow:
# 1. Click "Sign Up"
# 2. Enter email from allowed_users list
# 3. Enter password
# 4. Should redirect to dashboard
```

## Configure Supabase Redirect URLs

After deployment, update Supabase to allow auth callbacks:

1. Go to **Supabase Dashboard** → **Authentication** → **URL Configuration**
2. Add your Vercel URL to **Site URL:**
   ```
   https://your-app.vercel.app
   ```
3. Add to **Redirect URLs:**
   ```
   https://your-app.vercel.app/auth/callback
   http://localhost:3000/auth/callback
   ```
4. Click **Save**

**Without this step:** Users will get redirect errors after login.

## Custom Domain

### Add Custom Domain

Use your own domain instead of `.vercel.app`:

1. Go to **Project Settings** → **Domains**
2. Click **Add**
3. Enter your domain: `yourdomain.com`
4. Click **Add**

### Configure DNS

Vercel provides DNS instructions:

**For Root Domain (`yourdomain.com`):**
- **Type:** A Record
- **Name:** `@`
- **Value:** `76.76.21.21`

**For Subdomain (`www.yourdomain.com`):**
- **Type:** CNAME
- **Name:** `www`
- **Value:** `cname.vercel-dns.com`

**For App Subdomain (`app.yourdomain.com`):**
- **Type:** CNAME
- **Name:** `app`
- **Value:** `cname.vercel-dns.com`

### Verify Domain

1. Wait for DNS propagation (5 minutes to 48 hours)
2. Vercel automatically provisions SSL certificate
3. Visit your custom domain
4. **Update Supabase URLs** with your custom domain

## Continuous Deployment

### Automatic Deployments

Vercel auto-deploys on every push:

**Production deployments (main branch):**
```bash
git add .
git commit -m "Update feature"
git push origin main
```
- Vercel builds and deploys to production URL
- Takes ~2-3 minutes
- Atomic deployments (old version serves until new is ready)

**Preview deployments (feature branches):**
```bash
git checkout -b feature/new-ui
git add .
git commit -m "New UI design"
git push origin feature/new-ui
```
- Vercel creates a unique preview URL
- Every push updates the preview
- Great for testing before merging

### Pull Request Previews

When you open a PR:
1. Vercel bot comments with preview URL
2. Each commit updates the preview
3. Team can test changes before merge
4. Preview deleted when PR is closed

## Environment Management

### Multiple Environments

Vercel supports three environment types:

| Environment | Trigger | Use Case |
|-------------|---------|----------|
| **Production** | Push to `main` branch | Live application |
| **Preview** | Push to any other branch or PR | Testing features |
| **Development** | Local development | Local testing with production env vars |

### Environment-Specific Variables

Set different values per environment:

1. Go to **Project Settings** → **Environment Variables**
2. Click **Add New**
3. Select specific environments:
   - **Production only:** Live app values
   - **Preview only:** Test/staging values
   - **Development only:** Local dev overrides

**Example use cases:**
- Use staging Supabase project for previews
- Use test backend API for feature branches
- Enable debug logging in preview/development

### Updating Variables

**Update existing variable:**
1. Find variable in Project Settings
2. Click **Edit**
3. Change value
4. **Redeploy** to apply changes (variables don't auto-update)

**Trigger redeploy:**
1. Go to **Deployments** tab
2. Click **...** on latest deployment
3. Click **Redeploy**

Or push a commit to trigger new deployment.

## Monitoring & Debugging

### View Deployment Logs

Check build and runtime logs:

1. Go to **Deployments** tab
2. Click on a deployment
3. View:
   - **Building:** Shows build output, npm install, `next build`
   - **Runtime Logs:** Shows server-side logs (API routes, middleware)

**Common build errors:**
- TypeScript errors: Fix type issues locally
- Missing dependencies: Check `package.json`
- Environment variables: Verify all required vars are set

### Analytics

Monitor traffic and performance:

1. Go to **Analytics** tab (requires Vercel Pro)
2. View:
   - **Visitors:** Unique and total
   - **Page views:** Most popular pages
   - **Top Pages:** What users visit
   - **Top Referrers:** Where traffic comes from

**Web Vitals:**
- **LCP** (Largest Contentful Paint): Loading performance
- **FID** (First Input Delay): Interactivity
- **CLS** (Cumulative Layout Shift): Visual stability

Target: All metrics in "Good" range (green).

### Real-Time Logs

View live logs:

1. Install Vercel CLI: `npm i -g vercel`
2. Link project: `vercel link`
3. Stream logs: `vercel logs --follow`

**Useful for:**
- Debugging runtime errors
- Monitoring API route execution
- Checking middleware logs

### Speed Insights

Enable Speed Insights to track performance:

1. Go to **Speed Insights** tab
2. Click **Enable Speed Insights**
3. View real user performance data

## Preview Deployments

### Branch Previews

Every branch gets a preview URL:

**Create feature branch:**
```bash
git checkout -b feature/new-dashboard
# Make changes
git add .
git commit -m "Add new dashboard"
git push origin feature/new-dashboard
```

**Access preview:**
1. Check Vercel dashboard
2. Find deployment under **Deployments** tab
3. Click to view unique URL: `your-app-git-feature-new-dashboard.vercel.app`

### Share Previews

Share preview URLs with team:
1. Copy preview URL from deployment
2. Send to stakeholders for feedback
3. Iterate and push updates
4. Preview URL updates automatically

### Password Protection (Pro)

Protect preview deployments:

1. Go to **Project Settings** → **Deployment Protection**
2. Enable **Password Protection**
3. Set password
4. Share password with team

Users must enter password to access previews.

## Performance Optimization

### Image Optimization

Next.js Image component is automatically optimized by Vercel:

```tsx
import Image from 'next/image'

<Image 
  src="/hero.jpg"
  width={1200}
  height={600}
  alt="Hero"
/>
```

**Benefits:**
- Automatic WebP/AVIF conversion
- Lazy loading
- Responsive sizes
- CDN caching

### Edge Functions

Deploy API routes to edge for faster response:

```tsx
// app/api/hello/route.ts
export const runtime = 'edge'

export async function GET() {
  return Response.json({ message: 'Hello from edge!' })
}
```

**Benefits:**
- Lower latency (runs closer to users)
- Auto-scales globally
- No cold starts

### Static Generation

Pre-render pages at build time for instant loading:

```tsx
// app/about/page.tsx
export default async function AboutPage() {
  // Data fetched at build time
  const data = await fetchData()
  return <div>{data}</div>
}
```

**Benefits:**
- Instant page loads
- No server needed
- Perfect for marketing pages, blogs

### Caching Headers

Set cache headers for API routes:

```tsx
export async function GET() {
  return Response.json(
    { data: 'cached' },
    { 
      headers: { 
        'Cache-Control': 's-maxage=3600, stale-while-revalidate' 
      }
    }
  )
}
```

## Troubleshooting

### Build Fails

**Issue:** Build fails with TypeScript errors

**Solution:**
1. Run `npm run build` locally to reproduce
2. Fix TypeScript errors
3. Ensure `tsconfig.json` is committed
4. Push fixes

**Issue:** Build fails with "Module not found"

**Solution:**
1. Check `package.json` has all dependencies
2. Run `npm install` locally
3. Commit `package-lock.json`
4. Push to trigger rebuild

### Environment Variables Not Working

**Issue:** App can't access environment variables

**Solution:**
1. Verify variables are prefixed with `NEXT_PUBLIC_`
2. Check variables are set in Vercel dashboard
3. Redeploy after adding/changing variables
4. Use `console.log(process.env.NEXT_PUBLIC_*)` to debug

### Supabase Auth Errors

**Issue:** "redirect_uri mismatch" or "Invalid redirect URL"

**Solution:**
1. Go to Supabase → Authentication → URL Configuration
2. Add Vercel URL to redirect URLs:
   - `https://your-app.vercel.app/auth/callback`
   - `https://your-app-git-branch.vercel.app/auth/callback` (for previews)
3. Include all preview URL patterns if needed

### API Routes Return 500

**Issue:** API routes fail with internal server error

**Solution:**
1. Check **Runtime Logs** in deployment details
2. Look for error stack traces
3. Verify environment variables are set
4. Test API route locally first
5. Check Supabase/Railway services are accessible

### Slow Performance

**Issue:** Pages load slowly

**Solution:**
1. Check **Speed Insights** for bottlenecks
2. Optimize images with Next.js Image component
3. Use static generation for non-dynamic pages
4. Enable edge runtime for API routes
5. Minimize client-side JavaScript

## Advanced Configuration

### Custom Build Command

Override default build:

1. Go to **Project Settings** → **Build & Development Settings**
2. **Build Command:**
   ```bash
   npm run build && npm run post-build
   ```

### Root Directory

For monorepos with frontend in subdirectory:

1. **Root Directory:** `packages/frontend`
2. Vercel builds from that directory

### Redirects & Rewrites

Add in `next.config.ts`:

```typescript
module.exports = {
  async redirects() {
    return [
      {
        source: '/old-page',
        destination: '/new-page',
        permanent: true,
      },
    ]
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://your-backend.railway.app/:path*',
      },
    ]
  },
}
```

### Custom Headers

Set security headers:

```typescript
module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
}
```

## Vercel CLI

### Installation

```bash
npm i -g vercel
```

### Useful Commands

```bash
# Deploy from CLI
vercel

# Deploy to production
vercel --prod

# Link local project
vercel link

# View environment variables
vercel env ls

# Pull environment variables locally
vercel env pull .env.local

# View logs
vercel logs

# Open dashboard
vercel
```

## Team Collaboration

### Add Team Members

1. Go to **Project Settings** → **Team**
2. Click **Invite**
3. Enter email addresses
4. Select role: **Viewer**, **Developer**, or **Owner**

**Roles:**
- **Viewer:** View deployments and settings
- **Developer:** Create deployments, view logs
- **Owner:** Full access, billing, delete project

### Deployment Comments

Comment on deployments:

1. Open a deployment
2. Click **Comments** tab
3. Add feedback or notes
4. Tag team members

Great for QA feedback on preview deployments.

## Cost Management

### Free Tier

Vercel Hobby plan includes:
- Unlimited deployments
- 100 GB bandwidth/month
- 100 GB-Hrs compute/month
- Automatic HTTPS
- Preview deployments

**Limitations:**
- No team collaboration
- No password protection
- Limited analytics

### Pro Plan ($20/month)

**When to upgrade:**
- Need team collaboration
- Want advanced analytics
- Need password-protected previews
- Require more bandwidth

**Pricing:** 
- $20/month base
- Includes 1TB bandwidth
- Additional bandwidth: $40/TB

### Monitor Usage

1. Go to **Account Settings** → **Usage**
2. View:
   - Bandwidth usage
   - Build minutes
   - Serverless function invocations
3. Set up usage alerts

## Next Steps

- Test full authentication flow
- Set up custom domain
- Enable Web Analytics
- Configure staging environment
- [Main Deployment Guide](../DEPLOYMENT_GUIDE.md) - Complete workflow

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment Docs](https://nextjs.org/docs/deployment)
- [Vercel Discord](https://discord.gg/vercel) - Community support
- [Next.js GitHub Discussions](https://github.com/vercel/next.js/discussions)

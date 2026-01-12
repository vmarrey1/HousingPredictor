"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import toast from 'react-hot-toast'

// Configure axios base URL for production
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || ''
if (API_BASE) {
  axios.defaults.baseURL = API_BASE
}
axios.defaults.withCredentials = true

export default function AuthPage() {
  const router = useRouter()
  const [mode, setMode] = useState<'signin' | 'signup'>('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // If already logged in, redirect
    axios.get('/api/auth/me').then(res => {
      if (res.data?.user) router.push('/')
    }).catch(() => {/* ignore */})
  }, [router])

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      toast.error('Email and password are required')
      return
    }
    try {
      setLoading(true)
      if (mode === 'signup') {
        await axios.post('/api/auth/signup', { email, password })
        toast.success('Account created')
      } else {
        await axios.post('/api/auth/login', { email, password })
        toast.success('Signed in')
      }
      router.push('/')
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Authentication failed'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-sm border p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          {mode === 'signup' ? 'Create your account' : 'Sign in to your account'}
        </h1>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field w-full"
              placeholder="you@berkeley.edu"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field w-full"
              placeholder="••••••••"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition disabled:opacity-60"
          >
            {loading ? 'Please wait…' : (mode === 'signup' ? 'Sign Up' : 'Sign In')}
          </button>
        </form>

        <div className="text-sm text-gray-600 mt-6 text-center">
          {mode === 'signup' ? (
            <span>
              Already have an account?{' '}
              <button onClick={() => setMode('signin')} className="text-blue-600 hover:underline">Sign in</button>
            </span>
          ) : (
            <span>
              New here?{' '}
              <button onClick={() => setMode('signup')} className="text-blue-600 hover:underline">Create an account</button>
            </span>
          )}
        </div>
      </div>
    </div>
  )
}



"use client"

import { useEffect, useState } from 'react'
import axios from 'axios'
import { useRouter } from 'next/navigation'

axios.defaults.withCredentials = true

export default function SchedulesPage() {
  const router = useRouter()
  const [schedules, setSchedules] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('/api/auth/me').then(res => {
      if (!res.data?.user) {
        router.push('/auth')
        return
      }
      axios.get('/api/schedules').then(r => {
        setSchedules(r.data || [])
        setLoading(false)
      }).catch(() => setLoading(false))
    }).catch(() => router.push('/auth'))
  }, [router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-600">Loading…</div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-4">Your Saved Schedules</h1>
        {schedules.length === 0 ? (
          <p className="text-gray-600">No saved schedules yet.</p>
        ) : (
          <div className="space-y-3">
            {schedules.map((s) => (
              <div key={s.id} className="p-4 bg-white rounded-lg border flex items-center justify-between">
                <div>
                  <p className="font-semibold">{s.name}</p>
                  <p className="text-sm text-gray-500">Updated {s.updated_at}</p>
                </div>
                <button
                  onClick={() => {
                    sessionStorage.setItem('fourYearPlan', JSON.stringify(s.data))
                    router.push('/schedule')
                  }}
                  className="px-3 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
                >
                  Load
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}



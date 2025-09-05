'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { GraduationCap, Calendar, BookOpen, ChevronRight, Loader2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import axios from 'axios'

export default function Home() {
  const [majors, setMajors] = useState<string[]>([])
  const [selectedMajor, setSelectedMajor] = useState('')
  const [graduationSemester, setGraduationSemester] = useState('Spring 2028')
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [completedCourses, setCompletedCourses] = useState<string[]>([])
  const [newCourse, setNewCourse] = useState('')
  const [courseSuggestions, setCourseSuggestions] = useState<any[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const router = useRouter()

  useEffect(() => {
    loadMajors()
  }, [])

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('.relative')) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const loadMajors = async () => {
    try {
      setIsLoading(true)
      const response = await axios.get('/api/majors')
      setMajors(response.data)
    } catch (error) {
      console.error('Error loading majors:', error)
      toast.error('Failed to load majors')
    } finally {
      setIsLoading(false)
    }
  }

  const searchCourses = async (query: string) => {
    if (query.length < 2) {
      setCourseSuggestions([])
      setShowSuggestions(false)
      return
    }

    try {
      const response = await axios.post('/api/search-courses', { query })
      setCourseSuggestions(response.data.courses || [])
      setShowSuggestions(true)
    } catch (error) {
      console.error('Error searching courses:', error)
      setCourseSuggestions([])
    }
  }

  const addCourse = (courseCode?: string) => {
    const courseToAdd = courseCode || newCourse.trim().toUpperCase()
    if (courseToAdd && !completedCourses.includes(courseToAdd)) {
      setCompletedCourses([...completedCourses, courseToAdd])
      setNewCourse('')
      setShowSuggestions(false)
    }
  }

  const removeCourse = (course: string) => {
    setCompletedCourses(completedCourses.filter(c => c !== course))
  }

  const generatePlan = async () => {
    if (!selectedMajor) {
      toast.error('Please select a major')
      return
    }

    try {
      setIsGenerating(true)
      const [term, year] = graduationSemester.split(' ')
      const response = await axios.post('/api/generate-plan', {
        major: selectedMajor,
        graduation_year: parseInt(year),
        graduation_semester: term,
        current_year: currentYear,
        completed_courses: completedCourses,
        preferences: {}
      })

      // Store the plan in sessionStorage and navigate to results page
      sessionStorage.setItem('fourYearPlan', JSON.stringify(response.data))
      router.push('/schedule')
    } catch (error: any) {
      console.error('Error generating plan:', error)
      toast.error(error.response?.data?.error || 'Failed to generate plan')
    } finally {
      setIsGenerating(false)
    }
  }

  const currentYearOptions = Array.from({ length: 6 }, (_, i) => new Date().getFullYear() + i)
  
  // Generate graduation semester options
  const graduationSemesters = []
  const baseYear = new Date().getFullYear()
  for (let i = 0; i < 8; i++) {
    const year = baseYear + i
    graduationSemesters.push(`Fall ${year}`)
    graduationSemesters.push(`Spring ${year + 1}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-center">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <GraduationCap className="h-8 w-8 text-primary-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">UC Berkeley Four Year Plan Generator</h1>
                <p className="text-gray-600">Create your personalized academic roadmap</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="card"
        >
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Plan Your Berkeley Journey</h2>
            <p className="text-gray-600">
              Select your major and graduation year to generate a personalized four-year academic plan
            </p>
          </div>

          <div className="space-y-6">
            {/* Major Selection */}
            <div>
              <label htmlFor="major" className="block text-sm font-medium text-gray-700 mb-2">
                Select Your Major
              </label>
              <select
                id="major"
                value={selectedMajor}
                onChange={(e) => setSelectedMajor(e.target.value)}
                className="input-field"
                disabled={isLoading}
              >
                <option value="">Choose a major...</option>
                {majors.map((major) => (
                  <option key={major} value={major}>
                    {major}
                  </option>
                ))}
              </select>
              {isLoading && (
                <div className="flex items-center mt-2 text-sm text-gray-500">
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Loading majors...
                </div>
              )}
            </div>

            {/* Current Year Selection */}
            <div>
              <label htmlFor="current-year" className="block text-sm font-medium text-gray-700 mb-2">
                Current Academic Year
              </label>
              <select
                id="current-year"
                value={currentYear}
                onChange={(e) => setCurrentYear(parseInt(e.target.value))}
                className="input-field"
              >
                {currentYearOptions.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>

            {/* Graduation Semester Selection */}
            <div>
              <label htmlFor="graduation-semester" className="block text-sm font-medium text-gray-700 mb-2">
                Expected Graduation Semester
              </label>
              <select
                id="graduation-semester"
                value={graduationSemester}
                onChange={(e) => setGraduationSemester(e.target.value)}
                className="input-field"
              >
                {graduationSemesters.map((semester) => (
                  <option key={semester} value={semester}>
                    {semester}
                  </option>
                ))}
              </select>
            </div>

            {/* Completed Courses */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Completed Courses (Optional)
              </label>
              <div className="flex space-x-2 mb-2">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={newCourse}
                    onChange={(e) => {
                      setNewCourse(e.target.value)
                      searchCourses(e.target.value)
                    }}
                    onFocus={() => {
                      if (courseSuggestions.length > 0) setShowSuggestions(true)
                    }}
                    placeholder="e.g., MATH 1A, COMPSCI 61A"
                    className="input-field w-full"
                    onKeyPress={(e) => e.key === 'Enter' && addCourse()}
                  />
                  
                  {/* Autocomplete Dropdown */}
                  {showSuggestions && courseSuggestions.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {courseSuggestions.map((course, index) => (
                        <div
                          key={index}
                          onClick={() => addCourse(course.code)}
                          className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-gray-900">{course.code}</p>
                              <p className="text-sm text-gray-600 truncate">{course.title}</p>
                            </div>
                            <div className="text-right text-xs text-gray-500 ml-2">
                              <p>{course.units} units</p>
                              <p>{course.terms}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => addCourse()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add
                </button>
              </div>
              {completedCourses.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {completedCourses.map((course) => (
                    <span
                      key={course}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800"
                    >
                      {course}
                      <button
                        type="button"
                        onClick={() => removeCourse(course)}
                        className="ml-2 text-green-600 hover:text-green-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Generate Button */}
            <button
              onClick={generatePlan}
              disabled={!selectedMajor || isGenerating}
              className="w-full btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Generating Your Plan...</span>
                </>
              ) : (
                <>
                  <BookOpen className="h-5 w-5" />
                  <span>Generate Four Year Plan</span>
                </>
              )}
            </button>
          </div>
        </motion.div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="text-center p-6 bg-white rounded-xl shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <BookOpen className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Course Planning</h3>
            <p className="text-gray-600 text-sm">
              Get a semester-by-semester breakdown of required courses for your major
            </p>
          </div>

          <div className="text-center p-6 bg-white rounded-xl shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Calendar className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Academic Timeline</h3>
            <p className="text-gray-600 text-sm">
              Visualize your academic journey from freshman to graduation year
            </p>
          </div>

          <div className="text-center p-6 bg-white rounded-xl shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <ChevronRight className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Customization</h3>
            <p className="text-gray-600 text-sm">
              Choose from multiple course options to fulfill requirements
            </p>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
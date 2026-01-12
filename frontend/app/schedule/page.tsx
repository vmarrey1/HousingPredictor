'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import { motion } from 'framer-motion'
import { ArrowLeft, Calendar, BookOpen, Clock, CheckCircle, AlertCircle, Edit, X, Plus, Trash2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

// Configure axios base URL for production
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || ''
if (API_BASE) {
  axios.defaults.baseURL = API_BASE
}

interface Course {
  subject: string
  number: string
  title: string
  units: number
  requirement_type: string
  requirement_name: string
}

interface Semester {
  year: number
  term: string
  courses: Course[]
  units: number
}

interface FourYearPlan {
  major: string
  college: string
  graduation_year: number
  total_units: number
  semesters: Semester[]
  requirements: any
  ai_recommendations?: string
}

axios.defaults.withCredentials = true

export default function SchedulePage() {
  const [plan, setPlan] = useState<FourYearPlan | null>(null)
  const [user, setUser] = useState<{id: string; email: string} | null>(null)
  const [selectedSemester, setSelectedSemester] = useState<Semester | null>(null)
  const [showCourseOptions, setShowCourseOptions] = useState(false)
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)
  const [selectedCourseSemesterIndex, setSelectedCourseSemesterIndex] = useState<number | null>(null)
  const [selectedCourseIndex, setSelectedCourseIndex] = useState<number | null>(null)
  const [courseOptions, setCourseOptions] = useState<any[]>([])
  const [isLoadingOptions, setIsLoadingOptions] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const savedPlan = sessionStorage.getItem('fourYearPlan')
    if (savedPlan) {
      setPlan(JSON.parse(savedPlan))
    } else {
      router.push('/')
    }
    axios.get('/api/auth/me').then(res => setUser(res.data?.user || null)).catch(() => {})
  }, [router])

  const loadCourseOptions = async (course: Course, semesterIndex: number, courseIndex: number) => {
    if (!plan) return
    
    setIsLoadingOptions(true)
    try {
      const response = await axios.post('/api/course-options', {
        major: plan.major,
        requirement_type: course.requirement_type,
        requirement_name: course.requirement_name
      })
      setCourseOptions(response.data.options || [])
      setSelectedCourse(course)
      setSelectedCourseSemesterIndex(semesterIndex)
      setSelectedCourseIndex(courseIndex)
      setShowCourseOptions(true)
    } catch (error) {
      console.error('Error loading course options:', error)
    } finally {
      setIsLoadingOptions(false)
    }
  }

  const removeCourse = (semesterIndex: number, courseIndex: number) => {
    if (!plan) return
    
    const updatedPlan = { ...plan }
    updatedPlan.semesters[semesterIndex].courses.splice(courseIndex, 1)
    updatedPlan.semesters[semesterIndex].units = updatedPlan.semesters[semesterIndex].courses.reduce(
      (sum, course) => sum + course.units, 0
    )
    setPlan(updatedPlan)
    sessionStorage.setItem('fourYearPlan', JSON.stringify(updatedPlan))
  }

  const addCourse = (semesterIndex: number, course: any) => {
    if (!plan) return
    
    const updatedPlan = { ...plan }
    const newCourse = {
      subject: course.subject,
      number: course.number,
      title: course.title,
      units: course.units,
      requirement_type: selectedCourse?.requirement_type || 'elective',
      requirement_name: selectedCourse?.requirement_name || 'Elective'
    }
    
    // If we're replacing a course (selectedCourseIndex is not null)
    if (selectedCourseIndex !== null && selectedCourseSemesterIndex === semesterIndex) {
      updatedPlan.semesters[semesterIndex].courses[selectedCourseIndex] = newCourse
      // Recalculate units
      updatedPlan.semesters[semesterIndex].units = updatedPlan.semesters[semesterIndex].courses.reduce(
        (sum, course) => sum + course.units, 0
      )
    } else {
      updatedPlan.semesters[semesterIndex].courses.push(newCourse)
      updatedPlan.semesters[semesterIndex].units += newCourse.units
    }
    
    setPlan(updatedPlan)
    sessionStorage.setItem('fourYearPlan', JSON.stringify(updatedPlan))
    setShowCourseOptions(false)
    setSelectedCourseIndex(null)
    setSelectedCourseSemesterIndex(null)
  }

  const savePlan = async () => {
    if (!user) {
      router.push('/auth')
      return
    }
    if (!plan) return
    try {
      await axios.post('/api/schedules', { name: `${plan.major} Plan`, data: plan })
      alert('Plan saved')
    } catch (e) {
      console.error(e)
      alert('Failed to save plan')
    }
  }

  if (!plan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading plan...</p>
        </div>
      </div>
    )
  }

  const getTermColor = (term: string) => {
    switch (term) {
      case 'Fall':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'Spring':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'Summer':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getRequirementColor = (type: string) => {
    switch (type) {
      case 'lower_division':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      case 'upper_division':
        return 'bg-purple-50 text-purple-700 border-purple-200'
      case 'breadth':
        return 'bg-green-50 text-green-700 border-green-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const totalUnits = plan.semesters.reduce((sum, semester) => sum + semester.units, 0)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <ArrowLeft className="h-6 w-6 text-gray-600" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{plan.major}</h1>
                <p className="text-gray-600">{plan.college} • Graduating {plan.graduation_year}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Total Units</p>
              <p className="text-2xl font-bold text-primary-600">{totalUnits}</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Plan Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card mb-8"
        >
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <Calendar className="h-6 w-6 text-blue-600" />
              </div>
              <p className="text-sm text-gray-500">Duration</p>
              <p className="font-semibold">4 Years</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <BookOpen className="h-6 w-6 text-green-600" />
              </div>
              <p className="text-sm text-gray-500">Total Courses</p>
              <p className="font-semibold">{plan.semesters.reduce((sum, s) => sum + s.courses.length, 0)}</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
              <p className="text-sm text-gray-500">Total Units</p>
              <p className="font-semibold">{totalUnits}</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <CheckCircle className="h-6 w-6 text-orange-600" />
              </div>
              <p className="text-sm text-gray-500">Semesters</p>
              <p className="font-semibold">{plan.semesters.length}</p>
            </div>
            <div className="md:col-span-4 mt-4 text-center">
              <button onClick={savePlan} className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition">
                Save Plan
              </button>
            </div>
          </div>
        </motion.div>

        {/* AI Recommendations */}
        {plan.ai_recommendations && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200"
          >
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                <span className="text-blue-600 font-bold text-sm">AI</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Academic Advisor Recommendations</h3>
                <p className="text-gray-700 leading-relaxed">{plan.ai_recommendations}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Semesters Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {plan.semesters.map((semester, index) => (
            <motion.div
              key={`${semester.year}-${semester.term}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {semester.term} {semester.year}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {semester.courses.length} courses • {semester.units} units
                  </p>
                </div>
                <span className={`px-3 py-1.5 rounded-full text-xs font-semibold border ${getTermColor(semester.term)}`}>
                  {semester.term}
                </span>
              </div>

              <div className="space-y-3 mb-4">
                {semester.courses.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    <AlertCircle className="h-10 w-10 mx-auto mb-3 text-gray-300" />
                    <p className="text-sm">No courses scheduled for this semester</p>
                  </div>
                ) : (
                  semester.courses.map((course, courseIndex) => (
                    <div
                      key={courseIndex}
                      onClick={(e) => {
                        e.stopPropagation()
                        loadCourseOptions(course, index, courseIndex)
                      }}
                      className="group relative flex items-start justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-2">
                          <p className="font-semibold text-gray-900 text-base">
                            {course.subject} {course.number}
                          </p>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              removeCourse(index, courseIndex)
                            }}
                            className="ml-2 p-1.5 text-red-500 hover:bg-red-50 rounded-md transition-colors opacity-0 group-hover:opacity-100"
                            title="Remove course"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                        <p className="text-sm text-gray-700 mb-2 line-clamp-2">{course.title}</p>
                        <div className="flex items-center space-x-2 flex-wrap">
                          <span className={`px-2.5 py-1 rounded-md text-xs font-medium border ${getRequirementColor(course.requirement_type)}`}>
                            {course.requirement_name}
                          </span>
                          <span className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded">
                            {course.units} units
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          loadCourseOptions(course, index, courseIndex)
                        }}
                        className="ml-3 p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                        title="Change course"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                    </div>
                  ))
                )}
              </div>
              
              {/* Add Course Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedCourse({
                    subject: '',
                    number: '',
                    title: '',
                    units: 0,
                    requirement_type: 'elective',
                    requirement_name: 'Elective'
                  })
                  setSelectedCourseSemesterIndex(index)
                  setSelectedCourseIndex(null)
                  setCourseOptions([])
                  setShowCourseOptions(true)
                }}
                className="w-full flex items-center justify-center gap-2 p-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50 transition-colors font-medium"
              >
                <Plus className="h-5 w-5" />
                Add Course
              </button>
            </motion.div>
          ))}
        </div>


        {/* Course Options Modal */}
        {showCourseOptions && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={() => setShowCourseOptions(false)}>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl max-w-3xl w-full max-h-[85vh] overflow-hidden flex flex-col shadow-2xl"
            >
              <div className="p-6 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Course Selection</h2>
                    <p className="text-gray-700 mt-1.5">
                      {selectedCourse?.requirement_name && selectedCourse.subject ? 
                        `Alternative courses for ${selectedCourse.requirement_name}` : 
                        selectedCourseIndex !== null ? 
                          'Select a replacement course' : 
                          'Add a new course'}
                    </p>
                  </div>
                  <button
                    onClick={() => setShowCourseOptions(false)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white rounded-lg transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              <div className="p-6 overflow-y-auto flex-1">
                {isLoadingOptions ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading course options...</p>
                  </div>
                ) : courseOptions.length > 0 ? (
                  <div className="grid grid-cols-1 gap-3">
                    {courseOptions.map((option, index) => (
                      <div
                        key={index}
                        onClick={() => {
                          if (selectedCourseSemesterIndex !== null) {
                            addCourse(selectedCourseSemesterIndex, option)
                          }
                        }}
                        className="group p-4 border-2 border-gray-200 rounded-lg hover:border-blue-400 hover:shadow-md cursor-pointer transition-all bg-white"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-2">
                              <p className="font-bold text-lg text-gray-900">
                                {option.subject} {option.number}
                              </p>
                              <span className="px-2.5 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded">
                                {option.units} units
                              </span>
                            </div>
                            <p className="text-sm text-gray-700 mb-3 line-clamp-2">{option.title}</p>
                            {option.terms_offered && (
                              <p className="text-xs text-gray-500">
                                Offered: {option.terms_offered}
                              </p>
                            )}
                          </div>
                          <button className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm">
                            {selectedCourseIndex !== null ? 'Replace' : 'Add'}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600 font-medium">No course options available</p>
                    <p className="text-sm text-gray-500 mt-2">Please try selecting a different requirement</p>
                  </div>
                )}
              </div>

              <div className="p-6 border-t bg-gray-50 flex justify-end">
                <button
                  onClick={() => setShowCourseOptions(false)}
                  className="px-6 py-2.5 text-gray-700 hover:text-gray-900 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </main>
    </div>
  )
}

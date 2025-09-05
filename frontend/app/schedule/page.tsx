'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, Calendar, BookOpen, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

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

export default function SchedulePage() {
  const [plan, setPlan] = useState<FourYearPlan | null>(null)
  const [selectedSemester, setSelectedSemester] = useState<Semester | null>(null)
  const [showCourseOptions, setShowCourseOptions] = useState(false)
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)
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
  }, [router])

  const loadCourseOptions = async (course: Course) => {
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
    
    updatedPlan.semesters[semesterIndex].courses.push(newCourse)
    updatedPlan.semesters[semesterIndex].units += newCourse.units
    setPlan(updatedPlan)
    sessionStorage.setItem('fourYearPlan', JSON.stringify(updatedPlan))
    setShowCourseOptions(false)
  }

  if (!plan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your plan...</p>
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
              className="card hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedSemester(semester)}
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {semester.term} {semester.year}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {semester.courses.length} courses • {semester.units} units
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getTermColor(semester.term)}`}>
                  {semester.term}
                </span>
              </div>

              <div className="space-y-2">
                {semester.courses.map((course, courseIndex) => (
                  <div
                    key={courseIndex}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {course.subject} {course.number}
                      </p>
                      <p className="text-sm text-gray-600 truncate">{course.title}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`px-2 py-1 rounded text-xs font-medium border ${getRequirementColor(course.requirement_type)}`}>
                          {course.requirement_name}
                        </span>
                        <span className="text-xs text-gray-500">{course.units} units</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => loadCourseOptions(course)}
                        disabled={isLoadingOptions}
                        className="px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 border border-blue-200 rounded hover:bg-blue-50 transition-colors disabled:opacity-50"
                      >
                        {isLoadingOptions ? 'Loading...' : 'Options'}
                      </button>
                      <button
                        onClick={() => removeCourse(index, courseIndex)}
                        className="px-2 py-1 text-xs font-medium text-red-600 hover:text-red-800 border border-red-200 rounded hover:bg-red-50 transition-colors"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
                
                {/* Add Course Button */}
                <button
                  onClick={() => {
                    setSelectedCourse({
                      subject: '',
                      number: '',
                      title: '',
                      units: 0,
                      requirement_type: 'elective',
                      requirement_name: 'Elective'
                    })
                    setCourseOptions([])
                    setShowCourseOptions(true)
                  }}
                  className="w-full p-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-gray-400 hover:text-gray-600 transition-colors"
                >
                  + Add Course
                </button>
              </div>

              {semester.courses.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <AlertCircle className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p>No courses scheduled</p>
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Semester Detail Modal */}
        {selectedSemester && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            >
              <div className="p-6 border-b">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-gray-900">
                    {selectedSemester.term} {selectedSemester.year}
                  </h2>
                  <button
                    onClick={() => setSelectedSemester(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
                <p className="text-gray-600 mt-1">
                  {selectedSemester.courses.length} courses • {selectedSemester.units} units
                </p>
              </div>

              <div className="p-6">
                <div className="space-y-4">
                  {selectedSemester.courses.map((course, index) => (
                    <div
                      key={index}
                      className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">
                            {course.subject} {course.number}
                          </h3>
                          <p className="text-gray-600 mt-1">{course.title}</p>
                          <div className="flex items-center space-x-2 mt-2">
                            <span className={`px-2 py-1 rounded text-xs font-medium border ${getRequirementColor(course.requirement_type)}`}>
                              {course.requirement_name}
                            </span>
                            <span className="text-xs text-gray-500">{course.units} units</span>
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            setSelectedCourse(course)
                            setShowCourseOptions(true)
                          }}
                          className="ml-4 px-3 py-1 text-xs font-medium text-primary-600 hover:text-primary-700 border border-primary-200 rounded hover:bg-primary-50 transition-colors"
                        >
                          Options
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {/* Course Options Modal */}
        {showCourseOptions && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            >
              <div className="p-6 border-b">
                <h2 className="text-xl font-bold text-gray-900">Course Options</h2>
                <p className="text-gray-600 mt-1">
                  {selectedCourse?.requirement_name ? `Alternative courses for ${selectedCourse.requirement_name}` : 'Add a new course'}
                </p>
              </div>

              <div className="p-6">
                <div className="space-y-3">
                  {courseOptions.length > 0 ? (
                    courseOptions.map((option, index) => (
                      <div
                        key={index}
                        onClick={() => {
                          if (selectedSemester) {
                            addCourse(plan.semesters.findIndex(s => s === selectedSemester), option)
                          }
                        }}
                        className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">
                              {option.subject} {option.number}
                            </p>
                            <p className="text-sm text-gray-600 mt-1">{option.title}</p>
                            <div className="flex items-center space-x-2 mt-2">
                              <span className="text-xs text-gray-500">{option.units} units</span>
                              {option.terms_offered && (
                                <span className="text-xs text-gray-500">• {option.terms_offered}</span>
                              )}
                            </div>
                          </div>
                          <button className="px-3 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 border border-blue-200 rounded hover:bg-blue-50 transition-colors">
                            Add
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <p>No alternative courses available</p>
                      <p className="text-sm mt-1">You can still add custom courses</p>
                    </div>
                  )}
                </div>

                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    onClick={() => setShowCourseOptions(false)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </main>
    </div>
  )
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card, Button } from '@/components/ui';
import { hub3660Api, type Course } from '@/lib/hub3660';
import { useAuth } from '@/lib/auth';

interface CourseCatalogProps {
  onCourseSelect?: (course: Course) => void;
}

export default function CourseCatalog({ onCourseSelect }: CourseCatalogProps) {
  const [courses, setCourses] = useState<Course[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [priceFilter, setPriceFilter] = useState<'all' | 'free' | 'paid'>('all');
  const [enrollmentFilter, setEnrollmentFilter] = useState<'all' | 'enrolled' | 'not-enrolled'>('all');
  
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    filterCourses();
  }, [courses, searchTerm, priceFilter, enrollmentFilter, user]);

  const loadCourses = async () => {
    try {
      setLoading(true);
      setError(null);
      const coursesData = await hub3660Api.getCourses();
      setCourses(coursesData);
    } catch (err) {
      console.error('Failed to load courses:', err);
      setError('Failed to load courses. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filterCourses = useCallback(() => {
    let filtered = courses;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(course =>
        course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.instructor_name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Price filter
    if (priceFilter === 'free') {
      filtered = filtered.filter(course => parseFloat(course.price) === 0);
    } else if (priceFilter === 'paid') {
      filtered = filtered.filter(course => parseFloat(course.price) > 0);
    }

    // Enrollment filter
    if (user) {
      if (enrollmentFilter === 'enrolled') {
        filtered = filtered.filter(course => course.is_enrolled);
      } else if (enrollmentFilter === 'not-enrolled') {
        filtered = filtered.filter(course => !course.is_enrolled);
      }
    }

    setFilteredCourses(filtered);
  }, [courses, searchTerm, priceFilter, enrollmentFilter, user]);

  const formatPrice = (price: string, currency: string) => {
    const numPrice = parseFloat(price);
    if (numPrice === 0) {
      return 'Free';
    }
    return `${currency} ${numPrice.toFixed(2)}`;
  };

  const getEnrollmentStatusBadge = (course: Course) => {
    if (!user) return null;

    if (course.is_enrolled) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Enrolled
        </span>
      );
    }

    if (course.enrollment_status === 'pending') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Pending
        </span>
      );
    }

    return null;
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading courses...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card>
          <div className="p-6 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={loadCourses}>Try Again</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">Course Catalog</h1>
        
        {/* Search and Filters */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
                Search Courses
              </label>
              <input
                type="text"
                id="search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by title, description, or instructor..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Price Filter */}
            <div>
              <label htmlFor="price-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Price
              </label>
              <select
                id="price-filter"
                value={priceFilter}
                onChange={(e) => setPriceFilter(e.target.value as 'all' | 'free' | 'paid')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Courses</option>
                <option value="free">Free Courses</option>
                <option value="paid">Paid Courses</option>
              </select>
            </div>

            {/* Enrollment Filter */}
            {user && (
              <div>
                <label htmlFor="enrollment-filter" className="block text-sm font-medium text-gray-700 mb-2">
                  Enrollment
                </label>
                <select
                  id="enrollment-filter"
                  value={enrollmentFilter}
                  onChange={(e) => setEnrollmentFilter(e.target.value as 'all' | 'enrolled' | 'not-enrolled')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Courses</option>
                  <option value="enrolled">My Courses</option>
                  <option value="not-enrolled">Available Courses</option>
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Results count */}
        <p className="text-gray-600 mb-6">
          Showing {filteredCourses.length} of {courses.length} courses
        </p>
      </div>

      {/* Course Grid */}
      {filteredCourses.length === 0 ? (
        <Card>
          <div className="p-12 text-center">
            <p className="text-gray-500 text-lg">No courses found matching your criteria.</p>
            <Button 
              onClick={() => {
                setSearchTerm('');
                setPriceFilter('all');
                setEnrollmentFilter('all');
              }}
              className="mt-4"
            >
              Clear Filters
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <Card key={course.id} className="h-full flex flex-col">
              <div className="p-6 flex-1 flex flex-col">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-xl font-semibold text-gray-900 line-clamp-2">
                    {course.title}
                  </h3>
                  {getEnrollmentStatusBadge(course)}
                </div>
                
                <p className="text-gray-600 text-sm mb-4 flex-1 line-clamp-3">
                  {course.description}
                </p>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Instructor:</span>
                    <span className="font-medium text-gray-900">{course.instructor_name}</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Students:</span>
                    <span className="font-medium text-gray-900">{course.enrollment_count}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500 text-sm">Price:</span>
                    <span className="font-bold text-lg text-blue-600">
                      {formatPrice(course.price, course.currency)}
                    </span>
                  </div>
                </div>
                
                <Button
                  onClick={() => {
                    if (onCourseSelect) {
                      onCourseSelect(course);
                    } else {
                      router.push(`/hub3660/courses/${course.id}`);
                    }
                  }}
                  className="w-full"
                  variant={course.is_enrolled ? 'secondary' : 'primary'}
                >
                  {course.is_enrolled ? 'View Course' : 'Learn More'}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
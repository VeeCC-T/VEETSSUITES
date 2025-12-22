'use client';

import React, { useState } from 'react';
import { CourseCatalog, CourseDetail } from '@/components/hub3660';
import { type Course } from '@/lib/hub3660';

export default function Hub3660Page() {
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);

  const handleCourseSelect = (course: Course) => {
    setSelectedCourse(course);
  };

  const handleBackToCatalog = () => {
    setSelectedCourse(null);
  };

  const handleEnroll = (course: Course) => {
    // This will be implemented in task 16.2 (enrollment checkout flow)
    console.log('Enrollment flow for course:', course.title);
    // For now, just show an alert
    alert(`Enrollment flow for "${course.title}" will be implemented in the next task.`);
  };

  if (selectedCourse) {
    return (
      <CourseDetail
        course={selectedCourse}
        onBack={handleBackToCatalog}
        onEnroll={handleEnroll}
      />
    );
  }

  return (
    <CourseCatalog onCourseSelect={handleCourseSelect} />
  );
}

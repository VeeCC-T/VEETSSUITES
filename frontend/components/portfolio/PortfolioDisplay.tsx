'use client';

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Portfolio } from '@/lib/portfolio/api';

interface PortfolioDisplayProps {
  portfolio: Portfolio;
  isOwner?: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
}

export function PortfolioDisplay({ 
  portfolio, 
  isOwner = false, 
  onEdit, 
  onDelete 
}: PortfolioDisplayProps) {
  const { user, parsed_content, cv_file_url, is_public, created_at, updated_at } = portfolio;

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // Render parsed content sections
  const renderParsedContent = () => {
    if (!parsed_content || parsed_content.error) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-gray-500">
            {parsed_content?.error ? 'Failed to parse CV content' : 'CV content not available'}
          </p>
          {cv_file_url && (
            <div className="mt-4">
              <Button
                variant="secondary"
                onClick={() => cv_file_url && window.open(cv_file_url, '_blank')}
              >
                View Original PDF
              </Button>
            </div>
          )}
        </div>
      );
    }

    // If parsed_content has structured data, render it
    const sections = [];

    // Personal Information
    if (parsed_content.personal_info) {
      sections.push(
        <div key="personal" className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Personal Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(parsed_content.personal_info).map(([key, value]) => (
              <div key={key}>
                <dt className="text-sm font-medium text-gray-500 capitalize">
                  {key.replace('_', ' ')}
                </dt>
                <dd className="text-sm text-gray-900">{value as string}</dd>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Experience
    if (parsed_content.experience && Array.isArray(parsed_content.experience)) {
      sections.push(
        <div key="experience" className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Experience</h3>
          <div className="space-y-4">
            {parsed_content.experience.map((exp: any, index: number) => (
              <div key={index} className="border-l-2 border-blue-200 pl-4">
                <h4 className="font-medium text-gray-900">{exp.title || exp.position}</h4>
                {exp.company && (
                  <p className="text-sm text-gray-600">{exp.company}</p>
                )}
                {exp.duration && (
                  <p className="text-xs text-gray-500">{exp.duration}</p>
                )}
                {exp.description && (
                  <p className="text-sm text-gray-700 mt-1">{exp.description}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Education
    if (parsed_content.education && Array.isArray(parsed_content.education)) {
      sections.push(
        <div key="education" className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Education</h3>
          <div className="space-y-4">
            {parsed_content.education.map((edu: any, index: number) => (
              <div key={index} className="border-l-2 border-green-200 pl-4">
                <h4 className="font-medium text-gray-900">{edu.degree || edu.qualification}</h4>
                {edu.institution && (
                  <p className="text-sm text-gray-600">{edu.institution}</p>
                )}
                {edu.year && (
                  <p className="text-xs text-gray-500">{edu.year}</p>
                )}
                {edu.grade && (
                  <p className="text-sm text-gray-700 mt-1">Grade: {edu.grade}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Skills
    if (parsed_content.skills) {
      const skillsArray = Array.isArray(parsed_content.skills) 
        ? parsed_content.skills 
        : parsed_content.skills.split(',').map((s: string) => s.trim());
      
      sections.push(
        <div key="skills" className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Skills</h3>
          <div className="flex flex-wrap gap-2">
            {skillsArray.map((skill: string, index: number) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      );
    }

    // Raw text fallback
    if (sections.length === 0 && parsed_content.raw_text) {
      sections.push(
        <div key="raw" className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">CV Content</h3>
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
              {parsed_content.raw_text}
            </pre>
          </div>
        </div>
      );
    }

    return sections.length > 0 ? sections : (
      <div className="text-center py-8">
        <p className="text-gray-500">No content available to display</p>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <div className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {user.first_name} {user.last_name}
              </h1>
              <p className="text-gray-600 mt-1">{user.email}</p>
              <div className="flex items-center mt-2 space-x-4 text-sm text-gray-500">
                <span>Updated: {formatDate(updated_at)}</span>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  is_public 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {is_public ? 'Public' : 'Private'}
                </span>
              </div>
            </div>
            
            {isOwner && (
              <div className="flex space-x-2">
                {onEdit && (
                  <Button variant="secondary" onClick={onEdit}>
                    Edit
                  </Button>
                )}
                {onDelete && (
                  <Button variant="danger" onClick={onDelete}>
                    Delete
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* CV Content */}
      <Card>
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">CV Content</h2>
            {cv_file_url && (
              <Button
                variant="secondary"
                onClick={() => cv_file_url && window.open(cv_file_url, '_blank')}
              >
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download PDF
              </Button>
            )}
          </div>
          
          {renderParsedContent()}
        </div>
      </Card>

      {/* Public URL */}
      {is_public && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Public Portfolio</h3>
            <p className="text-sm text-gray-600 mb-3">
              Your portfolio is publicly accessible at:
            </p>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={`${window.location.origin}${portfolio.public_url}`}
                readOnly
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm bg-gray-50"
              />
              <Button
                variant="secondary"
                onClick={() => {
                  navigator.clipboard.writeText(`${window.location.origin}${portfolio.public_url}`);
                }}
              >
                Copy
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
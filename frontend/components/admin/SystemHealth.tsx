'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { adminApi, SystemHealth as SystemHealthType } from '../../lib/admin/api';
import { HEALTH_STATUS_MAP } from '../../lib/admin/types';

export const SystemHealth: React.FC = () => {
  const [health, setHealth] = useState<SystemHealthType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    loadHealth();
    const interval = setInterval(loadHealth, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadHealth = async () => {
    try {
      setLoading(true);
      const data = await adminApi.getSystemHealth();
      setHealth(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError('Failed to load system health');
      console.error('Health check error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusInfo = (status: string) => {
    return HEALTH_STATUS_MAP[status] || HEALTH_STATUS_MAP.unknown;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading && !health) {
    return (
      <Card className="p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">System Health</h2>
          <Button onClick={loadHealth} disabled={loading} variant="outline">
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>

        {error ? (
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={loadHealth}>Retry</Button>
          </div>
        ) : health ? (
          <div className="space-y-6">
            {/* Overall Status */}
            <div className="flex items-center space-x-4">
              <div className={`text-2xl ${getStatusInfo(health.status).color}`}>
                {getStatusInfo(health.status).icon}
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  System Status: <span className={getStatusInfo(health.status).color}>
                    {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
                  </span>
                </h3>
                <p className="text-sm text-gray-600">
                  Last updated: {formatTimestamp(health.timestamp)}
                </p>
                {lastUpdated && (
                  <p className="text-xs text-gray-500">
                    Refreshed: {lastUpdated.toLocaleTimeString()}
                  </p>
                )}
              </div>
            </div>

            {/* Health Checks */}
            <div className="grid gap-4">
              {Object.entries(health.checks).map(([checkName, checkData]) => {
                const statusInfo = getStatusInfo(checkData.status);
                return (
                  <div key={checkName} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className={`text-lg ${statusInfo.color}`}>
                          {statusInfo.icon}
                        </span>
                        <div>
                          <h4 className="font-medium text-gray-900 capitalize">
                            {checkName.replace(/_/g, ' ')}
                          </h4>
                          {checkData.message && (
                            <p className="text-sm text-gray-600">{checkData.message}</p>
                          )}
                        </div>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        checkData.status === 'healthy' ? 'bg-green-100 text-green-800' :
                        checkData.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                        checkData.status === 'unhealthy' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {checkData.status}
                      </span>
                    </div>
                    
                    {/* System Resources Details */}
                    {checkName === 'system_resources' && checkData.cpu_percent !== undefined && (
                      <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">CPU:</span>
                          <span className="ml-1 font-medium">{checkData.cpu_percent.toFixed(1)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Memory:</span>
                          <span className="ml-1 font-medium">{checkData.memory_percent.toFixed(1)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Disk:</span>
                          <span className="ml-1 font-medium">{checkData.disk_percent.toFixed(1)}%</span>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ) : null}
      </Card>
    </div>
  );
};
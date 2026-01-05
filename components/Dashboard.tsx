'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, TrendingUp, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import Link from 'next/link';
import { formatDateTime } from '@/lib/utils';

interface DashboardStats {
  totalInterviews: number;
  bottlenecksIdentified: number;
  opportunitiesFound: number;
  completedAnalyses: number;
}

interface RecentActivity {
  id: string;
  type: 'interview' | 'analysis' | 'scan';
  title: string;
  timestamp: Date;
  status: string;
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalInterviews: 0,
    bottlenecksIdentified: 0,
    opportunitiesFound: 0,
    completedAnalyses: 0,
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch actual data from API
    // For now, using mock data
    setStats({
      totalInterviews: 0,
      bottlenecksIdentified: 0,
      opportunitiesFound: 0,
      completedAnalyses: 0,
    });
    setRecentActivity([]);
    setLoading(false);
  }, []);

  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to your AI-powered workflow automation platform
          </p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link href="/interview">
              <Plus className="mr-2 h-4 w-4" />
              New Interview
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Interviews
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalInterviews}</div>
            <p className="text-xs text-muted-foreground">
              Workflow analysis sessions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Bottlenecks Identified
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.bottlenecksIdentified}</div>
            <p className="text-xs text-muted-foreground">
              Pain points discovered
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Opportunities Found
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.opportunitiesFound}</div>
            <p className="text-xs text-muted-foreground">
              Automation possibilities
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Completed Analyses
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completedAnalyses}</div>
            <p className="text-xs text-muted-foreground">
              Full workflow reports
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Start exploring your workflow automation opportunities
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <Button variant="outline" className="h-20 flex-col" asChild>
            <Link href="/interview">
              <Plus className="mb-2 h-6 w-6" />
              New Interview
            </Link>
          </Button>
          <Button variant="outline" className="h-20 flex-col" asChild>
            <Link href="/security">
              <AlertTriangle className="mb-2 h-6 w-6" />
              Security Scan
            </Link>
          </Button>
          <Button variant="outline" className="h-20 flex-col" asChild>
            <Link href="/context-studio">
              <TrendingUp className="mb-2 h-6 w-6" />
              Context Engineering
            </Link>
          </Button>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Your latest workflow analysis activities
          </CardDescription>
        </CardHeader>
        <CardContent>
          {recentActivity.length === 0 ? (
            <div className="py-12 text-center">
              <p className="text-muted-foreground">
                No recent activity. Start by creating your first interview!
              </p>
              <Button asChild className="mt-4">
                <Link href="/interview">
                  <Plus className="mr-2 h-4 w-4" />
                  Start Interview
                </Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center justify-between border-b pb-4 last:border-0"
                >
                  <div>
                    <p className="font-medium">{activity.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDateTime(activity.timestamp)}
                    </p>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {activity.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

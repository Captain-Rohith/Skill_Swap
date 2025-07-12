
import { useUser, useAuth } from '@clerk/clerk-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SwapRequest, User } from '@/types';
import { swapApi, userApi } from '@/lib/api';
import { useEffect, useState } from 'react';
import { CheckCircle, XCircle, Clock, User as UserIcon, Bell } from 'lucide-react';
import { toast } from 'sonner';
import { OngoingSwaps } from '@/components/OngoingSwaps';

export const Dashboard = () => {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [swapRequests, setSwapRequests] = useState<SwapRequest[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadDashboardData = async () => {
    if (!user || !getToken) return;

    try {
      setIsLoading(true);
      const token = await getToken();
      
      // Load swap requests
      const requests = await swapApi.getSwapRequests(token);
      console.log('Dashboard: Raw swap requests from API:', requests);
      
              // Transform backend data to frontend format
        const transformedRequests = requests.map((req: any) => ({
          id: req.id,
          fromUserId: req.from_user_id,
          toUserId: req.to_user_id,
          fromUserName: req.from_user_name,
          toUserName: req.to_user_name,
          skillOffered: req.skill_offered,
          skillWanted: req.skill_wanted,
          message: req.message,
          status: req.status,
          closedCount: req.closed_count || 0,
          createdAt: req.created_at,
          updatedAt: req.updated_at
        }));
      
      console.log('Dashboard: Transformed swap requests:', transformedRequests);
      console.log('Dashboard: Current user ID:', user.id);
      setSwapRequests(transformedRequests);
      
      // Load users for display
      const allUsers = await userApi.searchUsers(token);
      const transformedUsers = allUsers.map((user: any) => ({
        id: user.id,
        name: user.name,
        email: user.email || '',
        location: user.location,
        profilePicture: user.profile_picture,
        skillsOffered: user.skills_offered || [],
        skillsWanted: user.skills_wanted || [],
        availability: user.availability || '',
        isPublic: user.is_public || true,
        isActive: user.is_active || true,
        isBanned: user.is_banned || false,
        createdAt: user.created_at || new Date().toISOString(),
        clerkId: user.id
      }));
      
      setUsers(transformedUsers);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [user, getToken]);

  const handleSwapResponse = async (requestId: string, status: 'accepted' | 'rejected') => {
    if (!getToken) return;

    try {
      const token = await getToken();
      
      if (status === 'accepted') {
        await swapApi.acceptSwapRequest(token, requestId);
      } else {
        await swapApi.rejectSwapRequest(token, requestId);
      }
      
      setSwapRequests(prev => 
        prev.map(req => 
          req.id === requestId ? { ...req, status } : req
        )
      );
      
      toast.success(`Swap request ${status} successfully!`);
    } catch (error) {
      console.error('Failed to update swap request:', error);
      toast.error('Failed to update swap request');
    }
  };

  const handleSwapUpdate = () => {
    // Reload dashboard data when swaps are updated
    loadDashboardData();
  };

  const handleDeleteSwap = async (swapId: string) => {
    if (!getToken) return;

    try {
      const token = await getToken();
      await swapApi.deleteSwap(token, swapId);
      toast.success('Swap deleted successfully!');
      loadDashboardData();
    } catch (error) {
      console.error('Failed to delete swap:', error);
      toast.error('Failed to delete swap');
    }
  };

  const getUserById = (id: string) => users.find(u => u.id === id);

  const pendingRequests = swapRequests.filter(req => req.status === 'pending' && req.toUserId === user?.id);
  const sentRequests = swapRequests.filter(req => req.fromUserId === user?.id);

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <p>Please sign in to view your dashboard.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Dashboard</h1>
        <p className="text-muted-foreground">Manage your skill swaps and profile</p>
        
        {pendingRequests.length > 0 && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-blue-600" />
              <p className="text-blue-800 font-medium">
                You have {pendingRequests.length} pending swap request{pendingRequests.length !== 1 ? 's' : ''} waiting for your response!
              </p>
            </div>
          </div>
        )}
      </div>

      <Tabs defaultValue="requests" className="space-y-6">
        <TabsList>
          <TabsTrigger value="requests">
            Swap Requests
            {pendingRequests.length > 0 && (
              <Badge variant="destructive" className="ml-2">
                {pendingRequests.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="ongoing">Ongoing Swaps</TabsTrigger>
          <TabsTrigger value="profile">My Profile</TabsTrigger>
        </TabsList>

        <TabsContent value="requests" className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Pending Requests ({pendingRequests.length})
                </CardTitle>
                <CardDescription>Requests waiting for your response</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {pendingRequests.length === 0 ? (
                  <p className="text-muted-foreground text-center py-4">No pending requests</p>
                ) : (
                  pendingRequests.map(request => {
                    const fromUser = getUserById(request.fromUserId);
                    return (
                      <div key={request.id} className="border rounded-lg p-4 space-y-3 bg-blue-50 border-blue-200">
                        <div className="flex items-center gap-2">
                          <UserIcon className="h-4 w-4" />
                          <span className="font-medium">{fromUser?.name || 'Unknown User'}</span>
                          <Badge variant="secondary">New Request</Badge>
                        </div>
                        <div className="space-y-2">
                          <p className="text-sm"><strong>Offering:</strong> {request.skillOffered}</p>
                          <p className="text-sm"><strong>Wants:</strong> {request.skillWanted}</p>
                          <p className="text-sm text-muted-foreground">{request.message}</p>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleSwapResponse(request.id, 'accepted')}
                          >
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Accept
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSwapResponse(request.id, 'rejected')}
                          >
                            <XCircle className="h-4 w-4 mr-1" />
                            Decline
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteSwap(request.id)}
                          >
                            <XCircle className="h-4 w-4 mr-1" />
                            Delete
                          </Button>
                        </div>
                      </div>
                    );
                  })
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Sent Requests ({sentRequests.length})</CardTitle>
                <CardDescription>Requests you've sent to others</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {sentRequests.length === 0 ? (
                  <p className="text-muted-foreground text-center py-4">No sent requests</p>
                ) : (
                  sentRequests.map(request => {
                    const toUser = getUserById(request.toUserId);
                    return (
                      <div key={request.id} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <UserIcon className="h-4 w-4" />
                            <span className="font-medium">{toUser?.name || 'Unknown User'}</span>
                          </div>
                          <Badge variant={
                            request.status === 'accepted' ? 'default' :
                            request.status === 'rejected' ? 'destructive' : 'secondary'
                          }>
                            {request.status}
                          </Badge>
                        </div>
                        <div className="space-y-1">
                          <p className="text-sm"><strong>Offering:</strong> {request.skillOffered}</p>
                          <p className="text-sm"><strong>Wants:</strong> {request.skillWanted}</p>
                          <p className="text-sm text-muted-foreground">{request.message}</p>
                        </div>
                      </div>
                    );
                  })
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="ongoing">
          <OngoingSwaps
            swapRequests={swapRequests}
            currentUserId={user?.id || ''}
            onSwapUpdate={handleSwapUpdate}
          />
        </TabsContent>

        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile Management</CardTitle>
              <CardDescription>Update your profile and skills</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Profile editing functionality coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

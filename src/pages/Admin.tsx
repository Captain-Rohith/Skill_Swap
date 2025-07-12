import { useUser, useAuth } from '@clerk/clerk-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useState, useEffect } from 'react';
import { User, SwapRequest, AdminAction } from '@/types';
import { userApi, swapApi, adminApi } from '@/lib/api';
import { toast } from 'sonner';
import { Shield, Users, MessageSquare, BarChart3, Ban, CheckCircle, Download, Send, AlertTriangle } from 'lucide-react';

export const Admin = () => {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [swapRequests, setSwapRequests] = useState<SwapRequest[]>([]);
  const [adminActions, setAdminActions] = useState<AdminAction[]>([]);
  const [platformMessage, setPlatformMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const isAdmin = user?.emailAddresses[0]?.emailAddress === 'srivathsasmurthy2005@gmail.com';

  useEffect(() => {
    const loadAdminData = async () => {
      if (!isAdmin || !getToken) return;

      try {
        setIsLoading(true);
        const token = await getToken();
        
        // Load users
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
        
        // Load swap requests - get all swaps for admin monitoring
        const requests = await adminApi.getAllSwaps(token);
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
          createdAt: req.created_at,
          updatedAt: req.updated_at
        }));
        setSwapRequests(transformedRequests);
        
        // For now, we'll use empty admin actions since backend doesn't have this yet
        setAdminActions([]);
      } catch (error) {
        console.error('Failed to load admin data:', error);
        toast.error('Failed to load admin data');
      } finally {
        setIsLoading(false);
      }
    };

    loadAdminData();
  }, [isAdmin, getToken]);

  const handleBanUser = async (userId: string, isBanned: boolean) => {
    if (!getToken) return;

    try {
      const token = await getToken();
      // For now, just update the local state since backend doesn't have ban functionality yet
      const updatedUser = { ...users.find(u => u.id === userId)!, isBanned };
      setUsers(prev => prev.map(u => u.id === userId ? updatedUser : u));
      
      const action: Omit<AdminAction, 'id' | 'createdAt'> = {
        adminId: user!.id,
        type: isBanned ? 'user_banned' : 'user_unbanned',
        targetId: userId,
        reason: isBanned ? 'Policy violation' : 'Ban lifted',
        timestamp: new Date().toISOString()
      };
      
      setAdminActions(prev => [{ ...action, id: Date.now().toString(), createdAt: new Date().toISOString() }, ...prev]);
      
      toast.success(`User ${isBanned ? 'banned' : 'unbanned'} successfully`);
    } catch (error) {
      console.error('Failed to ban/unban user:', error);
      toast.error('Failed to ban/unban user');
    }
  };

  const handleRejectSkill = async (userId: string, skill: string) => {
    if (!getToken) return;

    try {
      const targetUser = users.find(u => u.id === userId);
      if (!targetUser) return;

      const updatedUser = {
        ...targetUser,
        skillsOffered: targetUser.skillsOffered.filter(s => s !== skill)
      };
      
      // For now, just update the local state since backend doesn't have skill rejection yet
      setUsers(prev => prev.map(u => u.id === userId ? updatedUser : u));
      
      const action: Omit<AdminAction, 'id' | 'createdAt'> = {
        adminId: user!.id,
        type: 'delete_skill' as any,
        targetId: userId,
        reason: `Rejected inappropriate skill: ${skill}`,
        timestamp: new Date().toISOString()
      };
      
      setAdminActions(prev => [{ ...action, id: Date.now().toString(), createdAt: new Date().toISOString() }, ...prev]);
      
      toast.success(`Skill "${skill}" rejected and removed`);
    } catch (error) {
      console.error('Failed to reject skill:', error);
      toast.error('Failed to reject skill');
    }
  };

  const sendPlatformMessage = async () => {
    if (!platformMessage.trim() || !getToken) return;

    try {
      const token = await getToken();
      await adminApi.sendPlatformMessage(token, platformMessage);
      
      const action: Omit<AdminAction, 'id' | 'createdAt'> = {
        adminId: user!.id,
        type: 'delete_skill' as any, // Reusing existing type for demo
        targetId: 'all_users',
        reason: `Platform message: ${platformMessage}`,
        timestamp: new Date().toISOString()
      };
      
      setAdminActions(prev => [{ ...action, id: Date.now().toString(), createdAt: new Date().toISOString() }, ...prev]);
      
      toast.success('Platform-wide message sent to all users');
      setPlatformMessage('');
    } catch (error) {
      console.error('Failed to send platform message:', error);
      toast.error('Failed to send platform message');
    }
  };

  const exportCSV = (data: any[], filename: string) => {
    const csv = [
      Object.keys(data[0]).join(','),
      ...data.map(row => Object.values(row).join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <p>Please sign in to access the admin panel.</p>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <Card>
          <CardContent className="text-center py-12">
            <Shield className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
            <p className="text-muted-foreground">You don't have permission to access the admin panel.</p>
            <p className="text-sm text-muted-foreground mt-2">
              Contact support if you believe this is an error.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  const activeUsers = users.filter(u => !u.isBanned).length;
  const bannedUsers = users.filter(u => u.isBanned).length;
  const pendingSwaps = swapRequests.filter(s => s.status === 'pending').length;
  const completedSwaps = swapRequests.filter(s => s.status === 'accepted').length;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Admin Panel</h1>
        <p className="text-muted-foreground">Monitor and manage the Skill Swap Platform</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Active Users</p>
                <p className="text-2xl font-bold">{activeUsers}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Ban className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Banned Users</p>
                <p className="text-2xl font-bold">{bannedUsers}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <MessageSquare className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Pending Swaps</p>
                <p className="text-2xl font-bold">{pendingSwaps}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Completed Swaps</p>
                <p className="text-2xl font-bold">{completedSwaps}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="users" className="space-y-6">
        <TabsList>
          <TabsTrigger value="users">User Management</TabsTrigger>
          <TabsTrigger value="swaps">Swap Monitoring</TabsTrigger>
          <TabsTrigger value="skills">Skill Moderation</TabsTrigger>
          <TabsTrigger value="messages">Platform Messages</TabsTrigger>
          <TabsTrigger value="actions">Admin Actions</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle>User Management</CardTitle>
              <CardDescription>View and manage user accounts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map(targetUser => (
                  <div key={targetUser.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{targetUser.name}</span>
                        {targetUser.isBanned && <Badge variant="destructive">Banned</Badge>}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {targetUser.email}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Skills: {targetUser.skillsOffered.join(', ')}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Location: {targetUser.location || 'Not specified'}
                      </p>
                    </div>
                    <Button
                      variant={targetUser.isBanned ? "outline" : "destructive"}
                      size="sm"
                      onClick={() => handleBanUser(targetUser.id, !targetUser.isBanned)}
                    >
                      {targetUser.isBanned ? 'Unban' : 'Ban'} User
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skills">
          <Card>
            <CardHeader>
              <CardTitle>Skill Moderation</CardTitle>
              <CardDescription>Review and moderate user skills</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map(targetUser => 
                  targetUser.skillsOffered.map(skill => (
                    <div key={`${targetUser.id}-${skill}`} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <p className="font-medium">{skill}</p>
                        <p className="text-sm text-muted-foreground">by {targetUser.name}</p>
                      </div>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleRejectSkill(targetUser.id, skill)}
                      >
                        <AlertTriangle className="h-4 w-4 mr-1" />
                        Reject Skill
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="messages">
          <Card>
            <CardHeader>
              <CardTitle>Platform Messages</CardTitle>
              <CardDescription>Send platform-wide notifications to all users</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Enter your platform-wide message here..."
                value={platformMessage}
                onChange={(e) => setPlatformMessage(e.target.value)}
                rows={4}
              />
              <Button onClick={sendPlatformMessage} disabled={!platformMessage.trim()}>
                <Send className="h-4 w-4 mr-2" />
                Send Platform Message
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="swaps">
          <Card>
            <CardHeader>
              <CardTitle>Swap Monitoring</CardTitle>
              <CardDescription>Monitor skill swap requests and status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {swapRequests.map(request => {
                  const fromUser = users.find(u => u.id === request.fromUserId);
                  const toUser = users.find(u => u.id === request.toUserId);
                  return (
                    <div key={request.id} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-medium">
                            {fromUser?.name || 'Unknown'} → {toUser?.name || 'Unknown'}
                          </p>
                          <p className="text-sm text-muted-foreground">{request.message}</p>
                        </div>
                        <Badge variant={
                          request.status === 'accepted' ? 'default' :
                          request.status === 'rejected' ? 'destructive' : 'secondary'
                        }>
                          {request.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Created: {new Date(request.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="actions">
          <Card>
            <CardHeader>
              <CardTitle>Admin Actions Log</CardTitle>
              <CardDescription>View all administrative actions taken</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {adminActions.map(action => (
                  <div key={action.id} className="p-4 border rounded-lg">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium capitalize">{action.type.replace('_', ' ')}</p>
                        <p className="text-sm text-muted-foreground">{action.reason}</p>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {new Date(action.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports">
          <Card>
            <CardHeader>
              <CardTitle>Export Reports</CardTitle>
              <CardDescription>Download CSV reports for analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={() => exportCSV(users, 'users_report.csv')}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                Export User Activity Report
              </Button>
              <Button
                onClick={() => exportCSV(swapRequests, 'swaps_report.csv')}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                Export Swap Statistics
              </Button>
              <Button
                onClick={() => exportCSV([], 'feedback_report.csv')}
                className="w-full"
                disabled
              >
                <Download className="h-4 w-4 mr-2" />
                Export Feedback Logs (Coming Soon)
              </Button>
              <Button
                onClick={() => exportCSV(adminActions, 'admin_actions_report.csv')}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                Export Admin Actions
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

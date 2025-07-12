
import { useState, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/clerk-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Bell, CheckCircle, XCircle, User as UserIcon, MessageSquare, Star, Trash2, Eye } from 'lucide-react';
import { Notification } from '@/types';
import { notificationApi, swapApi } from '@/lib/api';
import { toast } from 'sonner';

export const NotificationsDropdown = () => {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadNotifications = async () => {
    if (!user || !getToken) return;
    
    try {
      setLoading(true);
      const token = await getToken();
      const data = await notificationApi.getNotifications(token);
      
      // Transform backend data to frontend format
      const transformedNotifications = data.map((notification: any) => ({
        id: notification.id,
        type: notification.type,
        title: notification.title,
        message: notification.message,
        userId: notification.user_id,
        relatedId: notification.related_id,
        isRead: notification.is_read,
        createdAt: notification.created_at
      }));
      
      setNotifications(transformedNotifications);
    } catch (error) {
      console.error('Failed to load notifications:', error);
      toast.error('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
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
      
      // Remove the notification from the list
      setNotifications(prev => 
        prev.filter(notif => notif.relatedId !== requestId)
      );
      
      toast.success(`Swap request ${status} successfully!`);
    } catch (error) {
      console.error('Failed to respond to swap request:', error);
      toast.error('Failed to respond to swap request');
    }
  };

  const markAsRead = async (notificationId: string) => {
    if (!getToken) return;
    
    try {
      const token = await getToken();
      await notificationApi.markAsRead(token, notificationId);
      
      // Update the notification in the list
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId ? { ...notif, isRead: true } : notif
        )
      );
      
      toast.success('Notification marked as read');
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      toast.error('Failed to mark notification as read');
    }
  };

  const deleteNotification = async (notificationId: string) => {
    if (!getToken) return;
    
    try {
      const token = await getToken();
      await notificationApi.deleteNotification(token, notificationId);
      
      // Remove the notification from the list
      setNotifications(prev => 
        prev.filter(notif => notif.id !== notificationId)
      );
      
      toast.success('Notification deleted');
    } catch (error) {
      console.error('Failed to delete notification:', error);
      toast.error('Failed to delete notification');
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'swap_request':
        return <UserIcon className="h-4 w-4" />;
      case 'platform_message':
        return <MessageSquare className="h-4 w-4" />;
      case 'swap_accepted':
      case 'swap_rejected':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Bell className="h-4 w-4" />;
    }
  };

  const getNotificationBadgeVariant = (type: string) => {
    switch (type) {
      case 'swap_request':
        return 'secondary';
      case 'platform_message':
        return 'default';
      case 'swap_accepted':
        return 'default';
      case 'swap_rejected':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const unreadCount = notifications.filter(n => !n.isRead).length;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-4 w-4" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96" align="end">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Notifications</h3>
            {unreadCount > 0 && (
              <Badge variant="secondary">{unreadCount} unread</Badge>
            )}
          </div>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
              <p className="text-muted-foreground">Loading notifications...</p>
            </div>
          ) : notifications.length === 0 ? (
            <div className="text-center py-8">
              <Bell className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              <p className="text-muted-foreground">No notifications</p>
              <p className="text-sm text-muted-foreground">You're all caught up!</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {notifications.map(notification => (
                <Card 
                  key={notification.id} 
                  className={`border-l-4 ${
                    notification.isRead 
                      ? 'border-muted bg-muted/20' 
                      : 'border-blue-500 bg-blue-50'
                  }`}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getNotificationIcon(notification.type)}
                        <CardTitle className="text-sm">
                          {notification.title}
                        </CardTitle>
                        <Badge 
                          variant={getNotificationBadgeVariant(notification.type)} 
                          className="text-xs"
                        >
                          {notification.type.replace('_', ' ')}
                        </Badge>
                      </div>
                      
                      {/* Action buttons */}
                      <div className="flex gap-1">
                        {!notification.isRead && (
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-6 w-6 p-0"
                            onClick={() => markAsRead(notification.id)}
                            title="Mark as read"
                          >
                            <Eye className="h-3 w-3" />
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                          onClick={() => deleteNotification(notification.id)}
                          title="Delete notification"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="space-y-1">
                      <p className="text-xs text-muted-foreground">{notification.message}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(notification.createdAt).toLocaleString()}
                      </p>
                    </div>
                    
                    {/* Show action buttons for swap requests */}
                    {notification.type === 'swap_request' && notification.relatedId && (
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          className="h-7 text-xs"
                          onClick={() => handleSwapResponse(notification.relatedId!, 'accepted')}
                        >
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Accept
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-7 text-xs"
                          onClick={() => handleSwapResponse(notification.relatedId!, 'rejected')}
                        >
                          <XCircle className="h-3 w-3 mr-1" />
                          Decline
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
};

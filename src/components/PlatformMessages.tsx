import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, Clock } from 'lucide-react';
import { PlatformMessage } from '@/types';
import { notificationApi } from '@/lib/api';
import { toast } from 'sonner';

export const PlatformMessages = () => {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<PlatformMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const loadPlatformMessages = async () => {
    if (!getToken) return;
    
    try {
      setLoading(true);
      const token = await getToken();
      const data = await notificationApi.getPlatformMessages(token);
      
      // Transform backend data to frontend format
      const transformedMessages = data.map((message: any) => ({
        id: message.id,
        message: message.message,
        adminId: message.admin_id,
        adminName: message.admin_name,
        createdAt: message.created_at
      }));
      
      setMessages(transformedMessages);
    } catch (error) {
      console.error('Failed to load platform messages:', error);
      toast.error('Failed to load platform messages');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlatformMessages();
  }, [getToken]);

  if (loading) {
    return (
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
        </CardContent>
      </Card>
    );
  }

  if (messages.length === 0) {
    return null; // Don't show anything if no messages
  }

  return (
    <div className="space-y-4 mb-6">
      <h2 className="text-lg font-semibold flex items-center gap-2">
        <MessageSquare className="h-5 w-5" />
        Platform Messages
      </h2>
      
      {messages.slice(0, 3).map((message) => (
        <Card key={message.id} className="border-blue-200 bg-blue-50">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Message from {message.adminName}
              </CardTitle>
              <Badge variant="secondary" className="text-xs">
                <Clock className="h-3 w-3 mr-1" />
                {new Date(message.createdAt).toLocaleDateString()}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{message.message}</p>
          </CardContent>
        </Card>
      ))}
      
      {messages.length > 3 && (
        <p className="text-xs text-muted-foreground text-center">
          Showing 3 of {messages.length} messages
        </p>
      )}
    </div>
  );
}; 
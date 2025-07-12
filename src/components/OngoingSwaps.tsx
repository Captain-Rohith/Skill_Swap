import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Star, MessageSquare, CheckCircle, Users, Trash2, Phone, Mail } from 'lucide-react';
import { SwapRequest, User } from '@/types';
import { swapApi, userApi } from '@/lib/api';
import { toast } from 'sonner';
import { ContactButtons } from './ContactButtons';

interface OngoingSwapsProps {
  swapRequests: SwapRequest[];
  currentUserId: string;
  onSwapUpdate: () => void;
}

interface FeedbackDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  swapRequest: SwapRequest;
  currentUserId: string;
  onSubmit: () => void;
}

const FeedbackDialog = ({ open, onOpenChange, swapRequest, currentUserId, onSubmit }: FeedbackDialogProps) => {
  const { getToken } = useAuth();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!rating || !getToken) return;
    
    setSubmitting(true);
    try {
      const token = await getToken();
      // Determine which user to rate (the other user in the swap)
      const targetUserId = swapRequest.fromUserId === currentUserId 
        ? swapRequest.toUserId 
        : swapRequest.fromUserId;
      
      // Submit feedback
      await swapApi.submitFeedback(token, swapRequest.id, {
        rating,
        comment,
        toUserId: targetUserId
      });
      
      toast.success('Feedback submitted successfully!');
      onSubmit();
      onOpenChange(false);
      setRating(5);
      setComment('');
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      toast.error('Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  const otherUserName = swapRequest.fromUserId === currentUserId 
    ? swapRequest.toUserName 
    : swapRequest.fromUserName;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Rate {otherUserName}</DialogTitle>
          <DialogDescription>
            How was your experience with this skill swap?
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div>
            <Label>Rating</Label>
            <div className="flex gap-1 mt-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  className={`text-2xl ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <Label htmlFor="comment">Comment (optional)</Label>
            <Textarea
              id="comment"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Share your experience..."
              className="mt-2"
            />
          </div>
          
          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Feedback'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export const OngoingSwaps = ({ swapRequests, currentUserId, onSwapUpdate }: OngoingSwapsProps) => {
  const { getToken } = useAuth();
  const [feedbackDialog, setFeedbackDialog] = useState<{ open: boolean; swapRequest: SwapRequest | null }>({
    open: false,
    swapRequest: null
  });
  const [userDetails, setUserDetails] = useState<{ [key: string]: User }>({});
  const [loadingUsers, setLoadingUsers] = useState(false);

  const ongoingSwaps = swapRequests.filter(swap => 
    swap.status === 'accepted' && 
    (swap.fromUserId === currentUserId || swap.toUserId === currentUserId)
  );

  // Fetch user details for contact information
  useEffect(() => {
    const fetchUserDetails = async () => {
      if (!getToken || ongoingSwaps.length === 0) return;
      
      try {
        setLoadingUsers(true);
        const token = await getToken();
        const users = await userApi.searchUsers(token);
        
        // Transform backend data to frontend format
        const transformedUsers = users.map((user: any) => ({
          id: user.id,
          name: user.name,
          email: user.email || '',
          location: user.location,
          profilePicture: user.profile_picture,
          skillsOffered: user.skills_offered || [],
          skillsWanted: user.skills_wanted || [],
          availability: user.availability || '',
          phoneNumber: user.phone_number,
          isPublic: user.is_public || true,
          isActive: user.is_active || true,
          isBanned: user.is_banned || false,
          createdAt: user.created_at || new Date().toISOString(),
          clerkId: user.id,
          averageRating: user.average_rating || 0,
          totalRatings: user.total_ratings || 0
        }));
        
        // Create a map of user details
        const userMap: { [key: string]: User } = {};
        transformedUsers.forEach(user => {
          userMap[user.id] = user;
        });
        
        setUserDetails(userMap);
      } catch (error) {
        console.error('Failed to fetch user details:', error);
        toast.error('Failed to load contact information');
      } finally {
        setLoadingUsers(false);
      }
    };

    fetchUserDetails();
  }, [getToken, ongoingSwaps.length]);

  const handleCloseSwap = async (swapRequest: SwapRequest) => {
    if (!getToken) return;
    
    try {
      const token = await getToken();
      await swapApi.closeSwap(token, swapRequest.id);
      toast.success('Swap closure initiated. Waiting for other user to close.');
      onSwapUpdate();
    } catch (error) {
      console.error('Failed to close swap:', error);
      toast.error('Failed to close swap');
    }
  };

  const handleDeleteSwap = async (swapRequest: SwapRequest) => {
    if (!getToken) return;
    
    try {
      const token = await getToken();
      await swapApi.deleteSwap(token, swapRequest.id);
      toast.success('Swap deleted successfully!');
      onSwapUpdate();
    } catch (error) {
      console.error('Failed to delete swap:', error);
      toast.error('Failed to delete swap');
    }
  };

  const handleFeedbackSubmit = () => {
    onSwapUpdate();
  };

  if (ongoingSwaps.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Ongoing Swaps
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-4">
            No ongoing swaps. Complete a swap to see it here!
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Ongoing Swaps ({ongoingSwaps.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {ongoingSwaps.map((swap) => {
            const isInitiator = swap.fromUserId === currentUserId;
            const otherUserId = isInitiator ? swap.toUserId : swap.fromUserId;
            const otherUserName = isInitiator ? swap.toUserName : swap.fromUserName;
            const otherUser = userDetails[otherUserId];
            
            return (
              <div key={swap.id} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="default">Active Swap</Badge>
                    <span className="text-sm text-muted-foreground">
                      with {otherUserName}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(swap.createdAt).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-green-600">You're offering:</p>
                    <p>{swap.skillOffered}</p>
                  </div>
                  <div>
                    <p className="font-medium text-blue-600">You're receiving:</p>
                    <p>{swap.skillWanted}</p>
                  </div>
                </div>
                
                {swap.message && (
                  <div className="text-sm text-muted-foreground">
                    <p className="font-medium">Message:</p>
                    <p>{swap.message}</p>
                  </div>
                )}
                
                {/* Contact Information */}
                {otherUser && (
                  <div className="border-t pt-3">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium">Contact {otherUserName}:</p>
                      {loadingUsers && (
                        <div className="text-xs text-muted-foreground">Loading contact info...</div>
                      )}
                    </div>
                    <ContactButtons user={otherUser} />
                  </div>
                )}
                
                <div className="flex gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setFeedbackDialog({ open: true, swapRequest: swap })}
                  >
                    <Star className="h-4 w-4 mr-1" />
                    Rate & Feedback
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleCloseSwap(swap)}
                    disabled={swap.closedCount > 0}
                  >
                    <CheckCircle className="h-4 w-4 mr-1" />
                    {swap.closedCount > 0 ? 'Closing...' : 'Close Swap'}
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDeleteSwap(swap)}
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                </div>
                
                {swap.closedCount > 0 && (
                  <div className="text-sm text-muted-foreground">
                    {swap.closedCount === 1 ? 
                      'Waiting for other user to close...' : 
                      'Swap closed successfully!'
                    }
                  </div>
                )}
              </div>
            );
          })}
        </CardContent>
      </Card>

      {feedbackDialog.open && feedbackDialog.swapRequest && (
        <FeedbackDialog
          open={feedbackDialog.open}
          onOpenChange={(open) => setFeedbackDialog({ open, swapRequest: null })}
          swapRequest={feedbackDialog.swapRequest}
          currentUserId={currentUserId}
          onSubmit={handleFeedbackSubmit}
        />
      )}
    </>
  );
}; 
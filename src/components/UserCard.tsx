
import { useUser, useAuth } from '@clerk/clerk-react';
import { useEffect, useState } from 'react';
import { User } from '../types';
import { Button } from './ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { MapPin, Clock, Send, Star } from 'lucide-react';
import { SwapRequestDialog } from './SwapRequestDialog';
import { userApi } from '@/lib/api';
import { FeedbackDialog } from './FeedbackDialog';

interface UserCardProps {
  user: User;
  currentUserId?: string;
  showSwapButton?: boolean;
}

export const UserCard = ({ user, currentUserId, showSwapButton = true }: UserCardProps) => {
  const { getToken } = useAuth();
  const [showSwapDialog, setShowSwapDialog] = useState(false);
  const [showFeedbackDialog, setShowFeedbackDialog] = useState(false);

  const canSendSwapRequest = showSwapButton && currentUserId && currentUserId !== user.id;

  // Use rating information from user data if available, otherwise fetch it
  const [ratingInfo, setRatingInfo] = useState<{ average_rating: number; total_ratings: number } | null>(null);

  useEffect(() => {
    console.log('UserCard: User data received:', {
      id: user.id,
      name: user.name,
      averageRating: user.averageRating,
      totalRatings: user.totalRatings
    });

    // Use rating information from user data if available
    if (user.averageRating !== undefined && user.averageRating !== null) {
      console.log('UserCard: Using rating from user data:', user.averageRating);
      setRatingInfo({
        average_rating: user.averageRating,
        total_ratings: user.totalRatings || 0
      });
      return;
    }

    let mounted = true;
    (async () => {
      if (getToken) {
        const token = await getToken();
        try {
          console.log('UserCard: Fetching ratings for user:', user.id);
          const data = await userApi.getUserRatings(token, user.id);
          console.log('UserCard: Ratings data received:', data);
          if (mounted) setRatingInfo({
            average_rating: data.average_rating,
            total_ratings: data.total_ratings
          });
        } catch (error) {
          console.error('UserCard: Failed to fetch ratings for user:', user.id, error);
          if (mounted) setRatingInfo(null);
        }
      }
    })();
    return () => { mounted = false; };
  }, [user.id, user.averageRating, user.totalRatings, getToken]);

  return (
    <>
      <Card className="h-full">
        <CardHeader onClick={() => setShowFeedbackDialog(true)} className="cursor-pointer hover:bg-muted/50 rounded-t relative">
          {/* Rating positioned at top-right corner */}
          <div className="absolute top-3 right-3 flex items-center gap-1 text-yellow-600 text-sm bg-background/80 backdrop-blur-sm px-2 py-1 rounded-md border">
            <Star className="h-4 w-4" />
            {ratingInfo ? Number(ratingInfo.average_rating).toFixed(1) : '0.0'}
            <span className="text-muted-foreground ml-1">({ratingInfo ? Number(ratingInfo.total_ratings) : 0})</span>
          </div>
          
          <div className="flex items-center space-x-3">
            {user.profilePicture ? (
              <img 
                src={user.profilePicture} 
                alt={user.name}
                className="w-12 h-12 rounded-full object-cover"
              />
            ) : (
              <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center">
                <span className="text-lg font-semibold text-muted-foreground">
                  {user.name.charAt(0)}
                </span>
              </div>
            )}
            <div>
              <CardTitle className="text-lg">{user.name}</CardTitle>
              {user.location && (
                <div className="flex items-center text-sm text-muted-foreground">
                  <MapPin className="h-3 w-3 mr-1" />
                  {user.location}
                </div>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <div>
            <h4 className="font-medium text-sm mb-2">Skills Offered</h4>
            <div className="flex flex-wrap gap-1">
              {(user.skillsOffered || []).map((skill, index) => (
                <Badge key={index} variant="default" className="text-xs">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-medium text-sm mb-2">Skills Wanted</h4>
            <div className="flex flex-wrap gap-1">
              {(user.skillsWanted || []).map((skill, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>

          {user.availability && (
            <div className="flex items-center text-sm text-muted-foreground">
              <Clock className="h-3 w-3 mr-1" />
              {user.availability}
            </div>
          )}
        </CardContent>

        {canSendSwapRequest && (
          <CardFooter>
            <Button 
              onClick={() => {
                setShowSwapDialog(true);
              }}
              className="w-full"
              size="sm"
            >
              <Send className="h-4 w-4 mr-2" />
              Send Swap Request
            </Button>
          </CardFooter>
        )}
      </Card>

      {showSwapDialog && (
        <SwapRequestDialog
          targetUser={user}
          currentUserId={currentUserId!}
          open={showSwapDialog}
          onOpenChange={setShowSwapDialog}
        />
      )}
      {showFeedbackDialog && (
        <FeedbackDialog
          open={showFeedbackDialog}
          onOpenChange={setShowFeedbackDialog}
          userId={user.id}
          userName={user.name}
        />
      )}
    </>
  );
};

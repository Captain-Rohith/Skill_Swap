import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Star } from 'lucide-react';
import { userApi } from '@/lib/api';

interface FeedbackDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userId: string;
  userName: string;
}

export const FeedbackDialog = ({ open, onOpenChange, userId, userName }: FeedbackDialogProps) => {
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(false);
  const [ratings, setRatings] = useState<{ average_rating: number; total_ratings: number; feedback: any[] } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && getToken) {
      setLoading(true);
      setError(null);
      getToken().then(token => 
        userApi.getUserRatings(token, userId)
          .then(data => setRatings(data))
          .catch(err => setError('Failed to load feedback'))
          .finally(() => setLoading(false))
      );
    }
  }, [open, userId, getToken]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Feedback for {userName}</DialogTitle>
          <DialogDescription>
            See what others have said about this user.
          </DialogDescription>
        </DialogHeader>
        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : error ? (
          <div className="text-center text-red-500 py-8">{error}</div>
        ) : ratings ? (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Star className="text-yellow-400 h-5 w-5" />
              <span className="font-semibold text-lg">{ratings.average_rating.toFixed(1)}</span>
              <span className="text-muted-foreground text-sm">({ratings.total_ratings} rating{ratings.total_ratings !== 1 ? 's' : ''})</span>
            </div>
            {ratings.feedback.length === 0 ? (
              <div className="text-muted-foreground text-center py-4">No feedback yet.</div>
            ) : (
              <ul className="space-y-4 max-h-64 overflow-y-auto">
                {ratings.feedback.map((fb, idx) => (
                  <li key={fb.id || idx} className="border rounded p-3 bg-muted">
                    <div className="flex items-center gap-1 mb-1">
                      {[...Array(fb.rating)].map((_, i) => (
                        <Star key={i} className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                      ))}
                      <span className="ml-2 text-xs text-muted-foreground">{new Date(fb.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="text-sm mb-1">{fb.comment || <span className="text-muted-foreground">No comment</span>}</div>
                    {fb.from_user_id && (
                      <div className="text-xs text-muted-foreground">From: {fb.from_user_id}</div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}; 
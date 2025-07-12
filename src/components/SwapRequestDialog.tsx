
import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { User } from '@/types';
import { userApi, swapApi } from '@/lib/api';
import { useAuth } from '@clerk/clerk-react';
import { toast } from 'sonner';
import { Send } from 'lucide-react';

interface SwapRequestDialogProps {
  targetUser: User;
  currentUserId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const SwapRequestDialog = ({ targetUser, currentUserId, open, onOpenChange }: SwapRequestDialogProps) => {
  const { getToken } = useAuth();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [selectedSkillOffered, setSelectedSkillOffered] = useState('');
  const [selectedSkillWanted, setSelectedSkillWanted] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadCurrentUser = async () => {
      if (!currentUserId || !getToken) return;

      try {
        setIsLoading(true);
        const token = await getToken();
        const profile = await userApi.getProfile(token) as any;
        
        // Transform backend data to frontend format
        const transformedUser = {
          ...profile,
          skillsOffered: profile.skills_offered || [],
          skillsWanted: profile.skills_wanted || [],
          isPublic: profile.is_public
        };
        
        setCurrentUser(transformedUser);
      } catch (error) {
        console.error('Failed to load current user:', error);
        toast.error('Failed to load your profile');
      } finally {
        setIsLoading(false);
      }
    };

    if (open) {
      loadCurrentUser();
    }
  }, [currentUserId, getToken, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedSkillOffered || !selectedSkillWanted || !message.trim() || !currentUser || !getToken) {
      toast.error('Please fill in all fields');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const token = await getToken();
      
      // Transform frontend data to backend format (snake_case)
      const swapRequestData = {
        to_user_id: targetUser.id,
        skill_offered: selectedSkillOffered,
        skill_wanted: selectedSkillWanted,
        message: message.trim()
      };
      
      console.log('Sending swap request:', swapRequestData);
      await swapApi.createSwapRequest(token, swapRequestData);

      toast.success('Swap request sent successfully!');
      onOpenChange(false);
      
      // Reset form
      setSelectedSkillOffered('');
      setSelectedSkillWanted('');
      setMessage('');
    } catch (error) {
      console.error('Failed to send swap request:', error);
      toast.error('Failed to send swap request');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setSelectedSkillOffered('');
    setSelectedSkillWanted('');
    setMessage('');
  };

  useEffect(() => {
    if (!open) {
      resetForm();
    }
  }, [open]);

  if (isLoading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading your profile...</p>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (!currentUser) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Send Swap Request</DialogTitle>
          <DialogDescription>
            Send a skill swap request to {targetUser.name}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="skillOffered">Skill I'm Offering</Label>
            <Select value={selectedSkillOffered} onValueChange={setSelectedSkillOffered}>
              <SelectTrigger>
                <SelectValue placeholder="Select a skill you can offer" />
              </SelectTrigger>
              <SelectContent>
                {currentUser.skillsOffered.map((skill, index) => (
                  <SelectItem key={index} value={skill}>
                    {skill}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {currentUser.skillsOffered.length === 0 && (
              <p className="text-sm text-muted-foreground">
                Add skills to your profile first to send swap requests
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="skillWanted">Skill I Want to Learn</Label>
            <Select value={selectedSkillWanted} onValueChange={setSelectedSkillWanted}>
              <SelectTrigger>
                <SelectValue placeholder="Select a skill from their offerings" />
              </SelectTrigger>
              <SelectContent>
                {targetUser.skillsOffered.map((skill, index) => (
                  <SelectItem key={index} value={skill}>
                    {skill}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="message">Message</Label>
            <Textarea
              id="message"
              placeholder="Tell them why you'd like to swap skills..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={3}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              disabled={isSubmitting || !selectedSkillOffered || !selectedSkillWanted || !message.trim()}
              className="flex-1"
            >
              <Send className="h-4 w-4 mr-2" />
              {isSubmitting ? 'Sending...' : 'Send Request'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};


import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Camera } from 'lucide-react';
import { User } from '@/types';

interface ProfilePhotoProps {
  user: User | null;
  isEditing: boolean;
  clerkUser: any;
}

export const ProfilePhoto = ({ user, isEditing, clerkUser }: ProfilePhotoProps) => {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex flex-col items-center space-y-4">
          <div className="relative">
            {user?.profilePicture || clerkUser?.imageUrl ? (
              <img 
                src={user?.profilePicture || clerkUser?.imageUrl} 
                alt={user?.name || clerkUser?.fullName}
                className="w-32 h-32 rounded-full object-cover border-4 border-border"
              />
            ) : (
              <div className="w-32 h-32 bg-muted rounded-full flex items-center justify-center border-4 border-border">
                <span className="text-3xl font-semibold text-muted-foreground">
                  {(user?.name || clerkUser?.fullName || 'U').charAt(0)}
                </span>
              </div>
            )}
            
            {isEditing && (
              <Button
                size="sm"
                variant="secondary"
                className="absolute bottom-0 right-0 rounded-full p-2 h-8 w-8"
              >
                <Camera className="h-4 w-4" />
              </Button>
            )}
          </div>
          
          <div className="text-center">
            <h3 className="font-semibold text-lg">{user?.name || clerkUser?.fullName}</h3>
            <p className="text-sm text-muted-foreground">{clerkUser?.emailAddresses[0]?.emailAddress}</p>
            {user?.location && (
              <p className="text-sm text-muted-foreground mt-1">{user.location}</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

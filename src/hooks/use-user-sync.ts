import { useEffect, useState } from 'react';
import { useUser, useAuth } from '@clerk/clerk-react';
import { userApi } from '@/lib/api';
import { User } from '@/types';
import { toast } from 'sonner';

export const useUserSync = () => {
  const { user: clerkUser, isLoaded } = useUser();
  const { getToken } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const syncUser = async () => {
    if (!clerkUser || !getToken) return;

    try {
      setIsSyncing(true);
      const token = await getToken();
      
      console.log('Syncing user:', clerkUser.id);
      
      // First try to get the user profile
      try {
        const profile = await userApi.getProfile(token);
        console.log('User profile found:', profile);
        setUser(profile);
      } catch (error) {
        // If user doesn't exist, sync from Clerk
        console.log('User not found in database, syncing from Clerk...');
        const syncedUser = await userApi.syncFromClerk(token);
        console.log('User synced from Clerk:', syncedUser);
        setUser(syncedUser);
        toast.success('Profile synced successfully!');
      }
    } catch (error) {
      console.error('Failed to sync user:', error);
      toast.error('Failed to sync profile. Please try again.');
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    if (isLoaded && clerkUser) {
      syncUser();
    }
  }, [isLoaded, clerkUser?.id]);

  return {
    user,
    isSyncing,
    syncUser,
    isLoaded,
  };
}; 
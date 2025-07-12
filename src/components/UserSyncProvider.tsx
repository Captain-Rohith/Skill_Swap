import { useUserSync } from '@/hooks/use-user-sync';

interface UserSyncProviderProps {
  children: React.ReactNode;
}

export const UserSyncProvider = ({ children }: UserSyncProviderProps) => {
  const { isSyncing, isLoaded } = useUserSync();

  // Show loading state while syncing
  if (isLoaded && isSyncing) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Syncing your profile...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}; 
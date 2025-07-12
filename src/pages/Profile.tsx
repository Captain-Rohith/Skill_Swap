
import { useUser, useAuth } from '@clerk/clerk-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useState, useEffect } from 'react';
import { User } from '@/types';
import { userApi } from '@/lib/api';
import { toast } from 'sonner';
import { Edit, Save } from 'lucide-react';
import { ProfilePhoto } from '@/components/ProfilePhoto';
import { SkillsSection } from '@/components/SkillsSection';
import { ProfileForm } from '@/components/ProfileForm';

export const Profile = () => {
  const { user: clerkUser } = useUser();
  const { getToken } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    availability: '',
    skillsOffered: [] as string[],
    skillsWanted: [] as string[],
    isPublic: true
  });

  useEffect(() => {
    const loadUserProfile = async () => {
      if (!clerkUser || !getToken) return;

      try {
        setIsLoading(true);
        const token = await getToken();
        
        // Try to get user profile from backend
        try {
          const profile = await userApi.getProfile(token) as any;
          
          // Transform backend data (snake_case) to frontend format (camelCase)
          const transformedProfile = {
            ...profile,
            skillsOffered: profile.skills_offered || [],
            skillsWanted: profile.skills_wanted || [],
            isPublic: profile.is_public
          };
          
          setUser(transformedProfile);
          setFormData({
            name: profile.name,
            location: profile.location || '',
            availability: profile.availability || '',
            skillsOffered: profile.skills_offered || [],
            skillsWanted: profile.skills_wanted || [],
            isPublic: profile.is_public
          });
        } catch (error) {
          // If user doesn't exist, sync from Clerk
          console.log('User not found, syncing from Clerk...');
          const syncedUser = await userApi.syncFromClerk(token) as any;
          
          // Transform backend data (snake_case) to frontend format (camelCase)
          const transformedUser = {
            ...syncedUser,
            skillsOffered: syncedUser.skills_offered || [],
            skillsWanted: syncedUser.skills_wanted || [],
            isPublic: syncedUser.is_public
          };
          
          setUser(transformedUser);
          setFormData({
            name: syncedUser.name,
            location: syncedUser.location || '',
            availability: syncedUser.availability || '',
            skillsOffered: syncedUser.skills_offered || [],
            skillsWanted: syncedUser.skills_wanted || [],
            isPublic: syncedUser.is_public
          });
        }
      } catch (error) {
        console.error('Failed to load user profile:', error);
        toast.error('Failed to load profile');
      } finally {
        setIsLoading(false);
      }
    };

    loadUserProfile();
  }, [clerkUser, getToken]);

  const handleSave = async () => {
    if (!clerkUser || !user || !getToken) return;

    try {
      const token = await getToken();
      
      // Transform frontend data (camelCase) to backend format (snake_case)
      const updateData = {
        name: formData.name,
        location: formData.location || undefined,
        availability: formData.availability || undefined,
        skills_offered: formData.skillsOffered,
        skills_wanted: formData.skillsWanted,
        is_public: formData.isPublic
      };
      
      console.log('Sending update data:', updateData);
      const updatedUser = await userApi.updateProfile(token, updateData);

      setUser(updatedUser);
      setIsEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error('Failed to update profile');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    if (user) {
      setFormData({
        name: user.name,
        location: user.location || '',
        availability: user.availability || '',
        skillsOffered: [...(user.skillsOffered || [])],
        skillsWanted: [...(user.skillsWanted || [])],
        isPublic: user.isPublic
      });
    }
  };

  if (!clerkUser) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <p>Please sign in to view your profile.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      {/* Header Section */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">My Profile</h1>
          <p className="text-muted-foreground">Manage your profile and skills</p>
        </div>
        <Button
          onClick={() => isEditing ? handleSave() : setIsEditing(true)}
          variant={isEditing ? "default" : "outline"}
          className="flex items-center gap-2"
        >
          {isEditing ? (
            <>
              <Save className="h-4 w-4" />
              Save Changes
            </>
          ) : (
            <>
              <Edit className="h-4 w-4" />
              Edit Profile
            </>
          )}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Photo and Basic Info */}
        <div className="lg:col-span-1">
          <ProfilePhoto 
            user={user}
            isEditing={isEditing}
            clerkUser={clerkUser}
          />
        </div>

        {/* Main Profile Information */}
        <div className="lg:col-span-2 space-y-6">
          <ProfileForm
            formData={formData}
            setFormData={setFormData}
            isEditing={isEditing}
          />

          <SkillsSection
            skillsOffered={formData.skillsOffered}
            skillsWanted={formData.skillsWanted}
            isEditing={isEditing}
            onUpdateSkills={(type, skills) => {
              if (type === 'offered') {
                setFormData(prev => ({ ...prev, skillsOffered: skills }));
              } else {
                setFormData(prev => ({ ...prev, skillsWanted: skills }));
              }
            }}
          />

          {/* Privacy Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Privacy Settings</CardTitle>
              <CardDescription>Control who can see your profile</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <Switch
                  id="public"
                  checked={formData.isPublic}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, isPublic: checked }))}
                  disabled={!isEditing}
                />
                <Label htmlFor="public" className="text-sm">
                  Make profile visible in public search
                </Label>
              </div>
              {!formData.isPublic && (
                <p className="text-xs text-muted-foreground mt-2">
                  Your profile will only be visible to you and won't appear in search results
                </p>
              )}
            </CardContent>
          </Card>

          {/* Action Buttons */}
          {isEditing && (
            <div className="flex gap-3 pt-4">
              <Button onClick={handleSave} className="flex-1">
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </Button>
              <Button variant="outline" onClick={handleCancel} className="flex-1">
                Cancel
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

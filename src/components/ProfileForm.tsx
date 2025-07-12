
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

interface ProfileFormProps {
  formData: {
    name: string;
    location: string;
    availability: string;
    skillsOffered: string[];
    skillsWanted: string[];
    isPublic: boolean;
  };
  setFormData: React.Dispatch<React.SetStateAction<{
    name: string;
    location: string;
    availability: string;
    skillsOffered: string[];
    skillsWanted: string[];
    isPublic: boolean;
  }>>;
  isEditing: boolean;
}

export const ProfileForm = ({ formData, setFormData, isEditing }: ProfileFormProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Basic Information</CardTitle>
        <CardDescription>Your profile details</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="name">Full Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              disabled={!isEditing}
              placeholder="Enter your full name"
            />
          </div>

          <div>
            <Label htmlFor="location">Location</Label>
            <Input
              id="location"
              value={formData.location}
              onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
              disabled={!isEditing}
              placeholder="City, Country"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="availability">Availability</Label>
          <Textarea
            id="availability"
            value={formData.availability}
            onChange={(e) => setFormData(prev => ({ ...prev, availability: e.target.value }))}
            disabled={!isEditing}
            placeholder="When are you available for skill swaps? (e.g., Weekends, Evenings after 6pm...)"
            rows={3}
          />
        </div>
      </CardContent>
    </Card>
  );
};

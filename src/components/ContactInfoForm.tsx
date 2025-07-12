import { useState } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Phone, Mail, Save } from 'lucide-react';
import { userApi } from '@/lib/api';
import { toast } from 'sonner';

interface ContactInfoFormProps {
  currentEmail?: string;
  currentPhone?: string;
  onUpdate: () => void;
}

export const ContactInfoForm = ({ currentEmail, currentPhone, onUpdate }: ContactInfoFormProps) => {
  const { getToken } = useAuth();
  const [email, setEmail] = useState(currentEmail || '');
  const [phone, setPhone] = useState(currentPhone || '');
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    if (!getToken) return;
    
    try {
      setLoading(true);
      const token = await getToken();
      
      await userApi.updateProfile(token, {
        email: email.trim() || undefined,
        phoneNumber: phone.trim() || undefined
      });
      
      toast.success('Contact information updated successfully!');
      setIsEditing(false);
      onUpdate();
    } catch (error) {
      console.error('Failed to update contact info:', error);
      toast.error('Failed to update contact information');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEmail(currentEmail || '');
    setPhone(currentPhone || '');
    setIsEditing(false);
  };

  if (!isEditing) {
    return (
      <Card className="mb-4">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Contact Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div>
              <Label className="text-sm font-medium">Email</Label>
              <p className="text-sm text-muted-foreground">
                {currentEmail || 'No email provided'}
              </p>
            </div>
            <div>
              <Label className="text-sm font-medium">Phone Number</Label>
              <p className="text-sm text-muted-foreground">
                {currentPhone || 'No phone number provided'}
              </p>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setIsEditing(true)}
            >
              Edit Contact Info
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Mail className="h-5 w-5" />
          Edit Contact Information
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
            />
          </div>
          <div>
            <Label htmlFor="phone">Phone Number</Label>
            <Input
              id="phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Enter your phone number"
            />
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={handleSave}
              disabled={loading}
            >
              <Save className="h-4 w-4 mr-1" />
              {loading ? 'Saving...' : 'Save'}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleCancel}
              disabled={loading}
            >
              Cancel
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 
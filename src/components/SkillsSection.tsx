
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus, X } from 'lucide-react';
import { useState } from 'react';

interface SkillsSectionProps {
  skillsOffered: string[];
  skillsWanted: string[];
  isEditing: boolean;
  onUpdateSkills: (type: 'offered' | 'wanted', skills: string[]) => void;
}

export const SkillsSection = ({ skillsOffered, skillsWanted, isEditing, onUpdateSkills }: SkillsSectionProps) => {
  const [newSkillOffered, setNewSkillOffered] = useState('');
  const [newSkillWanted, setNewSkillWanted] = useState('');

  const addSkill = (type: 'offered' | 'wanted') => {
    const skill = type === 'offered' ? newSkillOffered : newSkillWanted;
    if (!skill.trim()) return;

    const currentSkills = type === 'offered' ? skillsOffered : skillsWanted;
    const newSkills = [...currentSkills, skill.trim()];
    onUpdateSkills(type, newSkills);

    if (type === 'offered') {
      setNewSkillOffered('');
    } else {
      setNewSkillWanted('');
    }
  };

  const removeSkill = (type: 'offered' | 'wanted', index: number) => {
    const currentSkills = type === 'offered' ? skillsOffered : skillsWanted;
    const newSkills = currentSkills.filter((_, i) => i !== index);
    onUpdateSkills(type, newSkills);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Skills Offered */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <span className="w-3 h-3 bg-primary rounded-full"></span>
            Skills I Offer
          </CardTitle>
          <CardDescription>Skills you can teach others</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2 min-h-[2.5rem]">
            {skillsOffered.map((skill, index) => (
              <Badge key={index} variant="default" className="flex items-center gap-1">
                {skill}
                {isEditing && (
                  <button
                    onClick={() => removeSkill('offered', index)}
                    className="ml-1 hover:bg-primary-foreground/20 rounded-full p-1"
                  >
                    <X className="h-3 w-3" />
                  </button>
                )}
              </Badge>
            ))}
            {skillsOffered.length === 0 && (
              <p className="text-sm text-muted-foreground">No skills added yet</p>
            )}
          </div>
          
          {isEditing && (
            <div className="flex gap-2">
              <Input
                value={newSkillOffered}
                onChange={(e) => setNewSkillOffered(e.target.value)}
                placeholder="Add a skill you can offer"
                onKeyPress={(e) => e.key === 'Enter' && addSkill('offered')}
              />
              <Button onClick={() => addSkill('offered')} size="sm">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Skills Wanted */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <span className="w-3 h-3 bg-secondary rounded-full border-2 border-secondary-foreground"></span>
            Skills I Want
          </CardTitle>
          <CardDescription>Skills you want to learn</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2 min-h-[2.5rem]">
            {skillsWanted.map((skill, index) => (
              <Badge key={index} variant="outline" className="flex items-center gap-1">
                {skill}
                {isEditing && (
                  <button
                    onClick={() => removeSkill('wanted', index)}
                    className="ml-1 hover:bg-muted rounded-full p-1"
                  >
                    <X className="h-3 w-3" />
                  </button>
                )}
              </Badge>
            ))}
            {skillsWanted.length === 0 && (
              <p className="text-sm text-muted-foreground">No skills added yet</p>
            )}
          </div>
          
          {isEditing && (
            <div className="flex gap-2">
              <Input
                value={newSkillWanted}
                onChange={(e) => setNewSkillWanted(e.target.value)}
                placeholder="Add a skill you want to learn"
                onKeyPress={(e) => e.key === 'Enter' && addSkill('wanted')}
              />
              <Button onClick={() => addSkill('wanted')} size="sm">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

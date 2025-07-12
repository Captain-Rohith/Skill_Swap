import { Button } from '@/components/ui/button';
import { Phone, Mail, MessageCircle } from 'lucide-react';
import { User } from '@/types';

interface ContactButtonsProps {
  user: User;
  className?: string;
}

export const ContactButtons = ({ user, className = '' }: ContactButtonsProps) => {
  const handleCall = () => {
    if (user.phoneNumber) {
      window.open(`tel:${user.phoneNumber}`, '_self');
    }
  };

  const handleWhatsApp = () => {
    if (user.phoneNumber) {
      const message = `Hi ${user.name}, I'd like to discuss our skill swap!`;
      const whatsappUrl = `https://wa.me/${user.phoneNumber.replace(/\D/g, '')}?text=${encodeURIComponent(message)}`;
      window.open(whatsappUrl, '_blank');
    }
  };

  const handleEmail = () => {
    if (user.email) {
      const subject = `Skill Swap Discussion`;
      const body = `Hi ${user.name},\n\nI'd like to discuss our skill swap arrangement.\n\nBest regards`;
      const mailtoUrl = `mailto:${user.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      window.open(mailtoUrl, '_self');
    }
  };

  const hasPhone = user.phoneNumber && user.phoneNumber.trim() !== '';
  const hasEmail = user.email && user.email.trim() !== '';

  if (!hasPhone && !hasEmail) {
    return (
      <div className={`text-sm text-muted-foreground ${className}`}>
        No contact information available
      </div>
    );
  }

  return (
    <div className={`flex gap-2 ${className}`}>
      {hasPhone && (
        <>
          <Button
            size="sm"
            variant="outline"
            onClick={handleCall}
            className="h-8 px-2"
            title={`Call ${user.name}`}
          >
            <Phone className="h-3 w-3" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleWhatsApp}
            className="h-8 px-2"
            title={`WhatsApp ${user.name}`}
          >
            <MessageCircle className="h-3 w-3" />
          </Button>
        </>
      )}
      {hasEmail && (
        <Button
          size="sm"
          variant="outline"
          onClick={handleEmail}
          className="h-8 px-2"
          title={`Email ${user.name}`}
        >
          <Mail className="h-3 w-3" />
        </Button>
      )}
    </div>
  );
}; 
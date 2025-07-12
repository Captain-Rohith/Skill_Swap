
import { SignedIn, SignedOut } from '@clerk/clerk-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Search, Star, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PlatformMessages } from '@/components/PlatformMessages';

export const Home = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Platform Messages */}
        <SignedIn>
          <PlatformMessages />
        </SignedIn>
        
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
            Skill Swap Platform
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Connect with others to exchange skills, learn new abilities, and build meaningful connections. 
            Trade your expertise for knowledge you want to gain.
          </p>
          
          <SignedOut>
            <div className="space-x-4">
              <Button size="lg" asChild>
                <Link to="/search">Get Started</Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link to="/search">Browse Skills</Link>
              </Button>
            </div>
          </SignedOut>

          <SignedIn>
            <div className="space-x-4">
              <Button size="lg" asChild>
                <Link to="/dashboard">Go to Dashboard</Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link to="/search">Find Skills</Link>
              </Button>
            </div>
          </SignedIn>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <Card>
            <CardHeader className="text-center">
              <Users className="h-12 w-12 text-primary mx-auto mb-4" />
              <CardTitle>Connect</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-center">
                Find people with complementary skills and build professional relationships
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="text-center">
              <Search className="h-12 w-12 text-primary mx-auto mb-4" />
              <CardTitle>Discover</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-center">
                Search for specific skills or browse profiles to find the perfect match
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="text-center">
              <Star className="h-12 w-12 text-primary mx-auto mb-4" />
              <CardTitle>Review</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-center">
                Rate and review your skill swap experiences to help the community
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="text-center">
              <Shield className="h-12 w-12 text-primary mx-auto mb-4" />
              <CardTitle>Safe</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-center">
                Secure platform with user verification and community moderation
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        {/* Stats Section */}
        <div className="bg-muted rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold mb-6">Join Our Growing Community</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-3xl font-bold text-primary">500+</div>
              <div className="text-muted-foreground">Active Members</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary">1,200+</div>
              <div className="text-muted-foreground">Skills Exchanged</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary">50+</div>
              <div className="text-muted-foreground">Skill Categories</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

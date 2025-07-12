
import { useState, useMemo } from 'react';
import { useUser, useAuth } from '@clerk/clerk-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search as SearchIcon, Filter, MapPin, X, Star, Zap } from 'lucide-react';
import { User } from '@/types';
import { UserCard } from '@/components/UserCard';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useQuery } from '@tanstack/react-query';
import { userApi } from '@/lib/api';

const fetchUsers = async (token: string | null): Promise<User[]> => {
  const users = await userApi.searchUsers(token);
  
  console.log('Search: Raw users data from API:', users);
  
  // Transform backend data (snake_case) to frontend format (camelCase)
  const transformedUsers = users.map((user: any) => ({
    id: user.id,
    name: user.name,
    email: user.email || '',
    location: user.location,
    profilePicture: user.profile_picture,
    skillsOffered: user.skills_offered || [],
    skillsWanted: user.skills_wanted || [],
    availability: user.availability || '',
    phoneNumber: user.phone_number,
    isPublic: user.is_public || true,
    isActive: user.is_active || true,
    isBanned: user.is_banned || false,
    createdAt: user.created_at || new Date().toISOString(),
    clerkId: user.id,
    averageRating: user.average_rating || 0,
    totalRatings: user.total_ratings || 0
  }));
  
  console.log('Search: Transformed users data:', transformedUsers);
  
  return transformedUsers;
};

export const Search = () => {
  const { user } = useUser();
  const { getToken } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [ratingFilter, setRatingFilter] = useState<string>('');
  const [skillsOfferedFilter, setSkillsOfferedFilter] = useState<string>('');
  const [skillsWantedFilter, setSkillsWantedFilter] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);

  const { data: users = [], isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const token = await getToken();
      return fetchUsers(token);
    },
    enabled: !!user,
  });

  const filteredUsers = useMemo(() => {
    let filtered = users;

    // Apply search term filter
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(user => {
        const nameMatch = user.name.toLowerCase().includes(searchLower);
        const locationMatch = user.location?.toLowerCase().includes(searchLower);
        const skillsOfferedMatch = (user.skillsOffered || []).some(skill => 
          skill.toLowerCase().includes(searchLower)
        );
        const skillsWantedMatch = (user.skillsWanted || []).some(skill => 
          skill.toLowerCase().includes(searchLower)
        );

        return nameMatch || locationMatch || skillsOfferedMatch || skillsWantedMatch;
      });
    }

    // Apply location filter
    if (locationFilter.trim()) {
      const locationLower = locationFilter.toLowerCase();
      filtered = filtered.filter(user => 
        user.location?.toLowerCase().includes(locationLower)
      );
    }

    // Apply rating filter
    if (ratingFilter && ratingFilter !== 'any') {
      const minRating = parseFloat(ratingFilter);
      filtered = filtered.filter(user => {
        return user.averageRating >= minRating;
      });
    }

    // Apply skills offered filter
    if (skillsOfferedFilter.trim()) {
      const skillLower = skillsOfferedFilter.toLowerCase();
      filtered = filtered.filter(user => 
        (user.skillsOffered || []).some(skill => 
          skill.toLowerCase().includes(skillLower)
        )
      );
    }

    // Apply skills wanted filter
    if (skillsWantedFilter.trim()) {
      const skillLower = skillsWantedFilter.toLowerCase();
      filtered = filtered.filter(user => 
        (user.skillsWanted || []).some(skill => 
          skill.toLowerCase().includes(skillLower)
        )
      );
    }

    return filtered;
  }, [searchTerm, locationFilter, ratingFilter, skillsOfferedFilter, skillsWantedFilter, users]);

  const clearLocationFilter = () => {
    setLocationFilter('');
  };

  const clearRatingFilter = () => {
    setRatingFilter('');
  };

  const clearSkillsOfferedFilter = () => {
    setSkillsOfferedFilter('');
  };

  const clearSkillsWantedFilter = () => {
    setSkillsWantedFilter('');
  };

  const clearAllFilters = () => {
    setLocationFilter('');
    setRatingFilter('');
    setSkillsOfferedFilter('');
    setSkillsWantedFilter('');
  };

  // Count active filters
  const activeFilterCount = [
    locationFilter,
    ratingFilter,
    skillsOfferedFilter,
    skillsWantedFilter
  ].filter(Boolean).length;

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center">Loading users...</div>
      </div>
    );
  }

  if (error) {
    console.error('Search error:', error);
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center text-red-500">
          <p className="mb-2">Error loading users. Please try again.</p>
          <p className="text-sm text-muted-foreground">
            Make sure you're signed in and the backend server is running.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Find Skills</h1>
        <p className="text-muted-foreground">Discover people with the skills you need</p>
      </div>

      <div className="mb-8">
        <div className="flex gap-4 items-center">
          <div className="relative flex-1">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name, location, or skills..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Popover open={showFilters} onOpenChange={setShowFilters}>
            <PopoverTrigger asChild>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filters
                {activeFilterCount > 0 && <Badge variant="secondary" className="ml-2">{activeFilterCount}</Badge>}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Filters</h4>
                  {activeFilterCount > 0 && (
                    <Button size="sm" variant="ghost" onClick={clearAllFilters}>
                      Clear all
                    </Button>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="location">Location</Label>
                  <div className="flex gap-2 mt-1">
                    <Input
                      id="location"
                      placeholder="Filter by location..."
                      value={locationFilter}
                      onChange={(e) => setLocationFilter(e.target.value)}
                    />
                    {locationFilter && (
                      <Button size="sm" variant="ghost" onClick={clearLocationFilter}>
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>

                <div>
                  <Label htmlFor="rating">Minimum Rating</Label>
                  <div className="flex gap-2 mt-1">
                    <Select value={ratingFilter} onValueChange={setRatingFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select minimum rating" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="any">Any rating</SelectItem>
                        <SelectItem value="1">1+ stars</SelectItem>
                        <SelectItem value="2">2+ stars</SelectItem>
                        <SelectItem value="3">3+ stars</SelectItem>
                        <SelectItem value="4">4+ stars</SelectItem>
                        <SelectItem value="5">5 stars</SelectItem>
                      </SelectContent>
                    </Select>
                    {ratingFilter && ratingFilter !== 'any' && (
                      <Button size="sm" variant="ghost" onClick={clearRatingFilter}>
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>

                <div>
                  <Label htmlFor="skills-offered">Skills Offered</Label>
                  <div className="flex gap-2 mt-1">
                    <Input
                      id="skills-offered"
                      placeholder="Filter by skills offered..."
                      value={skillsOfferedFilter}
                      onChange={(e) => setSkillsOfferedFilter(e.target.value)}
                    />
                    {skillsOfferedFilter && (
                      <Button size="sm" variant="ghost" onClick={clearSkillsOfferedFilter}>
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>

                <div>
                  <Label htmlFor="skills-wanted">Skills Wanted</Label>
                  <div className="flex gap-2 mt-1">
                    <Input
                      id="skills-wanted"
                      placeholder="Filter by skills wanted..."
                      value={skillsWantedFilter}
                      onChange={(e) => setSkillsWantedFilter(e.target.value)}
                    />
                    {skillsWantedFilter && (
                      <Button size="sm" variant="ghost" onClick={clearSkillsWantedFilter}>
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {/* Active Filters */}
      {(locationFilter || ratingFilter || skillsOfferedFilter || skillsWantedFilter) && (
        <div className="mb-6 flex gap-2 flex-wrap">
          {locationFilter && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              {locationFilter}
              <button onClick={clearLocationFilter} className="ml-1">
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {ratingFilter && ratingFilter !== 'any' && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <Star className="h-3 w-3" />
              {ratingFilter}+ stars
              <button onClick={clearRatingFilter} className="ml-1">
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {skillsOfferedFilter && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <Zap className="h-3 w-3" />
              Offers: {skillsOfferedFilter}
              <button onClick={clearSkillsOfferedFilter} className="ml-1">
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {skillsWantedFilter && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <Zap className="h-3 w-3" />
              Wants: {skillsWantedFilter}
              <button onClick={clearSkillsWantedFilter} className="ml-1">
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
        </div>
      )}

      <div className="mb-6">
        <p className="text-muted-foreground">
          Found {filteredUsers.length} user{filteredUsers.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredUsers.map(targetUser => (
          <UserCard 
            key={targetUser.id} 
            user={targetUser} 
            currentUserId={user?.id}
            showSwapButton={true}
          />
        ))}
      </div>

      {filteredUsers.length === 0 && !isLoading && (
        <div className="text-center py-12">
          {searchTerm || locationFilter ? (
            <>
              <p className="text-muted-foreground text-lg">No users found matching your search.</p>
              <p className="text-muted-foreground">Try different keywords or check the spelling.</p>
            </>
          ) : (
            <>
              <p className="text-muted-foreground text-lg">No users found.</p>
              <p className="text-muted-foreground">Be the first to join and share your skills!</p>
            </>
          )}
        </div>
      )}
    </div>
  );
};

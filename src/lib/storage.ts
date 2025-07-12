import { User, SwapRequest, Feedback, AdminAction } from '../types';

// Storage keys
const USERS_KEY = 'skill_swap_users';
const SWAP_REQUESTS_KEY = 'skill_swap_requests';
const FEEDBACK_KEY = 'skill_swap_feedback';
const ADMIN_ACTIONS_KEY = 'skill_swap_admin_actions';

// Sample data for testing
const sampleUsers: User[] = [
  {
    id: '1',
    name: 'Alice Johnson',
    email: 'alice@example.com',
    location: 'New York, NY',
    skillsOffered: ['JavaScript', 'React', 'Node.js'],
    skillsWanted: ['Python', 'Machine Learning'],
    availability: 'Weekends and evenings',
    isPublic: true,
    isActive: true,
    isBanned: false,
    createdAt: new Date().toISOString(),
    clerkId: 'sample_1'
  },
  {
    id: '2',
    name: 'Bob Smith',
    email: 'bob@example.com',
    location: 'San Francisco, CA',
    skillsOffered: ['Python', 'Django', 'PostgreSQL'],
    skillsWanted: ['React', 'TypeScript'],
    availability: 'Flexible schedule',
    isPublic: true,
    isActive: true,
    isBanned: false,
    createdAt: new Date().toISOString(),
    clerkId: 'sample_2'
  },
  {
    id: '3',
    name: 'Carol Davis',
    email: 'carol@example.com',
    location: 'Austin, TX',
    skillsOffered: ['UI/UX Design', 'Figma', 'Adobe Creative Suite'],
    skillsWanted: ['Frontend Development', 'CSS'],
    availability: 'Mornings preferred',
    isPublic: true,
    isActive: true,
    isBanned: false,
    createdAt: new Date().toISOString(),
    clerkId: 'sample_3'
  }
];

// Initialize sample data if not exists
export const initializeData = () => {
  if (!localStorage.getItem(USERS_KEY)) {
    localStorage.setItem(USERS_KEY, JSON.stringify(sampleUsers));
  }
  if (!localStorage.getItem(SWAP_REQUESTS_KEY)) {
    localStorage.setItem(SWAP_REQUESTS_KEY, JSON.stringify([]));
  }
  if (!localStorage.getItem(FEEDBACK_KEY)) {
    localStorage.setItem(FEEDBACK_KEY, JSON.stringify([]));
  }
  if (!localStorage.getItem(ADMIN_ACTIONS_KEY)) {
    localStorage.setItem(ADMIN_ACTIONS_KEY, JSON.stringify([]));
  }
};

// User operations
export const getUsers = (): User[] => {
  const users = localStorage.getItem(USERS_KEY);
  return users ? JSON.parse(users) : [];
};

export const getUserById = (id: string): User | null => {
  const users = getUsers();
  return users.find(user => user.id === id) || null;
};

export const getUserByClerkId = (clerkId: string): User | null => {
  const users = getUsers();
  return users.find(user => user.clerkId === clerkId) || null;
};

export const createUser = (user: Omit<User, 'id' | 'createdAt'>): User => {
  const users = getUsers();
  const newUser: User = {
    ...user,
    id: Date.now().toString(),
    createdAt: new Date().toISOString()
  };
  users.push(newUser);
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
  return newUser;
};

export const updateUser = (id: string, updates: Partial<User>): User | null => {
  const users = getUsers();
  const userIndex = users.findIndex(user => user.id === id);
  if (userIndex === -1) return null;
  
  users[userIndex] = { ...users[userIndex], ...updates };
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
  return users[userIndex];
};

// Swap request operations
export const getSwapRequests = (): SwapRequest[] => {
  const requests = localStorage.getItem(SWAP_REQUESTS_KEY);
  return requests ? JSON.parse(requests) : [];
};

export const createSwapRequest = (request: Omit<SwapRequest, 'id' | 'createdAt' | 'updatedAt'>): SwapRequest => {
  const requests = getSwapRequests();
  const newRequest: SwapRequest = {
    ...request,
    id: Date.now().toString(),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  requests.push(newRequest);
  localStorage.setItem(SWAP_REQUESTS_KEY, JSON.stringify(requests));
  return newRequest;
};

export const updateSwapRequest = (id: string, updates: Partial<SwapRequest>): SwapRequest | null => {
  const requests = getSwapRequests();
  const requestIndex = requests.findIndex(req => req.id === id);
  if (requestIndex === -1) return null;
  
  requests[requestIndex] = { 
    ...requests[requestIndex], 
    ...updates, 
    updatedAt: new Date().toISOString() 
  };
  localStorage.setItem(SWAP_REQUESTS_KEY, JSON.stringify(requests));
  return requests[requestIndex];
};

// Feedback operations
export const getFeedback = (): Feedback[] => {
  const feedback = localStorage.getItem(FEEDBACK_KEY);
  return feedback ? JSON.parse(feedback) : [];
};

export const createFeedback = (feedback: Omit<Feedback, 'id' | 'createdAt'>): Feedback => {
  const feedbackList = getFeedback();
  const newFeedback: Feedback = {
    ...feedback,
    id: Date.now().toString(),
    createdAt: new Date().toISOString()
  };
  feedbackList.push(newFeedback);
  localStorage.setItem(FEEDBACK_KEY, JSON.stringify(feedbackList));
  return newFeedback;
};

// Admin operations
export const getAdminActions = (): AdminAction[] => {
  const actions = localStorage.getItem(ADMIN_ACTIONS_KEY);
  return actions ? JSON.parse(actions) : [];
};

export const createAdminAction = (action: Omit<AdminAction, 'id' | 'createdAt'>): AdminAction => {
  const actions = getAdminActions();
  const newAction: AdminAction = {
    ...action,
    id: Date.now().toString(),
    createdAt: new Date().toISOString()
  };
  actions.push(newAction);
  localStorage.setItem(ADMIN_ACTIONS_KEY, JSON.stringify(actions));
  return newAction;
};

// Add the missing addAdminAction export (alias for createAdminAction)
export const addAdminAction = createAdminAction;


export interface User {
  id: string;
  name: string;
  email: string;
  location?: string;
  profilePicture?: string;
  skillsOffered: string[];
  skillsWanted: string[];
  availability: string;
  phoneNumber?: string;
  isPublic: boolean;
  isActive: boolean;
  isBanned?: boolean;
  createdAt: string;
  clerkId: string;
  averageRating?: number;
  totalRatings?: number;
}

export interface SwapRequest {
  id: string;
  fromUserId: string;
  toUserId: string;
  fromUserName: string;
  toUserName: string;
  skillOffered: string;
  skillWanted: string;
  message: string;
  status: 'pending' | 'accepted' | 'rejected' | 'completed' | 'closed';
  closedCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface Feedback {
  id: string;
  swapRequestId: string;
  fromUserId: string;
  toUserId: string;
  rating: number;
  comment?: string;
  createdAt: string;
}

export interface AdminAction {
  id: string;
  type: 'user_banned' | 'user_unbanned' | 'delete_skill' | 'delete_swap';
  targetId: string;
  adminId: string;
  reason: string;
  timestamp: string;
  createdAt: string;
}

export interface Notification {
  id: string;
  type: 'swap_request' | 'platform_message' | 'swap_accepted' | 'swap_rejected';
  title: string;
  message: string;
  userId: string;
  relatedId?: string; // swap request id, etc.
  isRead: boolean;
  createdAt: string;
}

export interface PlatformMessage {
  id: string;
  message: string;
  adminId: string;
  adminName: string;
  createdAt: string;
}

import { ChevronUp, ChevronDown } from 'lucide-react';

export interface VoteButtonsProps {
  voteCount: number;
  userVote: 'up' | 'down' | null;
  onUpvote: () => void;
  onDownvote: () => void;
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

export default function VoteButtons({
  voteCount,
  userVote,
  onUpvote,
  onDownvote,
  size = 'md',
  disabled = false,
}: VoteButtonsProps) {
  const sizeClasses = {
    sm: {
      button: 'w-7 h-7',
      icon: 'w-3 h-3',
      text: 'text-xs',
    },
    md: {
      button: 'w-9 h-9',
      icon: 'w-4 h-4',
      text: 'text-sm',
    },
    lg: {
      button: 'w-11 h-11',
      icon: 'w-5 h-5',
      text: 'text-base',
    },
  };

  const classes = sizeClasses[size];

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={onUpvote}
        disabled={disabled}
        aria-label="Upvote"
        className={`
          ${classes.button}
          flex items-center justify-center
          rounded-lg transition-all duration-200
          ${
            userVote === 'up'
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20'
              : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-purple-400'
          }
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
      >
        <ChevronUp className={classes.icon} />
      </button>

      <span
        className={`
          ${classes.text}
          font-semibold
          ${userVote === 'up' ? 'text-purple-400' : userVote === 'down' ? 'text-red-400' : 'text-gray-300'}
        `}
      >
        {voteCount}
      </span>

      <button
        onClick={onDownvote}
        disabled={disabled}
        aria-label="Downvote"
        className={`
          ${classes.button}
          flex items-center justify-center
          rounded-lg transition-all duration-200
          ${
            userVote === 'down'
              ? 'bg-red-600 text-white shadow-lg shadow-red-500/20'
              : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-red-400'
          }
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
      >
        <ChevronDown className={classes.icon} />
      </button>
    </div>
  );
}


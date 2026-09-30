import { useMutation } from '@tanstack/react-query'
import { fetchCommentary } from '../api/matchups'
import type { CommentaryStyle } from '../types/matchup'

export function useCommentary() {
  return useMutation({
    mutationFn: ({ matchupId, style, forceRefresh }: { matchupId: string; style: CommentaryStyle; forceRefresh?: boolean }) =>
      fetchCommentary(matchupId, style, forceRefresh),
  })
}

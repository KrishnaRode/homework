/* =============================================================================
 *  File:        frontend/lib/types.ts
 *  Description: Shared TypeScript types mirroring the backend schemas.
 *  Developer:   Krishna Rode
 *  Version:     1
 * ============================================================================= */
export type Role = "student" | "admin";

export interface Session {
  token: string;
  role: Role;
  student_id?: string | null;
  name?: string | null;
  klass?: string | null;
  board?: string | null;
}

export interface Board {
  code: string;
  name: string;
  type: string;
  curriculum: string;
}

export interface Topic {
  chapter_id: string;
  chapter_title: string;
  topic_id: string;
  title: string;
  skills: string[];
  difficulty_range: [number, number];
}

export interface Question {
  question_id: string;
  class: string;
  subject: string;
  topic: string;
  difficulty: number;
  type: string;
  question: string;
  options: string[];
  skill_tags: string[];
  estimated_time_seconds: number;
  index: number;
  limit: number;
  // Reading-comprehension sets: a shared passage shown above the question, plus the
  // question's position within the passage's question set.
  passage?: string;
  passage_id?: string;
  set_index?: number;
  set_total?: number;
}

export interface Evaluation {
  correct: boolean;
  score: number;
  what_was_right: string;
  what_was_wrong: string;
  step_by_step: string[];
  how_to_think: string;
  misconception: string | null;
  encouragement: string;
  expected_answer: string;
  next_difficulty: number;
  next_type: string;
}

export interface SessionSummary {
  session_id: string;
  subject: string;
  total_questions: number;
  correct: number;
  accuracy: number;
  avg_score: number;
  strengths: string[];
  weak_areas: string[];
  recommended_next_topics: string[];
  overall_index: number;
}

export interface BrainStats {
  points: number;
  games_played: number;
  current_streak: number;
  best_streak: number;
  by_game: Record<string, { played: number; best: number; wins: number }>;
  last_played: string | null;
}

export interface StudentRow {
  student_id: string;
  name: string;
  class: string;
  board: string;
  username: string;
  created_at: string;
  overall_index: number;
}

create table if not exists sessions (
  session_id uuid primary key,
  start_time timestamptz default now(),
  end_time timestamptz,
  duration_seconds int,
  summary text
);

create table if not exists session_events (
  id bigserial primary key,
  session_id uuid references sessions(session_id),
  role text,
  content text,
  created_at timestamptz default now()
);
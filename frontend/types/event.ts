export interface Event {
  id: number;
  name: string;
  start: string; // ISO datetime
  end: string;
  trainer_id: number;
  color: string; // hex без #
  weekly_event_id?: number | null;
}

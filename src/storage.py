import logging
import sqlite3
import datetime

logger = logging.getLogger(__name__)

class Storage:
    
    def save(self, records, db_path):
        current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

        for record in records:
                record['seen_at'] = current_time
        con = sqlite3.connect(db_path)

        with  con:
            cur = con.cursor()
        
            cur.execute(
                        '''
                            CREATE TABLE IF NOT EXISTS vacancies (
                                id          INTEGER PRIMARY KEY,               -- surrogate key, filled automatically
                                link        TEXT    NOT NULL UNIQUE,           -- natural key, without ?from=list_hot
                                title       TEXT    NOT NULL,
                                post_date   TEXT    NOT NULL,                  -- raw from DOU, e.g. "2 жовтня"; parsed later
                                company     TEXT,
                                salary      TEXT,                              -- raw, e.g. "$2000–3500"
                                location    TEXT,
                                description TEXT,
                                is_hot      INTEGER NOT NULL DEFAULT 0 CHECK (is_hot IN (0, 1)),
                                first_seen  TEXT    NOT NULL,                  -- ISO 8601 run timestamp, set once
                                last_seen   TEXT    NOT NULL,                  -- ISO 8601 run timestamp, updated every run
                                updated_at  TEXT                               -- set when title/company/salary change
                            );                
                        '''
                    )

            sql_insert_update_query = """
                            INSERT INTO vacancies (
                                link, title, post_date, company, salary, location, description,
                                is_hot, first_seen, last_seen
                            )
                            VALUES (
                                :link, :title, :post_date, :company, :salary, :location, :description, :is_hot, :seen_at, :seen_at
                            )
                            ON CONFLICT(link) DO UPDATE SET
                                updated_at  = CASE
                                                WHEN title   IS NOT excluded.title
                                                    OR company IS NOT excluded.company
                                                    OR salary  IS NOT excluded.salary
                                                THEN excluded.last_seen
                                                ELSE updated_at
                                            END,
                                title       = excluded.title,
                                post_date   = excluded.post_date,
                                company     = excluded.company,
                                salary      = excluded.salary,
                                location    = excluded.location,
                                description = excluded.description,
                                is_hot      = excluded.is_hot,
                                last_seen   = excluded.last_seen;
                                -- first_seen deliberately not updated
                        """
            
            cur.executemany(
                sql_insert_update_query,
                records
            )

        con.close()
        logger.info(f"Total written rows: {len(records)} at \"{db_path}\" file.")

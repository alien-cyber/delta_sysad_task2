import sys
import psycopg2

def main(mentee_details, mentor_details):
    conn = psycopg2.connect(
        host="db",
        database="postgres",
        user='postgres',
        password='postgres'
    )
    cur = conn.cursor()
    

   

    cur.execute('''CREATE TABLE IF NOT EXISTS mentors (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(150),
                    rollno BIGINT,
                    domain VARCHAR(50),
                    capacity INTEGER,
                    password VARCHAR(80),
                    assigned VARCHAR(80)
                );''')
     
    cur.execute('''CREATE TABLE IF NOT EXISTS mentee_domain (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(150),
                    rollno BIGINT,
                    domain VARCHAR(150),
                    password VARCHAR(80),
                    mentor_rollno BIGINT
                );''')
    
  
    cur.execute('''CREATE TABLE IF NOT EXISTS urls (
                    id SERIAL PRIMARY KEY,
                    domain VARCHAR(150),
                    rollno BIGINT,
                    url VARCHAR(300)
                );''')
    cur.execute('''DELETE FROM mentors
WHERE username=%s;''',('core',)
)
    cur.execute('''INSERT INTO mentors (username)
            
            VALUES (%s);''',
            ('core',))
   
    with open(mentor_details, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            elements = line.split()
            cur.execute('''INSERT INTO mentors (username, rollno, domain, capacity)
                            VALUES (%s, %s, %s, %s);''',
                        (elements[0], elements[1], elements[2], elements[3]))

    
    with open(mentee_details, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            elements = line.split()
            cur.execute('''INSERT INTO mentee_domain (username, rollno)
                            VALUES (%s, %s);''',
                        (elements[0], elements[1]))

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python init.py <mentee_details> <mentor_details>")
        sys.exit(1)
    mentee_details = sys.argv[1]
    mentor_details = sys.argv[2]
    main(mentee_details, mentor_details)


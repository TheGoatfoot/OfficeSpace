import sqlite3

from passlib.hash import sha256_crypt


class Database:
    # Properties
    database = None

    def __init__(self, database_name):
        self.database = sqlite3.connect(database_name, check_same_thread=False)
        self.default_table()

    def default_table(self):
        self.database.execute('CREATE TABLE IF NOT EXISTS admin ('
                              'id           INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'username     TEXT    NOT NULL UNIQUE, '
                              'password     TEXT    NOT NULL)')
        self.database.execute('CREATE TABLE IF NOT EXISTS client ('
                              'id           INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'name         TEXT    NOT NULL, '
                              'pob          TEXT, '
                              'dob          DATETIME, '
                              'gender       BOOLEAN, '
                              'occupation   TEXT, '
                              'address      TEXT, '
                              'religion     TEXT, '
                              'married      BOOLEAN,'
                              'joined       DATETIME DEFAULT CURRENT_TIMESTAMP, '
                              'admin_id     INTEGER NOT NULL, '
                              'FOREIGN KEY (admin_id) REFERENCES admin(id))')
        self.database.execute('CREATE TABLE IF NOT EXISTS client_rent ('
                              'id               INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'client_id        INTEGER     NOT NULL, '
                              'value            INTEGER     NOT NULL, '
                              'active           BOOLEAN     DEFAULT 0, '
                              'last_active      DATETIME    DEFAULT CURRENT_TIMESTAMP, '
                              'created          DATETIME    DEFAULT CURRENT_TIMESTAMP, '
                              'expires          DATETIME    NOT NULL, '
                              'note             TEXT, '
                              'void             BOOLEAN     DEFAULT 0, '
                              'admin_id         INTEGER NOT NULL, '
                              'void_admin_id    INTEGER, '
                              'FOREIGN KEY (client_id) REFERENCES client(id), '
                              'FOREIGN KEY (admin_id) REFERENCES admin(id), '
                              'FOREIGN KEY (void_admin_id) REFERENCES admin(id))')
        self.database.execute('CREATE TABLE IF NOT EXISTS client_rent_history ('
                              'id               INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'rent_id          INTEGER     NOT NULL, '
                              'start            DATETIME    DEFAULT CURRENT_TIMESTAMP, '
                              'end              DATETIME, '
                              'value            INTEGER, '
                              'start_admin_id   INTEGER ,'
                              'stop_admin_id    INTEGER ,'
                              'FOREIGN KEY (rent_id) REFERENCES client_rent(id), '
                              'FOREIGN KEY (start_admin_id) REFERENCES admin(id), '
                              'FOREIGN KEY (stop_admin_id) REFERENCES admin(id))')
        self.database.execute('PRAGMA foreign_keys = 1')
        self.database.commit()

    # Admin
    def is_admin_empty(self):
        result = self.database.cursor().execute('SELECT * FROM admin').fetchone()
        if result is not None:
            return False
        return True

    def insert_admin(self, username, password):
        self.database.execute('INSERT INTO admin (username, password) VALUES (?, ?)',
                              (username, sha256_crypt.encrypt(password)))
        self.database.commit()

    def get_admin_password(self, username):
        result = self.database.cursor().execute('SELECT password FROM admin WHERE username = ?', (username,)).fetchone()
        if result is not None:
            return result[0]
        return None

    def get_admin_id(self, username):
        result = self.database.cursor().execute('SELECT id FROM admin WHERE username = ?', (username,)).fetchone()
        if result is not None:
            return result[0]
        return None

    # Client
    def get_client(self, name=None):
        if name is None:
            result = self.database.cursor().execute('SELECT * FROM client').fetchall()
        else:
            result = self.database.cursor().execute('SELECT * FROM client WHERE name LIKE ?', (name,)).fetchall()

        if result is not None:
            return result
        return None

    def insert_client(self, data):
        try:
            self.database.execute('INSERT INTO client '
                                  '(name, pob, dob, gender, occupation, address, religion, married, admin_id) VALUES '
                                  '(?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
            self.database.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def edit_client(self, data):
        try:
            self.database.execute('UPDATE client SET '
                                  'name = ?, pob = ?, dob = ?, gender = ?, occupation = ?, address = ?,'
                                  'religion = ?, married = ? '
                                  'WHERE id = ?', data)
            self.database.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    # Rent
    def insert_client_rent(self, data):
        try:
            self.database.execute('INSERT INTO client_rent '
                                  '(client_id, value, expires, note, admin_id) VALUES '
                                  '(?, ?, ?, ?, ?)', data)
            self.database.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def get_rent(self, rent_id):
        result = self.database.cursor().execute(
            'SELECT * FROM client_rent WHERE id=?',
            (rent_id, )).fetchone()
        if result is not None:
            return result
        return None

    def get_rent_alert(self):
        result = self.database.cursor().execute(
            'SELECT id, client_id, '
            'value-(strftime("%s", CURRENT_TIMESTAMP) - strftime("%s", last_active)) as time_left '
            'FROM client_rent '
            'WHERE active=1 AND time_left>=0 AND time_left<3600').fetchall()
        if result is not None:
            return result
        return None

    def get_rent_alert_overdue(self):
        result = self.database.cursor().execute(
            'SELECT id, client_id, '
            'value-(strftime("%s", CURRENT_TIMESTAMP) - strftime("%s", last_active)) as time_left '
            'FROM client_rent '
            'WHERE active=1 AND time_left<0 ').fetchall()
        if result is not None:
            return result
        return None

    def get_rent_summary(self, data):
        result = self.database.cursor().execute(
            'SELECT * FROM client_rent WHERE created>? AND created<?', data).fetchall()
        if result is not None:
            return result
        return None

    def get_client_rent(self, data):
        if data[1] is None:
            result = self.database.cursor().execute(
                'SELECT *, value-(strftime("%s", CURRENT_TIMESTAMP) - strftime("%s", last_active)) FROM client_rent '
                'WHERE client_id=? AND expires > CURRENT_TIMESTAMP AND void=0',
                (data[0], )).fetchall()
        else:
            result = self.database.cursor().execute(
                'SELECT *, value-(strftime("%s", CURRENT_TIMESTAMP) - strftime("%s", last_active)) FROM client_rent '
                'WHERE client_id=? AND note=? AND expires > CURRENT_TIMESTAMP AND void=0',
                data).fetchall()
        if result is not None:
            return result
        return None

    def void_rent(self, rent_id, admin_id):
        try:
            self.database.execute('UPDATE client_rent SET void=1, void_admin_id=? WHERE id=?', (admin_id, rent_id))
            self.database.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def activate_rent(self, rent_id):
        try:
            self.database.execute('UPDATE client_rent '
                                  'SET active=1, last_active=CURRENT_TIMESTAMP WHERE id=?', (rent_id, ))
            self.database.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def deactivate_rent(self, rent_id):
        try:
            self.database.execute('UPDATE client_rent SET active=0 WHERE id=?', (rent_id, ))
            self.database.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def update_rent_value(self, rent_id, value):
        try:
            self.database.execute('UPDATE client_rent SET value=? WHERE id=?', (value, rent_id))
            self.database.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    # Rent History
    def get_history_summary(self, data):
        result = self.database.cursor().execute(
            'SELECT * FROM client_rent_history WHERE start>? AND start<?', data).fetchall()
        if result is not None:
            return result
        return None

    def insert_client_rent_history(self, rent_id, admin_id):
        try:
            self.database.execute('INSERT INTO client_rent_history '
                                  '(rent_id, start_admin_id) VALUES '
                                  '(?, ?)', (rent_id, admin_id))
            self.database.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def stamp_client_rent_history(self, rent_id, admin_id, value):
        try:
            self.database.execute('UPDATE client_rent_history SET end=CURRENT_TIMESTAMP, value=?, stop_admin_id=? '
                                  'WHERE rent_id=? AND end is null', (value, admin_id, rent_id))
            self.database.commit()
        except sqlite3.IntegrityError:
            return False
        return True

    def __del__(self):
        self.database.close()

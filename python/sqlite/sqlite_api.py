import sys
import datetime

# sqlite3 DB support
##
try:
  import sqlite3 as sqlite
except ImportError:
  try:
    import sqlite as sqlite
  except ImportError:
    try:
      from pysqlite2 import dbapi2 as sqlite
    except ImportError:
      raise ImportError, "WARNING: Could not find sqlite database support!"
      
# CLASS FOR SQLITE
##

class sql:
  # Open a database and supply a connection and cursor
  ##
  def __init__(self, database):
    #print sqlite.PARSE_DECLTYPES
    self.con = sqlite.connect(database, detect_types=sqlite.PARSE_DECLTYPES)
    self.db  = self.con.cursor()
    self.id  = None
    self.data = []
    self.count = None

  # Auto close
  ##
  def __del__(self):
    self.con.commit()
    self.con.close()

  # Manual close
  ##
  def close(self):
    self.con.commit()
    self.con.close()

  # Query
  ##
  def query(self, sql):
    db = self.db
    con = self.con
    drv = 'sqlite'

    db.execute(sql)

    if drv == 'sqlite':
      #self.last_count = db.rowcount
      data = []
      for r in [self.sqlite_dict_factory(db, x) for x in db.fetchall()]:
        data.append(r)
      self.data = tuple(data)
      self.count = len(data)
      try:
        self.id   = con.insert_id()
      except:
        self.id   = db.lastrowid

  # Creates a dict of results for SQLite
  ##
  def sqlite_dict_factory(self, cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
    return d



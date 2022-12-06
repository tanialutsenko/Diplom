import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
import sqlalchemy
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Course(Base):
     __tablename__ = "result_3"

     id = sq.Column(sq.Integer, primary_key=True)
     id_user = sq.Column(sq.Integer)
     id_people = sq.Column(sq.Integer)

     def __str__(self):
          return f'{self.id}: {self.name}'

with open("password_base.txt", "r") as file_object:  # access_token
    password = file_object.read().strip()

list_base = password.split(",")

login= list_base[0]
password = list_base[1]
database = list_base[2]


def create_tables(login,password,database):
     DSN = f"postgresql://{login}:{password}@localhost:5432/{database}"
     engine = sqlalchemy.create_engine(DSN)
     Base.metadata.create_all(engine)
     # Base.metadata.drop_all(engine)

def session(user_id,id_people_search,login,password,database):
     DSN = f"postgresql://{login}:{password}@localhost:5432/{database}"
     engine = sqlalchemy.create_engine(DSN)
     Session = sessionmaker(bind=engine)
     session = Session()
     list_all_faind= []
     for id in session.query(Course.id_people).filter(Course.id_user == user_id).all():
          number = id
          number_1 = str(number)
          number_strip = number_1.strip("(,)")
          number_int = int(number_strip)
          list_all_faind.append(number_int)


     for id in id_people_search:
         if id not in list_all_faind:
             course1 = Course(id_people=id, id_user=user_id)
             session.add(course1)
             session.commit()
             session.close()
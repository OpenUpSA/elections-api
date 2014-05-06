from sqlalchemy import Column, Integer, String, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from api import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64))

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % self.username


class VotingDistrict(db.Model):

    __tablename__ = 'voting_districts'

    # columns
    pk = Column(Integer, primary_key=True)
    voting_district_id = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    results_provincial = Column(String)
    results_national = Column(String)
    ward_pk = Column(Integer, ForeignKey('wards.pk'))
    municipality_pk = Column(Integer, ForeignKey('municipalities.pk'))
    province_pk = Column(Integer, ForeignKey('provinces.pk'))

    # associations
    ward = relationship("Ward")
    municipality = relationship("Municipality")
    province = relationship("Province")

    # indexes
    Index('voting_district_year_id_ix', year, voting_district_id, unique=True)

    def __repr__(self):
        return "<VotingDistrict(pk='%s', year='%s', voting_district_id='%s')>" % (
            str(self.pk), str(self.year), str(self.voting_district_id))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Ward(db.Model):

    __tablename__ = 'wards'

    # columns
    pk = Column(Integer, primary_key=True)
    ward_id = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    results_provincial = Column(String)
    results_national = Column(String)
    municipality_pk = Column(Integer, ForeignKey('municipalities.pk'))
    province_pk = Column(Integer, ForeignKey('provinces.pk'))

    # associations
    municipality = relationship("Municipality")
    province = relationship("Province")

    # indexes
    Index('ward_year_id_ix', year, ward_id, unique=True)

    def __repr__(self):
        return "<Ward(pk='%s', year='%s', ward_id='%s')>" % (
            str(self.pk), str(self.year), str(self.ward_id))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Municipality(db.Model):

    __tablename__ = 'municipalities'

    # columns
    pk = Column(Integer, primary_key=True)
    municipality_id = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    results_provincial = Column(String)
    results_national = Column(String)
    province_pk = Column(Integer, ForeignKey('provinces.pk'))

    # associations
    province = relationship("Province")

    # indexes
    Index('municipality_year_id_ix', year, municipality_id, unique=True)

    def __repr__(self):
        return "<Municipality(pk='%s', year='%s', municipality_id='%s')>" % (
            str(self.pk), str(self.year), str(self.municipality_id))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Province(db.Model):

    __tablename__ = 'provinces'

    # columns
    pk = Column(Integer, primary_key=True)
    province_id = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    results_provincial = Column(String)
    results_national = Column(String)

    # indexes
    Index('province_year_id_ix', year, province_id, unique=True)

    def __repr__(self):
        return "<Province(pk='%s', year='%s', province_id='%s')>" % (
            str(self.pk), str(self.year), str(self.province_id))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}



class Country(db.Model):

    __tablename__ = 'country'

    # columns
    pk = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    results_provincial = Column(String)
    results_national = Column(String)

    def __repr__(self):
        return "<Country(pk='%s', year='%s')>" % (
            str(self.pk), str(self.year))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}